import time

from icecream import ic
import pytest
from sqlalchemy import text


@pytest.mark.usefixtures("start_master_and_slave")
class TestDML:
    def test_insert(self, master_db_session, slave_db_session):
        # arrange
        master_db_session.execute(
            text("CREATE TABLE test_table (id INT, name VARCHAR(255));")
        )
        master_db_session.commit()
        time.sleep(2)

        # act
        master_db_session.execute(
            text("INSERT INTO test_table (id, name) VALUES (1, 'Alice');")
        )
        master_db_session.commit()
        time.sleep(2)

        # assert
        master_result = master_db_session.execute(
            text("SELECT * FROM test_table;")
        ).fetchall()
        slave_result = slave_db_session.execute(
            text("SELECT * FROM test_table;")
        ).fetchall()

        ic(master_result)
        ic(slave_result)
        assert (
            master_result == slave_result
        ), "Insert operation not replicated to slave."

    def test_update(self, master_db_session, slave_db_session):
        # arrange
        master_db_session.execute(
            text("CREATE TABLE test_table (id INT, name VARCHAR(255));")
        )
        master_db_session.execute(
            text("INSERT INTO test_table (id, name) VALUES (1, 'Alice');")
        )
        master_db_session.commit()
        time.sleep(2)

        # act
        master_db_session.execute(
            text("UPDATE test_table SET name = 'Bob' WHERE id = 1;")
        )
        master_db_session.commit()
        time.sleep(2)

        # assert
        master_result = master_db_session.execute(
            text("SELECT * FROM test_table;")
        ).fetchall()
        slave_result = slave_db_session.execute(
            text("SELECT * FROM test_table;")
        ).fetchall()

        ic(master_result)
        ic(slave_result)
        assert (
            master_result == slave_result
        ), "Update operation not replicated to slave."

    def test_delete(self, master_db_session, slave_db_session):
        # arrange
        master_db_session.execute(
            text("CREATE TABLE test_table (id INT, name VARCHAR(255));")
        )
        master_db_session.execute(
            text("INSERT INTO test_table (id, name) VALUES (1, 'Alice');")
        )
        master_db_session.commit()
        time.sleep(2)

        # act
        master_db_session.execute(text("DELETE FROM test_table WHERE id = 1;"))
        master_db_session.commit()
        time.sleep(2)

        # assert
        master_result = master_db_session.execute(
            text("SELECT * FROM test_table;")
        ).fetchall()
        slave_result = slave_db_session.execute(
            text("SELECT * FROM test_table;")
        ).fetchall()

        ic(master_result)
        ic(slave_result)
        assert (
            master_result == slave_result
        ), "Delete operation not replicated to slave."
