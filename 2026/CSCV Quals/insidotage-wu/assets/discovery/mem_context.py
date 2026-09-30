from pathlib import Path
import re
import sys

sys.stdout.reconfigure(encoding='utf-8',errors='backslashreplace')
mem=Path(r'D:\ctftraining\CSCV2026\fore\insidogetage\work\mem.raw')
with mem.open('rb') as f:
    for arg in sys.argv[1:]:
        pos=int(arg)
        start=max(0,pos-2048)
        f.seek(start)
        b=f.read(8192)
        print('\nOFFSET',pos)
        for m in re.finditer(rb'[\x20-\x7e]{5,}|(?:[\x20-\x7e]\x00){5,}',b):
            x=m.group()
            print(start+m.start(),x.decode('utf-16le' if b'\x00' in x else 'ascii'))
