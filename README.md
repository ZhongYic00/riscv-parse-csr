```markdown
UDb-CSR: lightweight Python tool to parse riscv-unified-db CSR definitions and decode CSR values/diffs
================================================================================

Quick summary
-------------
- Parse riscv-unified-db spec/csrs (YAML/JSON) and build CSR definitions.
- Enrich CSR definitions with riscv-config type information (WARL/WLRL/WPRI/etc).
- Decode a CSR value into its bitfields.
- Given an XOR mask (before ^ after), list which fields changed (and which bit positions inside them changed).
- CLI with argparse, optional JSON output.

Requirements
------------
- Python 3.8+
- pyyaml (`pip install pyyaml`)

Files
-----
- udblib/parser.py       - UDB parser and data models, riscv-config integration
- udblib/decoder.py      - Decoder utilities
- scripts/udb_csr_cli.py - CLI entrypoint (uses argparse)

Submodules
----------
- riscv-unified-db       - RISC-V Unified Database for CSR definitions
- riscv-config           - RISC-V Config for CSR type information (WARL/WLRL/etc)

Usage examples
--------------
Clone and initialize submodules:
  git clone --recurse-submodules https://github.com/ZhongYic00/riscv-parse-csr
  # or if already cloned:
  git submodule update --init riscv-unified-db riscv-config

Decode a value:
  python scripts/udb_csr_cli.py decode \
    --spec riscv-unified-db/spec/std/isa/csr \
    --csr mstatus --value 0x1888

Decode with CSR type information (WARL/WLRL/etc):
  python scripts/udb_csr_cli.py decode \
    --spec riscv-unified-db/spec/std/isa/csr \
    --config riscv-config/examples/rv64i_isa_checked.yaml \
    --csr mstatus --value 0x1888

Decode a xor-diff (list fields that changed):
  python scripts/udb_csr_cli.py diff \
    --spec riscv-unified-db/spec/std/isa/csr \
    --csr mstatus --xor 0x1008

Output JSON:
  python scripts/udb_csr_cli.py decode ... --json

CSR Type Information
--------------------
When using --config with riscv-config YAML file, the tool extracts and displays:
- WARL (Write-Any Read-Legal): Fields where any value can be written, but only legal values are read
- WLRL (Write-Legal Read-Legal): Fields where only legal values can be written
- WPRI (Write-Preserve Read-Ignore): Reserved fields
- WIRI (Write-Ignore Read-Ignore): Ignored fields
- ro_constant: Read-only constant value fields
- ro_variable: Read-only variable value fields

WARL legal values are extracted and stored but not printed by default.

Extension points
----------------
- Parser currently scans `*.yml`/`*.yaml`/`*.json` under spec/csrs. If the repository layout differs, pass another directory.
- Field parsing is robust to common UDB variants; add more keys or custom normalization in `udblib/parser.py`.
- Decoder returns structured Python dicts; you can import udblib.decoder.Decoder in other tools.

Next steps I can do for you
--------------------------
- Run/adapt the parser against a real checkout of riscv-unified-db and fix any schema corner cases (I can fetch and test if you allow).
- Add unit tests and CI config.
- Package as pip module and add entrypoint console script.
```