#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `tw_templates` package."""
import json

import pytest

from click.testing import CliRunner

from tw_templates.task import Task
from tw_templates.utils import date_parser as parse
from tw_templates import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert "tw_templates.cli.main" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output


def test_task_obj():
    """
    Test the Task object.
    """
    t_dict = {
        "description": "Test Task",
        "annotations": ["First annotation", "Second annotation"],
        "tags": ['tag0', 'tag1', 'tag2'],
        "due": "23 March",
        "scheduled": "2019-08-30",
        "wait": "24th July 2024",
    }
    t = Task(**t_dict)
    assert json.loads(t.json)["description"] == "Test Task"
    assert json.loads(t.json)["annotations"][0]["description"] == "First annotation"
    assert json.loads(t.json)["annotations"][1]["description"] == "Second annotation"
    assert json.loads(t.json)["tags"][0] == "tag0"
    assert json.loads(t.json)["tags"][1] == "tag1"
    assert json.loads(t.json)["tags"][2] == "tag2"
    assert json.loads(t.json)["due"] == "2019-03-23T00:00:00Z"
    assert json.loads(t.json)["scheduled"] == "2019-08-30T00:00:00Z"
    assert json.loads(t.json)["wait"] == "2024-07-24T00:00:00Z"


def test_date_parser():
    """
    Test date parsing used to build a Task() object.
    """
    assert parse("28 Dec 2019 12am") == "2019-12-28T00:00:00Z"
    assert parse("12 Dec") == "2019-12-12T00:00:00Z"
