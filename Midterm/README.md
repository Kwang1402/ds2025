# MySQL Replication clone

# Getting started

## Installation

-   Clone the repository
    
-   Set up configuration

    Edit MySQL Configuration File

    ```bash
    sudo nano /etc/mysql/my.cnf
    ```

    Enable Logging

    ```bash
    [mysqld]
    log_bin=mysql-bin
    server_id=1
    binlog_format=ROW
    ```

    Limit Logs to a Specific Database
    
    Add the following configuration to to limit logs a specific database (for example `master`)

    ```bash
    binlog-do-db=master
    ```

    Add Options to Log Column Names

    ```bash
    binlog_row_image=FULL
    binlog_row_metadata=FULL
    ```
    
## Development requirements

-   Navigate to the `Midterm` directory

    ```bash
    cd Midterm
    ```

This repository uses `poetry` (as shown by the poetry.lock file).


-   Install `poetry` if you haven't already:

    ```
    pip install poetry
    ```

-   Installing dependencies:

    ```
    poetry install
    ```

-   Or if you use a conda env:
    ```
    conda install -c conda-forge poetry
    poetry install
    ```

-   Config your connections in `.configs`:

    Master database configs: `database.yaml`

    Slave database configs: `slave_database.yaml`

    Message bus configs: `message_bus.yaml`
    
# Running the Master

-   To run the `master`, use the make command:

    ```bash
    make run-master
    ```

# Running the Slave

-   To run the `slave`, use the make command:

    ```bash
    make run-slave
    ```

# Running the Tests

-   To run the tests, use the make command:

    ```bash
    make test
    ```