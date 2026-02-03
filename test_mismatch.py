#!/usr/bin/env python3
"""
Simple test for CSR mismatch verification
Based on mismatch info at PC 0x0080000058
"""

from udblib.parser import UDBParser
from udblib.decoder import Decoder

def test_csr_mismatch():
    """Test CSR mismatches between reference and DUT"""
    
    # Mismatch data
    mismatches = {
        'mstatus': {
            'pc': '0x0080000058',
            'ref': '0x0000000a00002000',
            'dut': '0x8000000a00006000'
        },
        'sstatus': {
            'pc': '0x0080000058',
            'ref': '0x0000000200002000',
            'dut': '0x8000000200006000'
        }
    }
    
    # Initialize parser and decoder
    spec_path = "riscv-unified-db/spec/std/isa/csr"
    parser = UDBParser(spec_path)
    parser.load_all()
    decoder = Decoder(xlen=64)
    
    print("=" * 80)
    print(f"CSR Mismatch Analysis at PC: {mismatches['mstatus']['pc']}")
    print("=" * 80)
    
    for csr_name, data in mismatches.items():
        print(f"\n{'=' * 80}")
        print(f"CSR: {csr_name.upper()}")
        print(f"{'=' * 80}")
        
        csr = parser.get(csr_name)
        if csr is None:
            print(f"ERROR: CSR '{csr_name}' not found")
            continue
        
        # Parse values
        ref_val = int(data['ref'], 16)
        dut_val = int(data['dut'], 16)
        xor_mask = ref_val ^ dut_val
        
        print(f"REF value: {data['ref']} ({ref_val})")
        print(f"DUT value: {data['dut']} ({dut_val})")
        print(f"XOR mask:  0x{xor_mask:016x}\n")
        
        # Decode both values
        print(f"--- Reference Value Decoding ---")
        ref_decoded = decoder.decode_value(csr, ref_val)
        for f in ref_decoded:
            bits = f"[{f['msb']}:{f['lsb']}]" if f['msb'] != f['lsb'] else f"[{f['msb']}]"
            print(f"  {f['name']:20} {bits:10} = {f['bin']:>10} ({f['value']:>5}) {f.get('desc', '')}")
        
        print(f"\n--- DUT Value Decoding ---")
        dut_decoded = decoder.decode_value(csr, dut_val)
        for f in dut_decoded:
            bits = f"[{f['msb']}:{f['lsb']}]" if f['msb'] != f['lsb'] else f"[{f['msb']}]"
            print(f"  {f['name']:20} {bits:10} = {f['bin']:>10} ({f['value']:>5}) {f.get('desc', '')}")
        
        # Show differences
        print(f"\n--- Differences ---")
        differences_found = False
        for f1, f2 in zip(ref_decoded, dut_decoded):
            if f1['value'] != f2['value']:
                differences_found = True
                bits = f"[{f1['msb']}:{f1['lsb']}]" if f1['msb'] != f1['lsb'] else f"[{f1['msb']}]"
                print(f"  {f1['name']:20} {bits:10}: REF={f1['bin']:>10} ({f1['value']:>5}) vs DUT={f2['bin']:>10} ({f2['value']:>5})")
                print(f"    Description: {f1.get('desc', 'N/A')}")
        
        if not differences_found:
            print("  No differences found in decoded fields")
        
        # Show changed fields using XOR mask
        print(f"\n--- Changed Fields (using XOR mask) ---")
        try:
            changes = decoder.decode_xor_mask(csr, xor_mask)
            if changes:
                for c in changes:
                    print(f"  {c['name']:20} [{c['msb']:2d}:{c['lsb']:2d}] changed_mask={c['changed_mask']} bits={c.get('changed_bits_count', 'N/A')}")
            else:
                print("  No fields changed according to XOR mask analysis")
        except Exception as e:
            print(f"  XOR mask analysis skipped: {e}")
    
    print("\n" + "=" * 80)
    print("Test completed")
    print("=" * 80)

if __name__ == "__main__":
    test_csr_mismatch()
