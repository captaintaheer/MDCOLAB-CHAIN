#!/usr/bin/env python3
"""TPS/latency sweep on the Hyperledger Fabric test network.

For each endorser count and arrival rate, submits CreateAsset transactions through the `peer` CLI
using the ledger functions in automate_layers.py (run_tps_latency_sweep), then writes
output/charts/chart6_tps_latency_multi.{png,txt} and output/charts/chart2_dual_axis_tps_latency_bars.png.

Requirements: the test network is up with the `basic` chaincode deployed (see layer-3/README.md), and
layer-2/output/result_hash.txt exists (run automate_layers.py or layer-2/compute_sum.py first).

Usage:
    python tps.py [--rates 50,100,150,200,250] [--endorser_counts 1,2,3] [--concurrency 16]
"""
import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
import automate_layers as al  # noqa: E402


def _int_list(s):
    return [int(x) for x in s.split(',') if x.strip()]


def main():
    ap = argparse.ArgumentParser(description="TPS/latency sweep on the Fabric test network")
    ap.add_argument('--rates', type=_int_list, default=[50, 100, 150, 200, 250],
                    help='comma-separated arrival rates (default: 50,100,150,200,250)')
    ap.add_argument('--endorser_counts', type=_int_list, default=[1, 2, 3],
                    help='comma-separated endorser counts (default: 1,2,3)')
    ap.add_argument('--concurrency', type=int, default=16, help='maximum concurrent invokes (default: 16)')
    args = ap.parse_args()

    problems = al.check_fabric(BASE_DIR, need_script=False)
    hash_file = os.path.join(BASE_DIR, 'layer-2', 'output', 'result_hash.txt')
    if not os.path.exists(hash_file):
        problems.append(f"{os.path.relpath(hash_file, BASE_DIR)} not found "
                        "(run automate_layers.py or layer-2/compute_sum.py first)")
    if problems:
        print("Cannot run the TPS sweep:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print("See layer-3/README.md for the Fabric setup. No output was written.", file=sys.stderr)
        return 1

    sweep = al.run_tps_latency_sweep(BASE_DIR, args.rates, args.endorser_counts, concurrency=args.concurrency)
    if all(d['tps'] == 0.0 for points in sweep.values() for d in points):
        print("No transaction succeeded in the sweep (is the test network up and the `basic` chaincode "
              "deployed on mychannel?). No output was written.", file=sys.stderr)
        return 1

    for c in sorted(sweep):
        for d in sweep[c]:
            print(f"peers {c} arrival {d['arrival']} tps {d['tps']:.2f} latency_s {d['lat']:.3f}")

    out_dir = os.path.join(BASE_DIR, 'output', 'charts')
    ok = al.save_tps_latency_chart(BASE_DIR, sweep)
    ok_bars = al.save_tps_latency_bar_chart(BASE_DIR, sweep)
    for name in ['chart6_tps_latency_multi.png', 'chart6_tps_latency_multi.txt',
                 'chart2_dual_axis_tps_latency_bars.png']:
        path = os.path.join(out_dir, name)
        print(os.path.relpath(path, BASE_DIR), 'written' if os.path.exists(path) else 'missing')
    return 0 if (ok and ok_bars) else 1


if __name__ == '__main__':
    sys.exit(main())
