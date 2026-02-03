# udblib/parser.py
# UDB parser: load CSR definitions from riscv-unified-db spec/csrs YAML/JSON files
from __future__ import annotations
import os
import glob
import json
import yaml
import re
from typing import List, Dict, Optional, Any, Tuple

class CSRField:
    def __init__(self, name: str, msb: int, lsb: int, desc: str = "", field_type: str = "", reset_value: Any = None, alias: str = ""):
        self.name = name
        self.msb = msb
        self.lsb = lsb
        self.desc = desc.strip().replace('\n',' ')
        self.field_type = field_type
        self.reset_value = reset_value
        self.alias = alias

    @property
    def width(self) -> int:
        return self.msb - self.lsb + 1

    def mask(self) -> int:
        return ((1 << self.width) - 1) << self.lsb

    def contains_any(self, mask: int) -> bool:
        return (self.mask() & mask) != 0

    def changed_bits(self, xor_mask: int) -> int:
        return self.mask() & xor_mask

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "msb": self.msb,
            "lsb": self.lsb,
            "width": self.width,
            "desc": self.desc,
            "type": self.field_type,
            "reset_value": self.reset_value,
            "alias": self.alias,
            "mask": hex(self.mask())
        }

class CSRDefinition:
    def __init__(self, name: str, raw: Dict[str, Any]):
        self.name = name
        self.raw = raw
        self.fields: List[CSRField] = []
        self.long_name = raw.get("long_name", "")
        self.length = raw.get("length", 64)
        self.description = raw.get("description", "")
        self.writable = raw.get("writable", False)
        self.priv_mode = raw.get("priv_mode", "")
        self.definedBy = raw.get("definedBy", {})
        # populate fields via load_all

    def add_field(self, field: CSRField):
        self.fields.append(field)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "long_name": self.long_name,
            "length": self.length,
            "description": self.description,
            "writable": self.writable,
            "priv_mode": self.priv_mode,
            "definedBy": self.definedBy,
            "fields": [f.to_dict() for f in self.fields],
            "raw": self.raw
        }

# Utility: parse various forms of bit-range representations
def parse_range_spec(bits_spec) -> Tuple[int,int]:
    """
    Accepts schema-supported styles for location:
    - int -> single bit (n)
    - "31..12", "31:12", "31-12", "33-32"
    - dict like {"msb": 31, "lsb": 12} or {"hi":31,"lo":12} or {"from":12,"to":31}
    - list/tuple [31,12]
    Returns (msb, lsb) with msb >= lsb
    """
    if bits_spec is None:
        raise ValueError("bits_spec is None")
    # direct ints
    if isinstance(bits_spec, int):
        return bits_spec, bits_spec
    if isinstance(bits_spec, (list, tuple)) and len(bits_spec) >= 2:
        a, b = int(bits_spec[0]), int(bits_spec[1])
        return (a, b) if a >= b else (b, a)
    if isinstance(bits_spec, dict):
        msb = None
        lsb = None
        for k in ("msb","hi","from","to","high"):
            if k in bits_spec:
                msb = int(bits_spec[k])
                break
        for k in ("lsb","lo","to","low"):
            if k in bits_spec:
                lsb = int(bits_spec[k])
                break
        if msb is not None and lsb is not None:
            return (msb, lsb) if msb >= lsb else (lsb, msb)
        raise ValueError(f"Unrecognized dict bits_spec: {bits_spec}")
    # string forms: "31..12", "31:12", "31-12", "33-32"
    s = str(bits_spec).strip()
    m = re.match(r'^(\d+)\s*(?:\.\.|\:|\-)\s*(\d+)$', s)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return (a,b) if a >= b else (b,a)
    # single number "7"
    m2 = re.match(r'^(\d+)$', s)
    if m2:
        b = int(m2.group(1))
        return (b,b)
    raise ValueError(f"Unrecognized bits spec string: '{s}'")

class UDBParser:
    """
    Loads CSR definitions from a directory (riscv-unified-db/spec/csrs).
    It is tolerant to multiple YAML/JSON schema variants.
    """
    def __init__(self, csrs_dir: str):
        self.csrs_dir = csrs_dir
        self._by_name: Dict[str, CSRDefinition] = {}

    def load_all(self) -> Dict[str, CSRDefinition]:
        patterns = [
            os.path.join(self.csrs_dir, "*.yml"),
            os.path.join(self.csrs_dir, "*.yaml"),
            os.path.join(self.csrs_dir, "*.json"),
        ]
        files = []
        for p in patterns:
            files.extend(glob.glob(p))
        for fn in sorted(files):
            try:
                with open(fn, "r", encoding="utf-8") as f:
                    if fn.endswith(".json"):
                        data = json.load(f)
                    else:
                        data = yaml.safe_load(f)
            except Exception:
                continue
            if not data or not isinstance(data, dict):
                continue
            # Assume each file is a single CSR object per schema
            if data.get("kind") != "csr" or "name" not in data:
                continue
            name = str(data["name"])
            csr_def = CSRDefinition(name, data)
            # Parse fields: fields is an object with field names as keys
            fields_obj = data.get("fields", {})
            if isinstance(fields_obj, dict):
                for field_name, field_data in fields_obj.items():
                    if not isinstance(field_data, dict):
                        continue
                    try:
                        # Determine location: prefer location, then location_rv32/rv64 (assume 64-bit for now)
                        loc = field_data.get("location")
                        if loc is None:
                            loc = field_data.get("location_rv64") or field_data.get("location_rv32")
                        if loc is None:
                            continue
                        msb, lsb = parse_range_spec(loc)
                        desc = field_data.get("description", "")
                        field_type = field_data.get("type", "")
                        reset_value = field_data.get("reset_value", None)
                        alias = field_data.get("alias", "")
                        csr_def.add_field(CSRField(field_name, msb, lsb, desc, field_type, reset_value, alias))
                    except Exception:
                        continue
            self._by_name[name] = csr_def
        print(f"Loaded {len(self._by_name)} CSR definitions from {len(files)} files.")
        # print(f"CSR names: {', '.join(sorted(self._by_name.keys()))}")
        # print(f"CSR field names: {', '.join(sorted({f.name for d in self._by_name.values() for f in d.fields}))}")
        return self._by_name

    def get(self, name: str) -> Optional[CSRDefinition]:
        # case-insensitive lookup by simple name
        if name in self._by_name:
            return self._by_name[name]
        low = name.lower()
        for k,v in self._by_name.items():
            if k.lower() == low:
                return v
        return None