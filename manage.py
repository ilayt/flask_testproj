#! /usr/bin/env python

import os
import json
import signal
import subprocess

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
def run_container():
    set_env_vars()
    cmdline = ["docker-compose", "up", "-d"]

    try:
        p = subprocess.Popen(cmdline)
        p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()


if __name__ == "__main__":
    set_env_vars()
    cli()
