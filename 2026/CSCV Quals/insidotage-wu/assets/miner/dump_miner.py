import sys,struct,json,re,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'agent5b'))
from hunt import Dump
from js_hunt import AddressSpace
BASE=Path(__file__).parent
d=Dump();s=AddressSpace(d,1859534848)
(BASE/'pages.json').write_text(json.dumps(s.pages))
print('PAGES',len(s.pages),flush=True)
groups=[]
for va,raw in sorted(s.pages.items()):
    if not groups or va!=groups[-1][1]:groups.append([va,va+4096])
    else:groups[-1][1]+=4096
for lo,hi in groups:
    if hi-lo>64*1024*1024:continue
    data=s.read(lo,hi-lo)
    print('GROUP',hex(lo),hex(hi),hi-lo,'ELF',data[:4]==b'\x7fELF','payout',data.find(b'payout profile'),flush=True)
    if b'payout profile' in data or data[:4]==b'\x7fELF' or (0x550000000000<=lo<0x560000000000):
        name=f'group_{lo:x}.bin'
        (BASE/name).write_bytes(data)
        meta={'va':lo,'size':len(data),'hashes':{h:hashlib.new(h,data).hexdigest() for h in ('md5','sha1','sha256')}}
        (BASE/(name+'.json')).write_text(json.dumps(meta,indent=2))
        strings=[]
        for m in re.finditer(rb'[\x20-\x7e]{5,}',data):
            text=m.group().decode();strings.append(f'{lo+m.start():x} {text}')
            if re.search('payout|profile|secret|key|cipher|nonce|\.enc|wallet|/tmp/',text,re.I) and len(text)<300:print(hex(lo+m.start()),text,flush=True)
        (BASE/(name+'.strings.txt')).write_text('\n'.join(strings),encoding='utf8')
print('DONE',flush=True)
