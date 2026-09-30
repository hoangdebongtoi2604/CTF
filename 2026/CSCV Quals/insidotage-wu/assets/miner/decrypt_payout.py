"""Offline decoder reconstructed from kworker1's SIGHUP handler. Does not execute malware."""
import struct
from pathlib import Path

KEY=bytes.fromhex('11273a4c59687d8e90abbccddeeff102')
IV=bytes.fromhex('a1b2c3d4e5f60718')

def decrypt(ciphertext):
    key=struct.unpack('<4I',KEY)
    result=bytearray();previous=IV
    for offset in range(0,len(ciphertext),8):
        block=ciphertext[offset:offset+8]
        a,b=struct.unpack('<2I',block);total=0xc6ef3720
        for _ in range(32):
            b=(b-(((((a<<4)^(a>>5))+a)&0xffffffff)^((total+key[(total>>11)&3])&0xffffffff)))&0xffffffff
            total=(total-0x9e3779b9)&0xffffffff
            a=(a-(((((b<<4)^(b>>5))+b)&0xffffffff)^((total+key[total&3])&0xffffffff)))&0xffffffff
        result.extend(x^y for x,y in zip(struct.pack('<2I',a,b),previous))
        previous=block
    padding=result[-1]
    assert 1<=padding<=8 and result[-padding:]==bytes([padding])*padding
    return bytes(result[:-padding])

if __name__=='__main__':
    print(decrypt(Path(__file__).with_name('payout_cipher.bin').read_bytes()).decode('ascii'))
