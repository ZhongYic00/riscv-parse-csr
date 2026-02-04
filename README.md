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
  python scripts_udb_csr_cli.py decode \
    --spec riscv-unified-db/spec/std/isa/csr \
    --csr mstatus --value 0x1888

Decode with CSR type information (WARL/WLRL/etc):
  python scripts_udb_csr_cli.py decode \
    --spec riscv-unified-db/spec/std/isa/csr \
    --config riscv-config/examples/rv64i_isa_checked.yaml \
    --csr mstatus --value 0xa00006000

  Output:
  Enriched 41 CSR definitions with riscv-config type information.
  Loaded 80 CSR definitions from 80 files.
  CSR: mstatus
  SD[63]=0b0 (wlrl), MDT[42]=0b0, MPV[39]=0b0, GVA[38]=0b0, MBE[37]=0b0, 
  SBE[36]=0b0, SXL[35:34]=0b10 (ro_constant), UXL[33:32]=0b10 (ro_constant), 
  TSR[22]=0b0 (warl), TW[21]=0b0 (ro_constant), TVM[20]=0b0 (warl), 
  MXR[19]=0b0 (warl), SUM[18]=0b0 (warl), MPRV[17]=0b0 (warl), XS[16:15]=0b0, 
  FS[14:13]=0b11 (warl), MPP[12:11]=0b0 (ro_constant), VS[10:9]=0b0, 
  SPP[8]=0b0 (ro_constant), MPIE[7]=0b0 (wlrl), UBE[6]=0b0, 
  SPIE[5]=0b0 (wlrl), MIE[3]=0b0 (wlrl), SIE[1]=0b0 (wlrl),

Decode a xor-diff (list fields that changed):
  python scripts_udb_csr_cli.py diff \
    --spec riscv-unified-db/spec/std/isa/csr \
    --config riscv-config/examples/rv64i_isa_checked.yaml \
    --csr mstatus --xor 0x8000000000004000

  Output:
  Enriched 41 CSR definitions with riscv-config type information.
  Loaded 80 CSR definitions from 80 files.
  CSR: mstatus (fields with changes)
   SD      [63:63] changed_mask=0x8000000000000000 rel=0x1 bits_changed=1 (wlrl)
   FS      [14:13] changed_mask=0x4000 rel=0x2 bits_changed=1 (warl)

Compare two CSR values:
  python scripts_udb_csr_cli.py compare \
    --spec riscv-unified-db/spec/std/isa/csr \
    --config riscv-config/examples/rv64i_isa_checked.yaml \
    --csr mstatus --value1 0x0000000a00002000 --value2 0x8000000a00006000

  Output:
  Enriched 41 CSR definitions with riscv-config type information.
  Loaded 80 CSR definitions from 80 files.
  CSR: mstatus (field differences)
   SD    [63:63] = 0x0 / 0 / 0b0 vs 0x1 / 1 / 0b1 (wlrl)
   FS    [14:13] = 0x1 / 1 / 0b1 vs 0x3 / 3 / 0b11 (warl)

Output JSON:
  python scripts_udb_csr_cli.py decode ... --json

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