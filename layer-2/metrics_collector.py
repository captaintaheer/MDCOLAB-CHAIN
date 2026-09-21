import subprocess
import json
import time
import psutil
import re

def run_smpc_metrics(num_parties, num_ops=10):
    cmd = ['python', '-m', 'mpyc', 'layer2_smpc.py', '--num_ops', str(num_ops), '-M', str(num_parties)]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    output = stdout.decode()
    
    metrics = {}
    patterns = {
        'execution_time': r'Execution Time: (\d+\.\d+) seconds',
        'peak_ram': r'Peak RAM Usage: (\d+\.\d+) MB',
        'throughput': r'Throughput: (\d+\.\d+) ops/sec',
        'latency': r'Latency: (\d+\.\d+) seconds'
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            metrics[key] = float(match.group(1))
    return metrics

def run_non_secure_metrics(num_ops=10):
    process = psutil.Process()
    start_mem = process.memory_info().rss / 1024 / 1024
    peak_mem = start_mem
    start_time = time.perf_counter()
    
    with open("../layer-1/shares.json", "r") as f:
        shares_data = json.load(f)["shares"]
    inputs = [int(share.split('-')[1]) for share in shares_data]
    
    results = []
    for _ in range(num_ops):
        result = sum(inputs)
        results.append(result)
        current_mem = process.memory_info().rss / 1024 / 1024
        if current_mem > peak_mem:
            peak_mem = current_mem
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    throughput = num_ops / execution_time if execution_time > 0 else 0
    latency = execution_time
    
    return {
        'execution_time': execution_time,
        'peak_ram': peak_mem,
        'throughput': throughput,
        'latency': latency
    }

if __name__ == "__main__":
    party_counts = [2, 3]
    num_ops = 1
    results = {}
    
    print("Collecting non-secure metrics...")
    non_secure = run_non_secure_metrics(num_ops)
    results['non_secure'] = non_secure
    
    for parties in party_counts:
        print(f"Collecting metrics for {parties} parties...")
        metrics = run_smpc_metrics(parties, num_ops)
        results[f'parties_{parties}'] = metrics
    
    # Calculate privacy overhead
    for parties in party_counts:
        smpc = results[f'parties_{parties}']
        overhead = {}
        for key in smpc:
            if key in non_secure:
                overhead[key] = smpc[key] / non_secure[key] if non_secure[key] > 0 else 0
        results[f'overhead_{parties}'] = overhead
    
    with open('metrics_results.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("Results saved to metrics_results.json")