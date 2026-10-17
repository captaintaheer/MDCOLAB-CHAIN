python3 - << 'PY'
import os, re
base_dir = '/Users/tahirolaosebikan/python-tahir/MDCOLAB-CHAIN'
report = os.path.join(base_dir, 'metrics_report.md')
vals = {}
with open(report,'r') as f:
    for line in f:
        m = re.match(r"\|\s*(.*?)\s*\|\s*([0-9A-Za-z\.]+)\s*\|", line)
        if m:
            k = m.group(1).strip()
            v = m.group(2).strip()
            try:
                vals[k] = float(v)
            except Exception:
                vals[k] = v
import sys
sys.path.append(base_dir)
import  as al
rates = [50,100,150,200,250]
counts = [1,2,3]
# Use projection pathway by calling sweep; collect_ledger_metrics will likely fail without network, but we still test call structure
try:
    sweep = al.run_tps_latency_sweep(base_dir, rates, counts)
except Exception as e:
    sweep = {1:[{'arrival':r,'tps':0.0,'lat':0.0} for r in rates],2:[{'arrival':r,'tps':0.0,'lat':0.0} for r in rates],3:[{'arrival':r,'tps':0.0,'lat':0.0} for r in rates]}
ok = al.save_tps_latency_chart(base_dir, sweep)
print('OK' if ok else 'FAIL')
print(os.path.join(base_dir,'output','charts','chart6_tps_latency_multi.png'), os.path.exists(os.path.join(base_dir,'output','charts','chart6_tps_latency_multi.png')))
print(os.path.join(base_dir,'output','charts','chart6_tps_latency_multi.txt'), os.path.exists(os.path.join(base_dir,'output','charts','chart6_tps_latency_multi.txt')))
PY 