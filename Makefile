PYTHON3 ?= python3
PYRIGHT ?= pyright
RUFF ?= ruff

.PHONY: check
check:
	$(RUFF) check
	$(RUFF) format --diff
	$(PYRIGHT)

.PHONY: fix
fix:
	$(RUFF) check --fix
	$(PYRIGHT) format

.PHONY: generate
generate:
	$(PYTHON3) generate.py devices.toml 41-nitrokey.rules
