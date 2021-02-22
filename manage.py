#! /usr/bin/env python

import os
import json
import signal
import subprocess
import time

import click
import psycopg2
from psycopg2 import errors
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


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
    set_env_vars()
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

    create_db()
    subprocess.call(["pytest", "-svv", "--cov=application", "--cov-report=term-missing"])

    subprocess.call(dc_test_cmd() + ["down"])


def run_sql(statements):
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOSTNAME"),
        port=os.getenv("POSTGRES_PORT"),
    )

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    for statement in statements:
        cursor.execute(statement)

    cursor.close()
    conn.close()


def create_db():

    try:
        print(f"Try to create Db '{os.getenv('APPLICATION_DB')}'")
        run_sql([f"CREATE DATABASE {os.getenv('APPLICATION_DB')}"])
        print(f"Db '{os.getenv('APPLICATION_DB')}' was created successfully")
    except errors.DuplicateDatabase:
        print(
            f"The database {os.getenv('APPLICATION_DB')} already exists and will not be recreated"
        )


if __name__ == "__main__":
    cli()
