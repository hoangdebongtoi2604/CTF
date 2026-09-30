"""Known-offset verification, NOT a discovery solver. Offline; never executes ELF.

Usage: python verify_case.py --mem D:\path\mem.raw --out D:\case\verification
Dependencies: python-snappy, pycryptodomex, cryptography, mnemonic.
Offsets apply only to the mem.raw SHA256 documented in the writeup.
"""
import argparse
import hashlib
import hmac
import json
import mmap
import re
import struct
from pathlib import Path

import snappy
from Cryptodome.Cipher import AES
from Cryptodome.Hash import keccak
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from mnemonic import Mnemonic
from sqlite_carve import cell, record, varint
from decrypt_payout import decrypt as xtea_decrypt


class Lime:
    def __init__(self, path):
        self.file = open(path, 'rb')
        self.m = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)
        self.segments = []
        pos = 0
        while pos + 32 <= len(self.m):
            magic, version, start, end, reserved = struct.unpack_from('<IIQQQ', self.m, pos)
            if magic != 0x4c694d45 or version != 1 or end < start:
                raise ValueError(f'Invalid LiME header at {pos}')
            self.segments.append((start, end + 1, pos + 32))
            pos += 32 + end - start + 1
        if pos != len(self.m):
            raise ValueError('Unexpected trailing bytes')

    def raw(self, physical):
        for start, end, raw_start in self.segments:
            if start <= physical < end:
                return raw_start + physical - start
        raise ValueError(f'Physical address not captured: {physical:#x}')

    def virtual_raw(self, root, va):
        frame = root
        for level in (4, 3, 2, 1):
            entry = struct.unpack_from('<Q', self.m, self.raw(frame) + ((va >> (12 + 9*(level-1))) & 511)*8)[0]
            if not entry & 1:
                raise ValueError(f'Non-present page: root={root:#x} va={va:#x} level={level}')
            frame = entry & 0x000ffffffffff000
            if entry & 128 and level in (2, 3):
                bits = 12 + 9*(level-1)
                return self.raw((frame & ~((1 << bits)-1)) + (va & ((1 << bits)-1)))
        return self.raw(frame + (va & 4095))

    def read_virtual(self, root, va, length):
        result = bytearray()
        parts = []
        while len(result) < length:
            current = va + len(result)
            raw = self.virtual_raw(root, current)
            size = min(4096 - (current & 4095), length - len(result))
            parts.append({'file_offset': len(result), 'raw_offset': raw, 'size': size})
            result.extend(self.m[raw:raw+size])
        return bytes(result), parts


def aes_ctr(key, iv, data):
    return AES.new(key, AES.MODE_CTR, nonce=b'', initial_value=int.from_bytes(iv, 'big')).decrypt(data)


def pubkey(k):
    return ec.derive_private_key(k, ec.SECP256K1()).public_key().public_bytes(Encoding.X962, PublicFormat.CompressedPoint)


def wallet_pubkey(phrase):
    seed = Mnemonic.to_seed(phrase, passphrase='')
    digest = hmac.new(b'Bitcoin seed', seed, hashlib.sha512).digest()
    key, chain = int.from_bytes(digest[:32], 'big'), digest[32:]
    order = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
    for index in (0x8000002c, 0x80000076, 0x80000000, 0, 0):
        data = (b'\0' + key.to_bytes(32, 'big') if index >= 0x80000000 else pubkey(key)) + index.to_bytes(4, 'big')
        digest = hmac.new(chain, data, hashlib.sha512).digest()
        tweak = int.from_bytes(digest[:32], 'big')
        assert tweak < order
        key, chain = (key + tweak) % order, digest[32:]
        assert key
    return pubkey(key).hex()


