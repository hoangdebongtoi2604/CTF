import sys
import sqlite3
import zipfile
import mmap
import re
import json
from datetime import datetime,timezone
from sqlite_carve import MEM,cell

sys.stdout.reconfigure(encoding='utf-8',errors='backslashreplace')
source=r'D:\ctftraining\CSCV2026\fore\insidogetage\work\collect.zip'
profile='home/centos/Desktop/Old Firefox Data/n78a5dr3.default-release/'
with zipfile.ZipFile(source) as z:
    for name in ['places.sqlite','places.sqlite-wal']:
        data=z.read(profile+name)
        print('ORIGINAL ARCHIVE',name,'Keplr offsets',[m.start() for m in re.finditer(b'keplr',data)])

c=sqlite3.connect('file:D:/ctftraining/CSCV2026/fore/insidogetage/work/firefox/places.sqlite?mode=ro',uri=True)
for name in ['moz_places','moz_historyvisits']:
    print('SCHEMA',name,c.execute('select sql from sqlite_master where name=?',(name,)).fetchone())

stamps=[1788603332495755,1788604050357080]
pattern=re.compile(b'|'.join(re.escape(x.to_bytes(8,'big')) for x in stamps))
with MEM.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as mm:
    for match in pattern.finditer(mm):
        hit=match.start()
        stamp=int.from_bytes(match.group(),'big')
        print('TIMESTAMP_HIT',hit,stamp,datetime.fromtimestamp(stamp/1e6,timezone.utc).isoformat())
        start=hit-160
        b=mm[start:hit+1500]
        for p in range(160):
            try:
                rid,v,s,spans,end=cell(b,p)
                if stamp in v and len(v) >= 3:
                    print('CELL',json.dumps({'offset':start+p,'rowid':rid,'values':v,'serials':s},ensure_ascii=False))
            except (ValueError,IndexError):pass
