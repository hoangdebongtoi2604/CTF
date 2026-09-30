"""Reproduce the CSCV2026 GPS drawing from challenge.pcap.

Python 3 standard library only; Pillow is optional for PNG output.
Scope: classic PCAP, Ethernet/IPv4/UDP, one MAVLink 2 frame per datagram.
The capture is read-only. Payload text is never executed or trusted as instructions.
"""
import argparse
import csv
import hashlib
import json
import math
import struct
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path

EXTRA = {24: 24, 33: 104, 124: 87, 253: 83}


def crc_mavlink(data, extra):
    value = 0xffff
    for byte in data + bytes([extra]):
        tmp = byte ^ (value & 0xff)
        tmp ^= (tmp << 4) & 0xff
        value = ((value >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)) & 0xffff
    return value


def pcap_records(path):
    with path.open('rb') as stream:
        header = stream.read(24)
        formats = {b'\xd4\xc3\xb2\xa1': ('<', 1e6), b'\xa1\xb2\xc3\xd4': ('>', 1e6),
                   b'\x4d\x3c\xb2\xa1': ('<', 1e9), b'\xa1\xb2\x3c\x4d': ('>', 1e9)}
        if len(header) != 24 or header[:4] not in formats:
            raise ValueError('Expected classic PCAP, not PCAPNG')
        endian, resolution = formats[header[:4]]
        if struct.unpack_from(endian+'I', header, 20)[0] != 1:
            raise ValueError('Expected Ethernet link type 1')
        frame = 0
        while record := stream.read(16):
            if len(record) != 16:
                raise ValueError('Truncated PCAP record header')
            sec, fraction, length, _ = struct.unpack(endian+'IIII', record)
            packet = stream.read(length)
            if len(packet) != length:
                raise ValueError('Truncated PCAP packet')
            frame += 1
            yield frame, sec + fraction/resolution, packet


def udp_payload(packet):
    if len(packet) < 42 or packet[12:14] != b'\x08\x00' or packet[14] >> 4 != 4:
        return None
    ihl = (packet[14] & 15) * 4
    if ihl < 20 or packet[23] != 17 or int.from_bytes(packet[20:22], 'big') & 0x3fff:
        return None
    start = 14 + ihl
    if start + 8 > len(packet):
        return None
    sport, dport, size, _ = struct.unpack_from('!HHHH', packet, start)
    if size < 8 or start + size > len(packet):
        return None
    src = '.'.join(map(str, packet[26:30]))
    dst = '.'.join(map(str, packet[30:34]))
    return src, sport, dst, dport, packet[start+8:start+size]


def projected(records):
    lat0 = sum(p[2] for p in records) / len(records)
    lon0 = sum(p[3] for p in records) / len(records)
    xy = [((p[3]-lon0)*111320*math.cos(math.radians(lat0)),
           (p[2]-lat0)*111320) for p in records]
    xx = sum(x*x for x,y in xy)
    yy = sum(y*y for x,y in xy)
    cross = sum(x*y for x,y in xy)
    theta = .5 * math.atan2(2*cross, xx-yy)
    uv = [(x*math.cos(theta)+y*math.sin(theta),
           -x*math.sin(theta)+y*math.cos(theta)) for x,y in xy]
    return uv, math.degrees(theta)


def keep_edge(a, b):
    # Display heuristic for this dataset, not a GPS validity test.
    local = abs(a[0]-b[0]) <= 12
    low_stroke = max(a[1],b[1]) < -36 and abs(a[0]-b[0]) <= 16
    return (local or low_stroke) and math.dist(a,b) <= 36 and ((a[1]>12) == (b[1]>12))


