project_path = $(shell pwd)
config_path = $(project_path)/.configs

run-master:
	PYTHONPATH=$(project_path) CONFIG_PATH=$(config_path) python $(project_path)/master/master.py

run-slave:
	PYTHONPATH=$(project_path) CONFIG_PATH=$(config_path) python $(project_path)/slave/slave.py

test:
	PYTHONPATH=$(project_path) CONFIG_PATH=$(config_path) pytest -v -s