```markdown
UDb-CSR: lightweight Python tool to parse riscv-unified-db CSR definitions and decode CSR values/diffs
================================================================================

Quick summary
-------------
- Parse riscv-unified-db spec/csrs (YAML/JSON) and build CSR definitions.
- Decode a CSR value into its bitfields.
- Given an XOR mask (before ^ after), list which fields changed (and which bit positions inside them changed).
- CLI with argparse, optional JSON output.

Requirements
------------
- Python 3.8+
- pyyaml (`pip install pyyaml`)

Files
-----
- udblib/parser.py       - UDB parser and data models
- udblib/decoder.py      - Decoder utilities
- scripts/udb_csr_cli.py - CLI entrypoint (uses argparse)

Usage examples
--------------
Clone the riscv-unified-db locally (or point to its spec/csrs dir):
  git clone https://github.com/riscv-software-src/riscv-unified-db

Decode a value:
  python scripts/udb_csr_cli.py decode \
    --spec /path/to/riscv-unified-db/spec/csrs \
    --csr mstatus --value 0x1888

Decode a xor-diff (list fields that changed):
  python scripts/udb_csr_cli.py diff \
    --spec /path/to/riscv-unified-db/spec/csrs \
    --csr mstatus --xor 0x1008

Output JSON:
  python scripts/udb_csr_cli.py decode ... --json

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