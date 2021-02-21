#! /usr/bin/env python

import os
import json
import signal
import subprocess
import time

import click


def set_env_vars(conf_file='development.json'):
    with open(os.path.join("config", conf_file)) as f:
        config = json.load(f)

    for var in config:
        os.environ[var['name']] = os.getenv(var['name'], var['value'])


@click.group()
def cli():
    pass


@cli.command()
def run():
    cmdline = ["flask", "run", "--host=0.0.0.0"]

    try:
        p = subprocess.Popen(cmdline)
        p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()


@cli.command()
@click.option("--testing", default=False)
def build(testing):
    set_env_vars('testing.json' if testing else 'development.json')

    files = ["-f", "docker-compose-testing.yaml"] if testing else []
    cmdline = ["docker-compose"] + files + ["build"]

    try:
        p = subprocess.Popen(cmdline)
        p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()


@cli.command()
def run_container():
    set_env_vars()
    cmdline = ["docker-compose", "up", "-d"]

    try:
        p = subprocess.Popen(cmdline)
        p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()


@cli.command()
@click.option("-m", "--message", default="")
def create_migration(message):
    set_env_vars()

    subcommand = ["-m", message] if message else []
    cmdline = ["flask", "db", "migrate"] + subcommand

    try:
        p = subprocess.Popen(cmdline)
        p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()


@cli.command()
def migrate():
    set_env_vars()
    cmdline = ["flask", "db", "upgrade"]

    try:
        p = subprocess.Popen(cmdline)
        p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()


def dc_test_cmd():
    return ["docker-compose", "-f", "docker-compose-testing.yaml"]


@cli.command()
def test():
    set_env_vars("testing.json")

    subprocess.call(dc_test_cmd() + ["up", "-d"])

    logs = subprocess.check_output(dc_test_cmd() + ["logs", "db"])
    while "ready to accept connections" not in logs.decode("utf-8"):
        time.sleep(0.1)
        logs = subprocess.check_output(dc_test_cmd() + ["logs", "db"])

    subprocess.call(["pytest", "-svv", "--cov=application", "--cov-report=term-missing"])

    subprocess.call(dc_test_cmd() + ["up", "-d"])


if __name__ == "__main__":
    set_env_vars()
    cli()
