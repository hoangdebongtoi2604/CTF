import hashlib, json, re
from pathlib import Path
import snappy
from Cryptodome.Cipher import AES
from sqlite_carve import varint, record, MEM

def material():
    with MEM.open('rb') as f:
        start=1573972680
        f.seek(start); b=f.read(650)
    params={}
    for p in range(len(b)):
        try:
            n,q=varint(b,p)
            if not 20<n<180:continue
            vals,serials,spans=record(b,q,q+n)
            if len(vals)!=5 or vals[0]!=1 or not isinstance(vals[1],str):continue
            key=bytes((x-1)%256 for x in bytes.fromhex(vals[1]))
            if b'vault' not in key:continue
            decoded=snappy.decompress(bytes.fromhex(vals[-1]))
            value=re.search(rb'[0-9a-f]{32,}',decoded).group().decode()
            name=key.decode(errors='replace').strip('\x2f\x00').split('/')[-1]
            params[name]=value
            print(start+p,name,value,len(value),flush=True)
        except Exception:pass
    data=Path('work/vault_structured_clone.bin').read_bytes()
    ciphertext=re.search(rb'__uint8array__([0-9a-f]{200,})',data).group(1).decode()
    params['sensitive']=ciphertext
    Path('work/vault_params.json').write_text(json.dumps(params,indent=2))
    return params

def decrypt(key,iv,ct):
    return AES.new(key,AES.MODE_CTR,nonce=b'',initial_value=int.from_bytes(iv,'big')).decrypt(ct)

def crack(candidates):
    p=material()
    p={k:bytes.fromhex(v) for k,v in p.items()}
    for password in candidates:
        dk=hashlib.pbkdf2_hmac('sha256',password.encode(),p['userPasswordSalt'],4000,32)
        if hashlib.sha256(dk[16:]+p['passwordCipher'][16:]).digest()!=p['userPasswordMac']:continue
        master=decrypt(dk,p['userPasswordSalt'],p['passwordCipher'])
        counter=decrypt(master,p['aesCounterSalt'],p['aesCounterCipher'])
        plain=decrypt(master,counter,p['sensitive'])
        print('FOUND PASSWORD',repr(password),'MASTER',master.hex(),'COUNTER',counter.hex(),'PLAIN',plain,flush=True)
        Path('work/decrypted_wallet.json').write_bytes(plain)
        return
    print('No match',len(candidates),flush=True)

if __name__=='__main__':
    candidates=set(['12345678','123456789','1234567890','123456','password','password123','Password123!','P@ssw0rd','P@ssw0rd!','P@ssw0rd123','P@ssw0rd123!','changeme','centos','vagrant','admin','admin123','root','toor'])
    for root in ['Vietdollar','vietdollar','VietDollar','VietDollar','Centos','centos','Admin','admin','Password','password','Keplr','keplr','CSCV','cscv','insidogetage']:
        for suffix in ['','1','123','1234','123456','12345678','2026','2026!','@123','@2026','123!','!','@123456']:
            candidates.add(root+suffix)
    crack(candidates)
