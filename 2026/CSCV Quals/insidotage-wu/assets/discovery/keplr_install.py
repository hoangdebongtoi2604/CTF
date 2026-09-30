from pathlib import Path
import subprocess
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8',errors='backslashreplace')
mem=Path(r'D:\ctftraining\CSCV2026\fore\insidogetage\work\mem.raw')
out=subprocess.check_output(['rg','-a','-b','-o','-F','keplr-extension@keplr.app',str(mem)],text=True)
Path('work/keplr_extension_hits.txt').write_text(out)
seen=set()
with mem.open('rb') as f:
    for line in out.splitlines():
        hit=int(line.split(':')[0])
        start=max(0,hit-8192)
        f.seek(start)
        b=f.read(24576)
        for m in re.finditer(rb'"(?:installDate|updateDate|firstInstallDate)"\s*:\s*[0-9]+',b):
            abspos=start+m.start()
            if abspos in seen: continue
            seen.add(abspos)
            print('DATE',abspos,'nearest_keplr',hit,'delta',abspos-hit,m.group().decode())
            print('CONTEXT',repr(b[max(0,m.start()-900):m.end()+500]))
        for m in re.finditer(rb'\{\s*"id"\s*:\s*"keplr-extension@keplr\.app"',b):
            try:
                obj,n=json.JSONDecoder().raw_decode(b[m.start():].decode('utf8',errors='replace'))
                print('ADDON',start+m.start(),json.dumps(obj,ensure_ascii=False))
            except ValueError:pass
