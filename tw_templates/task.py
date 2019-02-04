# -*- coding: utf-8 -*-

"""Main module."""
import re
import datetime
import uuid
import json
import subprocess
import yaml

from tw_templates.utils import date_parser

completed_regex = r"Created task (\d)"

post_task = {}
last_id_added = 0

tasks = []


def date_calc_matcher(date: str):
    date_calc_regex = r"(\D+)([-+])(\d+)(\w+)"
    m = re.match(date_calc_regex, date)
    if m:
        base_param = m.group(1)
        operator = m.group(2)
        period = int(m.group(3))
        period_type = m.group(4)
        return base_param, operator, period,  period_type,
    else:
        return None


class Task:
    def __init__(
        self,
        description,
        tags=None,
        project=None,
        due=None,
        wait=None,
        scheduled=None,
        depends=None,
        annotations=None,
    ):
        self.desc = description
        self.tags = tags
        self.proj = project
        self.dep = depends
        self.annot = annotations
        self.status = "pending"
        self.uuid = str(uuid.uuid4())
        self.entry = self._serialise_date()
        if annotations:
            self.annot = self._add_annotations()
        if due:
            _d_formula = date_calc_matcher(due)
            if _d_formula:
                # PERFORM CALC
                pass
            else:
                self.due = self._convert_date(due)
        if scheduled:
            _d_formula = date_calc_matcher(scheduled)
            if _d_formula:
                # PERFORM CALC
                pass
            else:
                self.scheduled = self._convert_date(scheduled)
        if wait:
            _d_formula = date_calc_matcher(wait)
            if _d_formula:
                # PERFORM CALC
                pass
            else:
                self.wait = self._convert_date(wait)
        self._dict = self._to_dict()

    def _convert_date(self, date):
        return date_parser(date)

    def _serialise_date(self):
        return datetime.datetime.now().isoformat()

    def _add_annotations(self):
        _a = []
        for a in self.annot:
            _a.append(dict(entry=self.entry, description=a))
        return _a

    def _to_dict(self):
        return dict(
            description=self.desc,
            tags=self.tags,
            project=self.proj,
            due=self.due,
            scheduled=self.scheduled,
            wait=self.wait,
            depends=self.dep,
            status=self.status,
            uuid=self.uuid,
            entry=self.entry,
            annotations=self.annot
        )

    def _export_json(self):
        return json.dumps(self._to_dict())

    @property
    def json(self):
        return self._export_json()

    def parse(self, data):
        """
        Takes the output of each item in yaml.safe_load().
        """
        self.id = data.get("id")
        self.desc = data.get("description")
        self.tags = data.get("tags")
        self.proj = data.get("proj")
        self.due = data.get("due")
        self.dep = data.get("dep")
        self.annot = data.get("annot")

    def __str__(self):
        return self.desc

    def __repr__(self):
        return "Task({!r})".format(self.desc)


def read_file(f: str):
    with open("templates/test_template.yaml", "r") as f:
        data = yaml.safe_load(f)
        return data


def parse_tasks(data: dict):
    breakpoint()
    for task in data.values():
        tasks.append(Task(**task))
        added = subprocess.run(
            ["task", "add", task["description"], f"due:{task['due']}"],
            stdout=subprocess.PIPE,
        )
        msg = added.stdout.decode("utf-8")
        m = re.match(completed_regex, msg)
        t_id = m.group(1)
        if task.get("depends"):
            post_task["depends"] = task["depends"]

        if post_task.get("project"):
            subprocess.run(["task", t_id, "mod", f"project:{post_task['project']}"])
            post_task.pop("project")

        if post_task.get("annotation"):
            subprocess.run(["task", t_id, "annotate", post_task["annotation"]])
            post_task.pop("annotation")

        if post_task.get("depends"):
            breakpoint()
            dep_id = int(t_id) - int(dep_indicator)
            if dep_id <= 0:
                print("Check your dependency id. Doesn't make sense")
                continue
            subprocess.run(["task", t_id, "mod", f"dep:{dep_id}"])
            post_task.pop("depends")

        last_id_added = t_id


def main():
    data = read_file("templates/test_template.yaml")
    parse_tasks(data)


if __name__ == "__main__":
    main()
