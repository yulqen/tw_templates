# -*- coding: utf-8 -*-

"""Main module."""
import re
import subprocess
import yaml

completed_regex = r"Created task (\d)"

post_task = {}
last_id_added = 0

tasks = []


class Task:
    def __init__(self, id, description, tags, project, due, depends, annotation):
        self.id = id
        self.desc = description
        self.tags = tags
        self.proj = project
        self.due = due
        self.dep = depends
        self.annot = annotation

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
        return self.desc


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
