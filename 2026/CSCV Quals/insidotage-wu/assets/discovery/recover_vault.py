from pathlib import Path
import struct
import json
import snappy
import re
from sqlite_carve import varint,record,MEM

with MEM.open('rb') as f:
    f.seek(1573972200);window=f.read(600)
    for pos in range(40):
        n,p=varint(window,pos)
        if n!=3007:continue
        print('CELL',1573972200+pos,'payload',n,'header',window[p:p+12].hex())
        local=489
        print('OVERFLOW_PAGE',int.from_bytes(window[p+local:p+local+4],'big'))
        f.seek(1562370112)
        more=f.read(4096)
        print('NEXT_OVERFLOW',int.from_bytes(more[:4],'big'))
        payload=window[p:p+local]+more[4:4+n-local]
        vals,serials,spans=record(payload,0,len(payload))
        print('SERIALS',serials)
        print('META',vals[:-1])
        comp=bytes.fromhex(vals[-1])
        out=snappy.decompress(comp)
        Path('work/vault_structured_clone.bin').write_bytes(out)
        print('DECOMPRESSED',len(out))
        for m in re.finditer(rb'[\x20-\x7e]{4,}',out):print(m.start(),m.group().decode())
