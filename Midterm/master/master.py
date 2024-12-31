import redis
import utils
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import json
import datetime

from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent,
)
from pymysqlreplication.event import QueryEvent

from urllib.parse import urlparse

config = utils.get_config()

connection_url = config["database"]["connection"]["url"]

engine = create_engine(connection_url)


# Database connection details
parsed_url = urlparse(connection_url)

# Create the dictionary
MYSQL_SETTINGS = {
    "host": parsed_url.hostname,
    "port": parsed_url.port,
    "user": parsed_url.username,
    "passwd": parsed_url.password,
}


def convert_datetime_to_str(my_dict):
    for key, value in my_dict.items():
        if isinstance(value, datetime.datetime):
            my_dict[key] = value.strftime("%Y-%m-%d %H:%M:%S")
    return my_dict


def get_data(r):
    stream = BinLogStreamReader(
        connection_settings=MYSQL_SETTINGS,
        server_id=1,  # Unique ID for this binlog reader
        blocking=True,  # Block until a new event is available
        resume_stream=False,  # Resume reading from the last position
        only_events=[WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent, QueryEvent],
    )

    for event in stream:
        operations = {"query": "type_of_query", "table": "table_name", "data": {}}
        if isinstance(event, QueryEvent):
            print(f"Detected CREATE TABLE query: {event.query}")
            operations["query"] = "QUERY"
            operations["data"] = event.query
        else:
            for row in event.rows:
                if isinstance(event, WriteRowsEvent):
                    print(f"Insert: {row['values']}")
                    row["values"] = convert_datetime_to_str(row["values"])
                    operations["query"] = "INSERT"
                    operations["table"] = event.table
                    operations["data"] = row["values"]
                elif isinstance(event, UpdateRowsEvent):
                    print(
                        f"Update: Before: {row['before_values']} After: {row['after_values']}"
                    )
                    row["before_values"] = convert_datetime_to_str(row["before_values"])
                    row["after_values"] = convert_datetime_to_str(row["after_values"])
                    operations["query"] = "UPDATE"
                    operations["table"] = event.table
                    operations["data"] = {
                        "before": row["before_values"],
                        "after": row["after_values"],
                    }
                elif isinstance(event, DeleteRowsEvent):
                    print(f"Delete: {row['values']}")
                    row["values"] = convert_datetime_to_str(row["values"])
                    operations["query"] = "DELETE"
                    operations["table"] = event.table
                    operations["data"] = row["values"]

        sending_binary(r, operations)
    stream.close()


def sending_binary(r, operations):
    r.publish(
        channel=config["message_bus"]["publisher"]["channel"],
        message=json.dumps(operations),
    )
    print("Message published!")


if __name__ == "__main__":
    try:
        r = redis.Redis(**config["message_bus"]["connection"])
        get_data(r)

    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
