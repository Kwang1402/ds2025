import time
import os
import signal
import subprocess

import pytest
from sqlalchemy import create_engine, text, inspect
import redis

import utils

config = utils.get_config()


@pytest.fixture(scope="function")
def clean_environment():
    def clear_redis_log():
        client = redis.Redis(**config["message_bus"]["connection"])
        client.flushdb()

    def reset_master_db():
        engine = create_engine(url=config["database"]["connection"]["url"])
        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            if tables:
                for table in tables:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table};"))
            conn.commit()

            conn.execute(text("RESET MASTER;"))

    def reset_slave_db():
        engine = create_engine(url=config["slave_database"]["connection"]["url"])
        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            if tables:
                for table in tables:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table};"))
            conn.commit()

    clear_redis_log()
    reset_master_db()
    reset_slave_db()

    yield

    clear_redis_log()
    reset_master_db()
    reset_slave_db()


@pytest.fixture(scope="function")
def master_db_session():
    engine = create_engine(url=config["database"]["connection"]["url"])
    conn = engine.connect()

    yield conn

    conn.close()


@pytest.fixture(scope="function")
def slave_db_session():
    engine = create_engine(url=config["slave_database"]["connection"]["url"])
    conn = engine.connect()

    yield conn

    conn.close()


@pytest.fixture(scope="function")
def start_master_and_slave(clean_environment):
    try:
        master_process = subprocess.Popen(
            ["make", "run-master"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("Starting the master process...")
        time.sleep(2)

        slave_process = subprocess.Popen(
            ["make", "run-slave"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("Starting the slave process...")
        time.sleep(2)

        assert master_process.poll() is None, "Master process failed to start."
        assert slave_process.poll() is None, "Slave process failed to start."

        yield

    finally:
        print("Stopping the master and slave processes using pkill...")

        subprocess.run(["pkill", "-f", "slave.py"], check=True)
        subprocess.run(["pkill", "-f", "master.py"], check=True)

        time.sleep(2)
