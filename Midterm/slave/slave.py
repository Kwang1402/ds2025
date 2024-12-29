import redis
import utils
import json
from sqlalchemy import create_engine, Table, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

config = utils.get_config()


def get_mysql_connection():
    engine = create_engine(url=config["slave_database"]["connection"]["url"])
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


# Execute DDL queries: (e.g., CREATE, ALTER, DROP)
def execute_ddl_query(query, session):
    try:
        session.execute(text(query))
        session.commit()
        print(f"Executed DDL query: {query}")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error executing DDL query: {e}")


def insert(table, data, session):
    try:
        columns = ", ".join(data.keys())
        placeholders = ", ".join([f":{key}" for key in data.keys()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        session.execute(text(query), data)
        session.commit()
        print(f"Inserted data into {table}: {data}")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting data into {table}: {e}")


def update(table, data, session):
    try:
        set_clause = ", ".join([f"{key} = :{key}" for key in data["after"].keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE id = :id"
        params = {**data["after"], "id": data["before"]["id"]}
        session.execute(text(query), params)
        session.commit()
        print(f"Updated data in {table}: {params}")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error updating data in {table}: {e}")


def delete(table, data, session):
    try:
        query = f"DELETE FROM {table} WHERE id = :id"
        session.execute(text(query), {"id": data["id"]})
        session.commit()
        print(f"Deleted data from {table} where id = {data['id']}")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error deleting data from {table}: {e}")


def handle_message(message, session):
    query_handlers = {
        "QUERY": execute_ddl_query,
        "INSERT": insert,
        "UPDATE": update,
        "DELETE": delete,
    }

    message_data = json.loads(message["data"])
    query = message_data.get("query").upper()
    table = message_data.get("table")
    data = message_data.get("data")

    if query in query_handlers:
        if query == "QUERY":
            query_handlers[query](data, session)
        else:
            query_handlers[query](table, data, session)
    else:
        print(f"Unknown query type: {query}")


if __name__ == "__main__":
    r = redis.Redis(**config["message_bus"]["connection"])
    pubsub = r.pubsub()
    pubsub.subscribe(config["message_bus"]["subscriber"]["channel"])

    session = get_mysql_connection()

    for message in pubsub.listen():
        if message["type"] == "message":
            handle_message(message, session)
