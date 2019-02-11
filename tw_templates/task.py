# -*- coding: utf-8 -*-

"""Main module."""
import re
import datetime
import uuid
import json
import subprocess
import yaml

from dataclasses import dataclass, field

from typing import NamedTuple, Union, List, Optional

from tw_templates.utils import date_parser

completed_regex = r"Created task (\d)"

post_task = {}
last_id_added = 0

tasks = []


class DateCalc(NamedTuple):
    entity: str
    operator: str
    value: int
    period: str


class EntityCalc(NamedTuple):
    entity: str


def date_calc_matcher(date: str) -> Union[DateCalc, EntityCalc, None]:
    """
    Returns a DateCalc or EntityCalc NamedTuple based
    on a date string entered.
    """
    date_calc_regex = r"^(sched|due|wait)([+-])(\d+)(\w+)"
    entity_regex = r"^(sched|due|wait)$"

    m = re.match(date_calc_regex, date)
    me = re.match(entity_regex, date)
    if m:
        m_tup = list(m.groups())
        i = int(m_tup[2])
        m_tup[2] = i
        return DateCalc(*tuple(m_tup))
    if me:
        return EntityCalc(me.group(0))
    else:
        return None


@dataclass
class _Holder:
    """
    We create one of these before initialising a Task object.
    """
    description: Optional[str]
    tags: Optional[List]
    project: Optional[str]
    due: Optional[Union[str, DateCalc, EntityCalc]]
    wait: Optional[Union[str, DateCalc, EntityCalc]]
    scheduled: Optional[Union[str, DateCalc, EntityCalc]]
    depends: Optional[str]
    annotations: Union[List]
    req_calcs: list = field(default_factory=list)


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
        self.description = description
        self.tags = tags
        self.project = project
        self.due = None
        self.wait = None
        self.scheduled = None
        self.depends = depends
        self.annotations = annotations
        self.status = "pending"
        self.uuid = str(uuid.uuid4())
        self.entry = self._serialise_date()
        self._data_metadata = {"due", "scheduled", "wait"}
        hold = _Holder(
            description,
            tags,
            project,
            due,
            wait,
            scheduled,
            depends,
            annotations,
        )
        if annotations:
            self.annotations = self._add_annotations(annotations)
        if due:
            _d_formula = date_calc_matcher(due)
            if isinstance(_d_formula, (DateCalc, EntityCalc)):
                hold.due = _d_formula
                hold.req_calcs.append("due")
            else:
                hold.due = self._convert_date(due)
        if scheduled:
            _d_formula = date_calc_matcher(scheduled)
            if isinstance(_d_formula, (DateCalc, EntityCalc)):
                hold.scheduled = _d_formula
                hold.req_calcs.append("scheduled")
            else:
                hold.scheduled = self._convert_date(scheduled)
        if wait:
            _d_formula = date_calc_matcher(wait)
            if isinstance(_d_formula, (DateCalc, EntityCalc)):
                hold.wait = _d_formula
                hold.req_calcs.append("wait")
            else:
                hold.wait = self._convert_date(wait)
        # hold off on this until we process _Holder data
        if len(hold.req_calcs) > 0:
            for i in self._data_metadata:
                # anything not in hold.req_calcs gets added to self
                if i not in hold.req_calcs:
                    setattr(self, i, getattr(hold, i))
            calc_data = {item: getattr(hold, item) for item in hold.req_calcs}
            self.process_calcs(calc_data)
        else:
            self.due = hold.due
            self.wait = hold.wait
            self.scheduled = hold.scheduled
            self._dict = self._to_dict()

    def process_calcs(self, calc_data):
        for i in calc_data.items():
            if isinstance(i[1], DateCalc):
                _comp = i[1].entity
                try:
                    _comp_str = getattr(self, _comp)
                except AttributeError:
                    raise
                finally:
                    _comp_date = datetime.date.fromisoformat((_comp_str[:10]))
        print(calc_data)
        pass

    def _convert_date(self, date):
        return date_parser(date)

    def _serialise_date(self):
        return datetime.datetime.now().isoformat()

    def _add_annotations(self, annotations):
        _a = []
        for a in annotations:
            _a.append(dict(entry=self.entry, description=a))
        return _a

    def _to_dict(self):
        return dict(
            description=self.description,
            tags=self.tags,
            project=self.project,
            due=self.due,
            scheduled=self.scheduled,
            wait=self.wait,
            depends=self.depends,
            status=self.status,
            uuid=self.uuid,
            entry=self.entry,
            annotations=self.annotations,
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
        self.description = data.get("description")
        self.tags = data.get("tags")
        self.project = data.get("proj")
        self.due = data.get("due")
        self.depends = data.get("dep")
        self.annotations = data.get("annot")

    def __str__(self):
        return self.desc

    def __repr__(self):
        return "Task({!r})".format(self.description)


def read_file(f: str):
    with open("templates/test_template.yaml", "r") as f:
        data = yaml.safe_load(f)
        return data


def parse_tasks(data: dict):
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
