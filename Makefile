VERSION := "v1.1.1"

PYTHON3 ?= python3
TY ?= ty
RUFF ?= ruff

.PHONY: check
check:
	$(RUFF) check
	$(RUFF) format --diff
	$(TY) check

.PHONY: verify
verify:
	udevadm verify 41-nitrokey.rules

.PHONY: fix
fix:
	$(RUFF) check --fix
	$(RUFF) format

.PHONY: generate
generate:
	$(PYTHON3) generate.py $(VERSION) devices.toml 41-nitrokey.rules
