import struct,re,json,hashlib
from pathlib import Path
B=Path(__file__).parent
targets=[0x55c2d1a36a30,0x55c2d1a36a68,0x55c2d1a36a90,0x55c2d1a340d8]
for f in B.glob('group_55*.bin'):
    base=int(f.stem.split('_')[1],16);data=f.read_bytes()
    for m in re.finditer(rb'[\x48\x4c][\x8d\x8b][\x05\x0d\x15\x1d\x25\x2d\x35\x3d]',data):
        if m.start()+7>len(data):continue
        dest=base+m.start()+7+struct.unpack_from('<i',data,m.start()+3)[0]
        if any(abs(dest-t)<8 for t in targets):print('XREF',f.name,hex(base+m.start()),'to',hex(dest))
base=0x55c2d17fe000;end=0x55c2d1b42000
data=bytearray(end-base)
for f in B.glob('group_55*.bin'):
    va=int(f.stem.split('_')[1],16)
    if base<=va<end:data[va-base:va-base+f.stat().st_size]=f.read_bytes()
(B/'miner_mapped.bin').write_bytes(data)
(B/'miner_mapped.json').write_text(json.dumps({'base':base,'size':len(data),'type':'partial ELF64 Linux x86-64 memory reconstruction; missing pages zero-filled','hashes':{h:hashlib.new(h,data).hexdigest() for h in ('md5','sha1','sha256')}},indent=2))
