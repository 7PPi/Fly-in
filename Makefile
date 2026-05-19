PIP = ./fly_env/bin/pip install
PY = fly_env/bin/python
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict build

# Terminal colors
C_RESET = \033[0m
C_BLUE = \033[1;34m
C_GREEN = \033[1;32m
C_YELLOW = \033[1;33m
C_RED = \033[1;31m

define msg_info
	@printf "$(C_BLUE)[INFO]$(C_RESET) %s\n" "$(1)"
endef

define msg_ok
	@printf "$(C_GREEN)[OK]$(C_RESET) %s\n" "$(1)"
endef

define msg_warn
	@printf "$(C_YELLOW)[WARN]$(C_RESET) %s\n" "$(1)"
endef

define msg_error
	@printf "$(C_RED)[ERROR]$(C_RESET) %s\n" "$(1)"
endef

define msg_step
	@printf "$(C_BLUE)>>$(C_RESET) %s\n" "$(1)"
endef

install:
	$(call msg_info,Preparing virtual environment and installing tooling...)
	@python3 -m venv fly_env

	@$(PIP) flake8
	@$(PIP) mypy
	@$(PIP) colorama
	@$(PIP) types-colorama
	$(call msg_ok,Environment is ready.)

# Run your project
run:
ifndef MAP
	$(call msg_error, Please provide a file like: make run MAP=map.txt)
else
	$(call msg_step,Running maze application...)
	@python3 fly-in.py $(MAP)
endif

env_on:
	$(call msg_step, Activating virtual environment...)
	@source fly_env/bin/activate

# Debug mode
debug:
	$(call msg_warn,Starting debugger for maze application...)
	@python3 -m pdb fly-in.py

# Clean cache files
clean:
	$(call msg_warn,Removing temporary and cache files...)
	@rm -rf .mypy_cache fly_env
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	$(call msg_ok,Cleanup completed.)

# Linting (mandatory)
lint:
	$(call msg_step,Running flake8 checks...)
	@python3 -m flake8 fly-in.py src/
	$(call msg_step,Running mypy checks...)
	@$(PY) -m mypy fly-in.py src/ $(MYPY_FLAGS)
	$(call msg_ok,Lint checks passed.)

# Strict lint (optional)
lint-strict:
	$(call msg_step,Running strict lint checks...)
	@python3 -m flake8 fly-in.py src/
	@$(PY) -m mypy fly-in.py src/ --strict
	$(call msg_ok,Strict lint checks passed.)


