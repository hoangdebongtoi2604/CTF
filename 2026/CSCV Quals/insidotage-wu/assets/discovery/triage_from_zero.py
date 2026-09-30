"""Triage evidence containers and standard Linux artifacts, without answer keywords.

Does not execute evidence, follow symlinks, or extract arbitrary ZIP paths.
"""
import argparse
import collections
import csv
import json
import re
import stat
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def write_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    copydir = args.out/'selected_copies'
    copydir.mkdir(exist_ok=True)
    summary = {'case':str(args.case), 'method':'container inventory + standard artifact triage; no challenge-specific search terms'}
    with zipfile.ZipFile(args.case/'dist.zip') as z:
        summary['outer_members'] = [{'path':i.filename,'size':i.file_size,'zip_date_no_timezone':str(i.date_time)} for i in z.infolist()]
    mem = args.case/'work/mem.raw'
    with mem.open('rb') as f:
        head = f.read(64)
    summary['memory_header_hex'] = head.hex(' ')
    summary['memory_size'] = mem.stat().st_size
    if head[:4] == b'EMiL':
        summary['lime_first_header'] = dict(zip(('magic','version','start','end','reserved'),struct.unpack('<IIQQQ',head[:32])))
    rows = []
    text_artifacts = []
    all_names = []
    with zipfile.ZipFile(args.case/'work/collect.zip') as z:
        info_by_name = {i.filename:i for i in z.infolist()}
        all_names = list(info_by_name)
        for i in z.infolist():
            mode = i.external_attr >> 16
            kind = 'directory' if i.is_dir() else 'symlink' if stat.S_ISLNK(mode) else 'file'
            row = {'path':i.filename,'kind':kind,'size':i.file_size,'compressed_size':i.compress_size,
                   'zip_date_no_timezone':datetime(*i.date_time).isoformat(),'mode':oct(mode),'crc32':f'{i.CRC:08x}'}
            rows.append(row)
        summary['member_count'] = len(rows)
        summary['top_level_counts'] = dict(collections.Counter(r['path'].split('/')[0] for r in rows))
        summary['disk_image_candidates'] = [r for r in rows if re.search(r'\.(?:e01|ex01|dd|vmdk|vhdx?|qcow2|aff4?)$',r['path'],re.I)]
        summary['ntfs_metadata_candidates'] = [r for r in rows if any(x in r['path'] for x in ('$MFT','$UsnJrnl','$LogFile')) or r['path'].rsplit('/',1)[-1]=='$J']
        baseline = ['etc/os-release','etc/centos-release','etc/redhat-release','etc/hostname','etc/fstab','etc/passwd','etc/group','etc/timezone','etc/localtime','etc/crontab','etc/anacrontab','etc/rc.d/rc.local','etc/sudoers']
        baseline += [n for n in all_names if n.startswith(('home/','root/')) and n.rsplit('/',1)[-1] in ('.bash_history','.zsh_history','profiles.ini','installs.ini','recently-used.xbel')]
        baseline += [n for n in all_names if n.startswith(('etc/cron.d/','etc/sudoers.d/','var/spool/cron/')) and not n.endswith('/')]
        summary['standard_artifacts'] = []
        for name in dict.fromkeys(baseline):
            if name not in info_by_name:
                summary['standard_artifacts'].append({'path':name,'status':'absent from collection inventory'})
                continue
            info = info_by_name[name]
            item = {'path':name,'size':info.file_size,'mode':oct(info.external_attr>>16)}
            if info.file_size <= 256000:
                data = z.read(name)
                if b'\0' not in data[:2000]:
                    item['text'] = data.decode('utf-8',errors='replace')
            summary['standard_artifacts'].append(item)
        log_names = [n for n in all_names if n.startswith('var/log/') and not n.endswith('/')]
        summary['log_inventory'] = [{'path':n,'size':info_by_name[n].file_size} for n in log_names]
        for name in log_names:
            info = info_by_name[name]
            if info.file_size > 16000000 or name.endswith(('.gz','.xz','.journal','.journal~')):
                continue
            data = z.read(name)
            if b'\0' in data[:8192]:
                continue
            dest = copydir / name.replace('/','__')
            dest.write_bytes(data)
            text_artifacts.append((name,data))
    write_csv(args.out/'inventory.csv',rows,list(rows[0]))
    user_rows = [r for r in rows if r['path'].startswith(('home/','root/','tmp/')) and r['kind']!='directory']
    write_csv(args.out/'user_file_inventory.csv',user_rows,list(rows[0]))
    browser_rows = [r for r in rows if re.search(r'firefox|chromium|google-chrome|places\.sqlite|profiles\.ini',r['path'],re.I)]
    write_csv(args.out/'browser_inventory.csv',browser_rows,list(rows[0]))
    persistence = [r for r in rows if r['path'].startswith(('etc/systemd/system/','etc/cron','var/spool/cron/','etc/rc.d/'))]
    write_csv(args.out/'persistence_inventory.csv',persistence,list(rows[0]))
    grouped = collections.defaultdict(list)
    log_hits = []
    audit_types = collections.Counter()
    for name,data in text_artifacts:
        offset = 0
        for line_number,rawline in enumerate(data.splitlines(keepends=True),1):
            line = rawline.decode('utf-8',errors='replace').rstrip('\r\n')
            m = re.search(r'type=(\S+)\s+msg=audit\((\d+(?:\.\d+)?):(\d+)\)',line)
            if m:
                typ,stamp,event = m.groups()
                audit_types[typ] += 1
                decoded = ''
                for key in ('proctitle','cmd'):
                    field = re.search(r'\b'+key+r'=([0-9A-Fa-f]{4,})(?=\s|\x27|$)',line)
                    if field:
                        try:
                            decoded += key+'='+bytes.fromhex(field.group(1)).replace(b'\0',b' ').decode('utf-8',errors='replace')+' '
                        except ValueError:
                            pass
                grouped[(name,stamp,event)].append({'type':typ,'line':line_number,'offset':offset,'raw':line,'decoded':decoded.strip()})
            elif re.search(r'sudo:|COMMAND=|Accepted |Failed password|passwd|session (?:opened|closed)|CROND|Linux version|systemd\[1\].*(?:Starting|Started)',line):
                log_hits.append({'source':name,'line':line_number,'raw_offset':offset,'text':line})
            offset += len(rawline)
    events = []
    for (name,stamp,event),records in grouped.items():
        text = ' | '.join(r['decoded'] or r['raw'] for r in records)
        events.append({'UTC':datetime.fromtimestamp(float(stamp),timezone.utc).isoformat(),
                       'epoch':stamp,'source':name,'event_id':event,'types':','.join(dict.fromkeys(r['type'] for r in records)),
                       'first_line':records[0]['line'],'first_raw_offset':records[0]['offset'],'text':text})
    events.sort(key=lambda r:float(r['epoch']))
    summary['audit_types'] = dict(audit_types)
    summary['audit_event_count'] = len(events)
    summary['audit_bounds_utc'] = [events[0]['UTC'],events[-1]['UTC']] if events else []
    write_csv(args.out/'audit_events.csv',events,['UTC','epoch','source','event_id','types','first_line','first_raw_offset','text'])
    commands = [e for e in events if any(x in e['types'].split(',') for x in ('EXECVE','USER_CMD','PROCTITLE'))]
    write_csv(args.out/'audit_commands.csv',commands,['UTC','epoch','source','event_id','types','first_line','first_raw_offset','text'])
    write_csv(args.out/'log_triage_hits.csv',log_hits,['source','line','raw_offset','text'])
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ('member_count','top_level_counts','disk_image_candidates','ntfs_metadata_candidates','audit_event_count','audit_bounds_utc','audit_types')},indent=2))


if __name__ == '__main__':
    main()
