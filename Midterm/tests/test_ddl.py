import time

from icecream import ic
import pytest
from sqlalchemy import text


@pytest.mark.usefixtures("start_master_and_slave")
class TestDDL:
    def test_create_table(self, master_db_session, slave_db_session):
        # arrange
        # act
        master_db_session.execute(
            text("CREATE TABLE test_table (id INT, name VARCHAR(255));")
        )
        master_db_session.commit()
        time.sleep(2)

        master_schema = get_table_schema(master_db_session, "test_table")
        slave_schema = get_table_schema(slave_db_session, "test_table")

        # assert
        ic(master_schema)
        ic(slave_schema)
        assert (
            master_schema == slave_schema
        ), f"Schemas do not match! Master schema: {master_schema}, Slave schema: {slave_schema}"

    def test_drop_table(self, master_db_session, slave_db_session):
        # arrange
        master_db_session.execute(
            text("CREATE TABLE test_table (id INT, name VARCHAR(255));")
        )
        master_db_session.commit()
        time.sleep(2)

        # act
        master_db_session.execute(text("DROP TABLE test_table;"))
        master_db_session.commit()
        time.sleep(2)

        # assert
        master_result_after_drop = master_db_session.execute(
            text("SHOW TABLES LIKE 'test_table';")
        ).fetchone()

        slave_result_after_drop = slave_db_session.execute(
            text("SHOW TABLES LIKE 'test_table';")
        ).fetchone()

        assert (
            master_result_after_drop is None
        ), "Table 'test_table' still exists in master DB after drop."
        assert (
            slave_result_after_drop is None
        ), "Table 'test_table' still exists in slave DB after drop."


def get_table_schema(session, table_name):
    result = session.execute(text(f"DESCRIBE {table_name};")).fetchall()
    schema = {row[0]: row[1] for row in result}
    return schema
