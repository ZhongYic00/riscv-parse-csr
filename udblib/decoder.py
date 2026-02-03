# udblib/decoder.py
# Decoder: decode values or xor-diffs given CSRDefinition instances from parser
from __future__ import annotations
from typing import List, Dict, Any
from .parser import CSRDefinition, CSRField

class Decoder:
    def __init__(self, xlen: int = 64):
        self.xlen = xlen

    def decode_value(self, csr: CSRDefinition, value: int) -> List[Dict[str, Any]]:
        """
        Decode full value into fields.
        Returns list of dicts with keys: name, msb, lsb, width, raw_value, hex, bin, desc
        """
        out = []
        for f in sorted(csr.fields, key=lambda ff: ff.msb, reverse=True):
            raw = (value & f.mask()) >> f.lsb
            out.append({
                "name": f.name,
                "msb": f.msb,
                "lsb": f.lsb,
                "width": f.width,
                "value": int(raw),
                "hex": hex(int(raw)),
                "bin": bin(int(raw)),
                "desc": f.desc
            })
        return out

    def decode_xor_mask(self, csr: CSRDefinition, xor_mask: int) -> List[Dict[str, Any]]:
        """
        Given xor_mask (before ^ after), return fields that have any changed bits.
        For each changed field, include changed_bitmask (bits inside field that changed).
        """
        out = []
        for f in sorted(csr.fields, key=lambda ff: ff.msb, reverse=True):
            changed = f.changed_bits(xor_mask)
            if changed:
                # bits relative to lsb
                rel = (changed >> f.lsb)
                out.append({
                    "name": f.name,
                    "msb": f.msb,
                    "lsb": f.lsb,
                    "width": f.width,
                    "changed_mask": hex(changed),
                    "changed_rel": hex(rel),
                    "changed_bits_count": changed.bit_count(),
                    "desc": f.desc
                })
        return out