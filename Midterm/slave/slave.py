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
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error executing DDL query: {e}")


def insert(table, data, session):
    try:
        table_class = Table(table, session.metadata, autoload_with=session.bind)
        session.execute(table_class.insert().values(data))
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting data into {table}: {e}")


def update(table, data, session):
    try:
        table_class = Table(table, session.metadata, autoload_with=session.bind)
        session.execute(
            table_class.update()
            .where(table_class.c.id == data["before"]["id"])
            .values(data["after"])
        )
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error updating data in {table}: {e}")


def delete(table, data, session):
    try:
        table_class = Table(table, session.metadata, autoload_with=session.bind)
        session.execute(table_class.delete().where(table_class.c.id == data["id"]))
        session.commit()
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
    query = message_data.get("query")
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
    r = redis.Redis(**config["message_broker"]["connection"])
    pubsub = r.pubsub()
    pubsub.subscribe(config["message_broker"]["subscriber"]["channel"])

    session = get_mysql_connection()

    for message in pubsub.listen():
        if message["type"] == "message":
            handle_message(message, session)