def monero_decode(address):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    sizes = {2:1, 3:2, 5:3, 6:4, 7:5, 9:6, 10:7, 11:8}
    result = bytearray()
    for start in range(0, len(address), 11):
        block = address[start:start+11]
        value = 0
        for char in block:
            value = value*58 + alphabet.index(char)
        result.extend(value.to_bytes(sizes[len(block)], 'big'))
    checksum = keccak.new(digest_bits=256, data=bytes(result[:-4])).digest()[:4]
    assert checksum == result[-4:]
    return bytes(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mem', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    dump = Lime(args.mem)
    m = dump.m
    results = {'mode': 'known-offset evidence verification; not discovery', 'lime_segments': dump.segments}

    # Each record decoded from evidence bytes, not copied from the answers.
    histories = []
    for place_off, visit_off in ((826077288, 820026149), (1091826976, 1116800651)):
        place_id, place, _, _, _ = cell(m, place_off)
        visit_id, visit, _, _, _ = cell(m, visit_off)
        assert place[1] == 'https://www.keplr.app/'
        assert visit[2] == place_id and place[8] == visit[3]
        histories.append({'places_offset': place_off, 'visits_offset': visit_off, 'place_id': place_id,
                          'visit_id': visit_id, 'place': place, 'visit': visit, 'epoch_seconds': visit[3] // 1000000})
    results['history'] = histories
    addon = m[1209478129:1209480129]
    assert b'keplr-extension@keplr.app' in addon
    assert b'"installDate":1788604175124' in addon
    results['Q1'] = 'Keplr'
    results['Q2'] = histories[1]['epoch_seconds']
    results['Q3'] = int(re.search(rb'"installDate":([0-9]+)', addon).group(1))

    payload_len, pos = varint(m, 1573972219)
    assert payload_len == 3007
    assert int.from_bytes(m[pos+489:pos+493], 'big') == 35
    assert m[1562370112:1562370116] == b'\0'*4
    payload = m[pos:pos+489] + m[1562370116:1562370116+payload_len-489]
    values, serials, _ = record(payload, 0, len(payload))
    assert serials == [9, 42, 0, 0, 5982]
    clone = snappy.decompress(bytes.fromhex(values[-1]))
    assert len(clone) == 5192
    assert b'Vietdollar' in clone
    params = json.loads(Path(__file__).with_name('vault_params.json').read_text())
    params = {k:bytes.fromhex(v) for k,v in params.items()}
    sensitive = bytes.fromhex(re.search(rb'__uint8array__([0-9a-f]{200,})', clone).group(1).decode())
    assert sensitive == params['sensitive']
    master = m[1195430584:1195430616]
    counter = aes_ctr(master, params['aesCounterSalt'], params['aesCounterCipher'])
    secret = json.loads(aes_ctr(master, counter, sensitive))
    assert Mnemonic('english').check(secret['mnemonic'])
    derived = wallet_pubkey(secret['mnemonic'])
    assert derived == '028e8b4fd6f245ef66cce90a571988425bf26b90fdf204068f1b0e4850030e4af2'
    results.update(Q4='Vietdollar', Q5=secret['mnemonic'], derived_cosmos_public_key=derived)
    (args.out / 'vault_structured_clone.bin').write_bytes(clone)
    (args.out / 'decrypted_wallet.json').write_text(json.dumps(secret, indent=2))

    assert b'cd /tmp/' in m[1675625360:1675625450]
    assert b'nohup ./kworker1 > out 2>&1 &' in m[1675625450:1675625530]
    assert m[2071719986:2071719986+13] == b'/tmp/kworker1'
    results['Q6'] = '/tmp/kworker1'
    copies = [m[off:off+96] for off in (2517662496, 2615479136, 2696993696)]
    assert len(set(copies)) == 1
    address = xtea_decrypt(copies[0]).decode('ascii')
    decoded = monero_decode(address)
    assert len(address) == 95 and len(decoded) == 69 and decoded[0] == 18
    results.update(Q7=address, monero_checksum=decoded[-4:].hex())
    (args.out / 'payout_cipher.bin').write_bytes(copies[0])

    picture, parts = dump.read_virtual(18644992, 0x7f81acd03000, 173360)
    digest = hashlib.sha256(picture).hexdigest()
    assert len(parts) == 43 and picture[:4] == b'RIFF' and picture[8:12] == b'WEBP'
    assert digest == '0fb07dde95ea454f7419338bc4a447e84ecb20f6541a6557e1372c28293bd6a0'
    results.update(image_sha256=digest, image_pages=parts, Q8='Read recovered image visually; expected text without spaces: AIplsforgiveme')
    (args.out / 'insider-viewed-image.webp').write_bytes(picture)
    (args.out / 'verification.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    for key in ('Q1','Q2','Q3','Q4','Q5','Q6','Q7','Q8'):
        print(key, results[key])
    print('All byte-level, cryptographic and reconstruction assertions passed.')


if __name__ == '__main__':
    main()
