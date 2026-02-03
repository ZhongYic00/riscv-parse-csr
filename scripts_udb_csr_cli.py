#!/usr/bin/env python3
# CLI entrypoint: argparse with subcommands decode / diff
import argparse
import sys
import json
from udblib.parser import UDBParser
from udblib.decoder import Decoder

def parse_int(s: str) -> int:
    s = s.strip()
    if s.startswith("0x") or s.startswith("0X"):
        return int(s, 16)
    if s.startswith("0b") or s.startswith("0B"):
        return int(s, 2)
    return int(s, 0)

def pretty_print_decode(name, decoded, compact=True):
    print(f"CSR: {name}")
    if compact:
        for f in decoded:
            bits = f"[{f['msb']}:{f['lsb']}]" if f['msb'] != f['lsb'] else f"[{f['msb']}]"
            print(f"{f['name']}{bits}={f['bin']}", end=', ')
    else:
        for f in decoded:
            print(f" {f['name']:20} [{f['msb']:2d}:{f['lsb']:2d}] = {f['hex']:>6} / {f['value']:>3} / {f['bin']:>10}")
            #  {f.get('desc','')}
    print()

def pretty_print_diff(name, diffs):
    print(f"CSR: {name} (fields with changes)")
    for d in diffs:
        print(f" {d['name']:20} [{d['msb']:2d}:{d['lsb']:2d}] changed_mask={d['changed_mask']:>10} rel={d['changed_rel']:>6} bits_changed={d['changed_bits_count']:>2}  {d.get('desc','')}")
    print()

def pretty_print_compare(name, decoded1, decoded2, compact=False):
    print(f"CSR: {name} (field differences)")
    if compact:
        for f1, f2 in zip(decoded1, decoded2):
            if f1['value'] != f2['value']:
                bits = f"[{f1['msb']}:{f1['lsb']}]" if f1['msb'] != f1['lsb'] else f"[{f1['msb']}]"
                print(f"{f1['name']}{bits}={f1['bin']} vs {f2['bin']}", end=', ')
    else:
        for f1, f2 in zip(decoded1, decoded2):
            if f1['value'] != f2['value']:
                print(f" {f1['name']:20} [{f1['msb']:2d}:{f1['lsb']:2d}] = {f1['hex']:>6} / {f1['value']:>3} / {f1['bin']:>10} vs {f2['hex']:>6} / {f2['value']:>3} / {f2['bin']:>10} \"{f1['desc']}\"")
    print()

def main(argv=None):
    p = argparse.ArgumentParser(prog="udb-csr", description="Decode RISC-V CSR values using riscv-unified-db")
    sub = p.add_subparsers(dest="cmd", required=True)

    # common args
    def add_common(parser):
        parser.add_argument("--spec", required=True, help="Path to riscv-unified-db spec/csrs directory")
        parser.add_argument("--xlen", type=int, default=64, help="XLEN (default 64)")
        parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    dec = sub.add_parser("decode", help="Decode CSR value into bitfields")
    add_common(dec)
    dec.add_argument("--csr", required=True, help="CSR name (e.g. mstatus)")
    dec.add_argument("--value", required=True, help="Value (hex 0x..., bin 0b..., or decimal)")

    diff = sub.add_parser("diff", help="Given XOR mask (before ^ after), list which fields changed")
    add_common(diff)
    diff.add_argument("--csr", required=True, help="CSR name")
    diff.add_argument("--xor", required=True, help="XOR mask value (hex/bin/dec)")

    cmp = sub.add_parser("compare", help="Compare two CSR values and show differing fields")
    add_common(cmp)
    cmp.add_argument("--csr", required=True, help="CSR name")
    cmp.add_argument("--value1", required=True, help="First value (hex/bin/dec)")
    cmp.add_argument("--value2", required=True, help="Second value (hex/bin/dec)")

    args = p.parse_args(argv)

    parser = UDBParser(args.spec)
    csrs = parser.load_all()
    csr = parser.get(args.csr)
    if csr is None:
        print(f"CSR '{args.csr}' not found under {args.spec}. Available count: {len(csrs)}", file=sys.stderr)
        # print some names
        sample = list(csrs.keys())[:50]
        print("Some available CSRs:", ", ".join(sample), file=sys.stderr)
        sys.exit(2)

    decoder = Decoder(xlen=args.xlen)
    if args.cmd == "decode":
        val = parse_int(args.value)
        decoded = decoder.decode_value(csr, val)
        if args.json:
            print(json.dumps({"csr": csr.name, "value": hex(val), "decoded": decoded}, indent=2))
        else:
            pretty_print_decode(csr.name, decoded)
    elif args.cmd == "diff":
        xm = parse_int(args.xor)
        diffs = decoder.decode_xor_mask(csr, xm)
        if args.json:
            print(json.dumps({"csr": csr.name, "xor": hex(xm), "changes": diffs}, indent=2))
        else:
            pretty_print_diff(csr.name, diffs)
    elif args.cmd == "compare":
        val1 = parse_int(args.value1)
        val2 = parse_int(args.value2)
        decoded1 = decoder.decode_value(csr, val1)
        decoded2 = decoder.decode_value(csr, val2)
        if args.json:
            diffs = [{"field": f1["name"], "value1": f1["value"], "value2": f2["value"]} for f1, f2 in zip(decoded1, decoded2) if f1["value"] != f2["value"]]
            print(json.dumps({"csr": csr.name, "value1": hex(val1), "value2": hex(val2), "differences": diffs}, indent=2))
        else:
            pretty_print_compare(csr.name, decoded1, decoded2)
    else:
        p.print_help()

if __name__ == "__main__":
    main()