def render(points, target, title, clean=False):
    lo = min(x for x,y in points)-5
    hi = max(x for x,y in points)+5
    bottom = min(y for x,y in points)-5
    top = max(y for x,y in points)+5
    width, height = hi-lo, top-bottom
    edges = [(a,b) for a,b in zip(points, points[1:]) if not clean or keep_edge(a,b)]
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
           f'<title>{escape(title)}</title>', '<rect width="100%" height="100%" fill="white"/>',
           '<g stroke="#101827" stroke-width="0.3" fill="none">']
    for a,b in edges:
        svg.append(f'<path d="M {a[0]-lo:.6f},{top-a[1]:.6f} L {b[0]-lo:.6f},{top-b[1]:.6f}"/>')
    svg.extend(['</g>', '</svg>'])
    target.with_suffix('.svg').write_text('\n'.join(svg), encoding='utf-8')
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return len(edges)
    scale = 5900/width
    image = Image.new('RGB', (6000, round(height*scale)+100), 'white')
    draw = ImageDraw.Draw(image)
    for a,b in edges:
        draw.line([(50+(a[0]-lo)*scale,50+(top-a[1])*scale),
                   (50+(b[0]-lo)*scale,50+(top-b[1])*scale)],
                  fill='#101827', width=max(2,round(.2*scale)))
    image.save(target.with_suffix('.png'))
    return len(edges)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pcap', type=Path)
    parser.add_argument('--out', type=Path, default=Path('gps_result'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with args.pcap.open('rb') as source:
        for block in iter(lambda: source.read(1024*1024), b''):
            digest.update(block)
    stats = Counter()
    endpoints = Counter()
    systems = Counter()
    messages = Counter()
    checks = Counter()
    stages = Counter()
    gps = defaultdict(list)
    gpi = defaultdict(list)
    altitudes = Counter()
    hints = []
    first = last = None
    for frame, timestamp, packet in pcap_records(args.pcap):
        stats['pcap_packets'] += 1
        first = timestamp if first is None else min(first,timestamp)
        last = timestamp if last is None else max(last,timestamp)
        udp = udp_payload(packet)
        if udp is None:
            continue
        src,sport,dst,dport,wire = udp
        stats['udp_packets'] += 1
        endpoints[(src,sport,dst,dport)] += 1
        if len(wire)<12 or wire[0]!=0xfd or len(wire)<wire[1]+12:
            continue
        length,sysid,mid = wire[1],wire[5],int.from_bytes(wire[7:10],'little')
        stats['mavlink2_frames'] += 1
        systems[(src,sysid)] += 1
        messages[mid] += 1
        if mid not in EXTRA:
            continue
        payload = wire[10:10+length]
        good = crc_mavlink(wire[1:10+length],EXTRA[mid]) == int.from_bytes(wire[10+length:12+length],'little')
        checks[(sysid,mid,good)] += 1
        if mid==253:
            text = payload[1:51].split(b'\0')[0].decode('ascii','backslashreplace')
            if any(word in text for word in ('FLAG','MD5','GPS2_RAW','fix_type','sats')):
                hints.append({'frame':frame,'sysid':sysid,'crc_valid':good,'text':text})
        if not good:
            continue
        if mid==33:
            v=struct.unpack('<IiiiihhhH',payload[:28].ljust(28,b'\0'))
            if 29800<=v[3]<=30200:
                gpi[sysid].append((v[1]/1e7,v[2]/1e7))
        if mid not in (24,124):
            continue
        fmt = '<QiiiHHHHBB' if mid==24 else '<QiiiIHHHHBB'
        size = struct.calcsize(fmt)
        v = struct.unpack(fmt,payload[:size].ljust(size,b'\0'))
        stamp,lat,lon,alt = v[:4]
        fix,sats = v[-2:]
        stages[(sysid,mid,'crc_valid')] += 1
        if sysid==3 and mid==24:
            altitudes[alt] += 1
        if fix<3 or sats<8:
            continue
        stages[(sysid,mid,'quality')] += 1
        if not 29800<=alt<=30200:
            continue
        stages[(sysid,mid,'altitude')] += 1
        lat,lon = lat/1e7,lon/1e7
        if not (10.761<=lat<=10.775 and 106.645<=lon<=106.662):
            continue
        gps[(sysid,mid)].append((frame,timestamp,lat,lon,alt/1000,fix,sats,stamp))
    selected = gps[(3,24)]
    if not selected:
        raise ValueError('No SYSID 3 GPS_RAW_INT points match the challenge filter')
    uv,angle = projected(selected)
    with (args.out/'gps_sys3.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.writer(stream)
        writer.writerow(['frame','capture_epoch','latitude','longitude','altitude_m','fix','satellites','time_usec','u_m','v_m'])
        writer.writerows([*row,*point] for row,point in zip(selected,uv))
    render(uv,args.out/'gps_full','SYSID 3 GPS_RAW_INT: all consecutive edges')
    retained=render(uv,args.out/'gps_clean','SYSID 3: heuristic connector filtering',clean=True)
    for (sysid,mid),rows in sorted(gps.items()):
        points,_=projected(rows)
        render(points,args.out/f'track_sys{sysid}_msg{mid}',f'SYSID {sysid}, message {mid}')
    coordinates={(r[2],r[3]) for r in selected}
    report={
        'source_sha256':digest.hexdigest(), 'source_size':args.pcap.stat().st_size,
        **stats, 'first_utc':datetime.fromtimestamp(first,timezone.utc).isoformat(),
        'last_utc':datetime.fromtimestamp(last,timezone.utc).isoformat(), 'duration_seconds':last-first,
        'endpoints':[{'src':k[0],'sport':k[1],'dst':k[2],'dport':k[3],'packets':v} for k,v in sorted(endpoints.items())],
        'systems':[{'src':k[0],'sysid':k[1],'packets':v} for k,v in sorted(systems.items())],
        'messages':dict(messages), 'crc_counts':{str(k):v for k,v in sorted(checks.items())},
        'filter_stages':{str(k):v for k,v in sorted(stages.items())},
        'filtered_tracks':{f'{sysid}-{mid}':len(rows) for (sysid,mid),rows in sorted(gps.items())},
        'sys3_gps24_valid_altitudes_top10':altitudes.most_common(10),
        'sys3_gpi33_records':len(gpi[3]), 'sys3_gpi33_unique':len(set(gpi[3])),
        'gps24_gpi33_coordinate_sets_equal':coordinates==set(gpi[3]),
        'pca_axis_degrees':angle, 'retained_edges':retained, 'original_edges':len(uv)-1,
        'selected_first':selected[0], 'selected_last':selected[-1], 'statustext_leads':hints,
    }
    (args.out/'report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('statustext_leads','crc_counts','messages','filter_stages')},indent=2))
    print('Open gps_full.svg and gps_clean.svg; read the letters, then add CSCV2026{...}.')


if __name__=='__main__':
    main()
