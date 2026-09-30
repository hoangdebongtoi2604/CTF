import struct
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

MEM = Path(r'D:\ctftraining\CSCV2026\fore\insidogetage\work\mem.raw')

def varint(b, pos):
    v = 0
    for i in range(9):
        x = b[pos+i]
        if i == 8:
            return (v << 8) | x, pos+i+1
        v = (v << 7) | (x & 127)
        if x < 128:
            return v, pos+i+1
    raise ValueError()

def record(b, start, end):
    hl, p = varint(b, start)
    he = start+hl
    if hl < 2 or he > end or hl > 128:
        raise ValueError()
    serials = []
    while p < he:
        s, p = varint(b, p)
        serials.append(s)
    if p != he:
        raise ValueError()
    vals = []
    pos = he
    spans = []
    for s in serials:
        n = {0:0,1:1,2:2,3:3,4:4,5:6,6:8,7:8,8:0,9:0}.get(s)
        if n is None:
            if s < 12: raise ValueError()
            n = (s-12)//2
        if pos+n > end:
            raise ValueError()
        x = b[pos:pos+n]
        if s == 0: v = None
        elif s in (8,9): v = s-8
        elif s == 7: v = struct.unpack('>d', x)[0]
        elif s < 7: v = int.from_bytes(x,'big',signed=True)
        elif s % 2: v = x.decode('utf-8', 'replace')
        else: v = x.hex()
        vals.append(v)
        spans.append((pos,pos+n))
        pos += n
    if pos != end:
        raise ValueError()
    return vals, serials, spans

def cell(b,p):
    n, q = varint(b,p)
    rowid, q = varint(b,q)
    if n < 3 or n > 16000 or q+n > len(b): raise ValueError()
    v,s,spans = record(b,q,q+n)
    return rowid,v,s,spans,q+n

def url_hits():
    import subprocess
    out = subprocess.check_output(['rg','-a','-b','-o','https://www\\.keplr\\.app',str(MEM)],text=True)
    return [int(line.split(':')[0]) for line in out.splitlines()]

def main():
    sys.stdout.reconfigure(encoding='utf-8',errors='backslashreplace')
    results=[]
    with MEM.open('rb') as f:
        for hit in url_hits():
            start=hit-160
            f.seek(start)
            b=f.read(1800)
            for p in range(160):
                try:
                    rowid,v,s,spans,end = cell(b,p)
                    if any(isinstance(x,str) and x.startswith('https://www.keplr.app') and span[0]==160 for x,span in zip(v,spans)):
                        result={'offset':start+p,'hit':hit,'rowid':rowid,'values':v,'serials':s}
                        results.append(result)
                        print(json.dumps(result,ensure_ascii=False))
                except (ValueError,IndexError,struct.error): pass
    Path('work/keplr_records.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__ == '__main__': main()
