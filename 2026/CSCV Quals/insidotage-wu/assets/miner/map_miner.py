import sys,json,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'agent5b'))
from hunt import Dump
from js_hunt import AddressSpace
BASE=Path(__file__).parent
d=Dump();off=int(sys.argv[1]) if len(sys.argv)>1 else 781227424
states=[(d.phys(off)&~4095,d.phys(off)&4095,[])]
cache={}
for level in range(4):
    nxt=[]
    for phys,va,path in states:
        if phys not in cache:
            out=subprocess.check_output([str(BASE/'pte_refs.exe'),str(d.f.name),str(phys)],text=True)
            cache[phys]=[list(map(int,line.split())) for line in out.splitlines()]
        for parent,idx,raw,val in cache[phys]:
            if parent in [x[0] for x in path] or (level==3 and idx>=256):continue
            nxt.append((parent,va|(idx<<(12+9*level)),path+[(parent,idx,raw,hex(val))]))
    states=nxt
    print('LEVEL',level+1,'STATES',len(states),flush=True)
    if len(states)>1000:raise RuntimeError('Too many')
result=[{'root':p,'va':v,'va_hex':hex(v),'path':path,'raw':off} for p,v,path in states]
(BASE/f'mapping_{off}.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result),flush=True)
