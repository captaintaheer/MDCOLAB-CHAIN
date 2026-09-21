from mpyc.runtime import mpc
import json
import asyncio
import time
import psutil
import argparse

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_ops", type=int, default=1, help="Number of operations for throughput")
    args = parser.parse_args()

    process = psutil.Process()
    start_mem = process.memory_info().rss / 1024 / 1024  # MB
    peak_mem = start_mem
    start_time = time.perf_counter()

    await mpc.start()

    # Load shares or use hardcoded
    with open("../layer-1/shares.json", "r") as f:
        shares_data = json.load(f)["shares"]
    # Convert to secure ints (assuming shares are integers)
    inputs = [mpc.SecInt()(int(share.split('-')[1])) for share in shares_data]

    results = []
    for _ in range(args.num_ops):
        result = sum(inputs)
        results.append(await mpc.output(result))
        # Track peak memory during ops
        current_mem = process.memory_info().rss / 1024 / 1024
        if current_mem > peak_mem:
            peak_mem = current_mem

    m = len(mpc.parties)
    nbytes = [peer.protocol.nbytes_sent if peer.pid != mpc.pid else 0 for peer in mpc.parties]
    comm_bytes = sum(nbytes)
    comm_rounds = args.num_ops

    await mpc.shutdown()

    end_time = time.perf_counter()
    execution_time = end_time - start_time
    throughput = args.num_ops / execution_time if execution_time > 0 else 0
    latency = execution_time  # end-to-end

    print(f"Execution Time: {execution_time:.4f} seconds")
    print(f"Peak RAM Usage: {peak_mem:.2f} MB")
    print(f"Throughput: {throughput:.2f} ops/sec")
    print(f"Latency: {latency:.4f} seconds")
    print(f"Comm Rounds: {comm_rounds}")
    print(f"Comm Volume Bytes: {comm_bytes}")
    print("Results:", results)

if __name__ == "__main__":
    mpc.run(main())
