#!/usr/bin/env python3
"""Run one experiment command, capture stdout/stderr, and write run_meta.json (Asia/Kuala_Lumpur times).
Usage: runexp.py --dir OUTDIR --id EXP_ID --maps "Table I" --params '{"n":3,...}' [--cwd DIR] -- cmd args...
"""
import argparse, datetime, json, os, subprocess, sys, zoneinfo
KL = zoneinfo.ZoneInfo('Asia/Kuala_Lumpur')
ap = argparse.ArgumentParser()
ap.add_argument('--dir', required=True); ap.add_argument('--id', required=True)
ap.add_argument('--maps', default=''); ap.add_argument('--params', default='{}')
ap.add_argument('--cwd', default=None); ap.add_argument('--host', default='')
ap.add_argument('--timeout', type=float, default=None); ap.add_argument('--note', default='')
ap.add_argument('cmd', nargs=argparse.REMAINDER)
a = ap.parse_args()
cmd = a.cmd[1:] if a.cmd and a.cmd[0] == '--' else a.cmd
os.makedirs(a.dir, exist_ok=True)
commit = subprocess.run(['git', '-C', os.environ.get('MDC_REPO', '.'), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
# optional memory guard: if mem_requirements.json (experiment id -> MB) is present next to this script, wait
# (up to 45 min) for enough available memory and otherwise record a skip instead of risking an out-of-memory kill
import time, psutil
HERE = os.path.dirname(os.path.abspath(__file__))
REQ_FILE = os.path.join(HERE, 'mem_requirements.json')
req = json.load(open(REQ_FILE)).get(a.id) if os.path.exists(REQ_FILE) else None
if req:
    t_wait = time.time()
    while psutil.virtual_memory().available / 2**20 < req * 1.15 and time.time() - t_wait < 2700:
        time.sleep(30)
    avail = psutil.virtual_memory().available / 2**20
    if avail < req * 1.15:
        now = datetime.datetime.now(KL).isoformat(timespec='seconds')
        json.dump({'experiment_id': a.id, 'maps_to': a.maps, 'command': ' '.join(cmd), 'parameters': json.loads(a.params), 'host': a.host,
                   'start': now, 'end': now, 'git_commit': commit, 'exit_status': 'skipped_insufficient_memory',
                   'note': f'needed ~{req} MB (+15%), available {avail:.0f} MB after waiting 45 min; not run'},
                  open(os.path.join(a.dir, 'run_meta.json'), 'w'), indent=1)
        print(a.id, 'SKIPPED insufficient memory', flush=True); sys.exit(1)
start = datetime.datetime.now(KL)
with open(os.path.join(a.dir, 'stdout.log'), 'w') as fo, open(os.path.join(a.dir, 'stderr.log'), 'w') as fe:
    fo.write('$ ' + ' '.join(cmd) + '\n'); fo.flush()
    try:
        p = subprocess.run(cmd, cwd=a.cwd, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL, timeout=a.timeout)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        rc = 'timeout'
end = datetime.datetime.now(KL)
meta = {'experiment_id': a.id, 'maps_to': a.maps, 'command': ' '.join(cmd), 'cwd': a.cwd or os.getcwd(),
        'parameters': json.loads(a.params), 'host': a.host, 'start': start.isoformat(timespec='seconds'),
        'end': end.isoformat(timespec='seconds'), 'duration_s': round((end - start).total_seconds(), 1),
        'git_commit': commit, 'exit_status': rc, 'note': a.note}
json.dump(meta, open(os.path.join(a.dir, 'run_meta.json'), 'w'), indent=1)
print(a.id, 'rc', rc, f"{meta['duration_s']}s", flush=True)
sys.exit(0 if rc == 0 else 1)
