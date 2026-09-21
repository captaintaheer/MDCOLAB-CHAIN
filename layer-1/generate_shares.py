#!/usr/bin/env python3
"""
Layer-1: Secret Sharing Script
This script takes a numeric input value, splits it into additive secret shares,
and saves them to the input files for Layer-2.
"""

import json
import os
import random
import argparse
from datetime import datetime

def generate_shares(value, num_shares=3):
    """
    Generate additive secret shares for a given value.
    The sum of all shares equals the original value.
    """
    # Generate random shares for all but the last one
    shares = [random.randint(1, 10) for _ in range(num_shares - 1)]
    
    # Calculate the last share so the sum equals the original value
    last_share = value - sum(shares)
    shares.append(last_share)
    
    return shares

def save_shares_to_files(shares, layer2_dir):
    """
    Save each share to its corresponding input file in layer-2 directory.
    """
    for i, share in enumerate(shares):
        file_path = os.path.join(layer2_dir, f"Input-P{i}-0")
        with open(file_path, 'w') as f:
            f.write(str(share))
        print(f"Share {i} saved to {file_path}: {share}")

def update_shares_json(data_id, layer1_dir):
    """
    Update the shares.json file with metadata about the shares.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d")
    shares_data = {
        "data_id": data_id,
        "consent": True,
        "timestamp": timestamp,
        "shares": [f"{i+1}-{random.randint(1, 20)}" for i in range(3)]
    }
    
    json_path = os.path.join(layer1_dir, "shares.json")
    with open(json_path, 'w') as f:
        json.dump(shares_data, f)
    print(f"Shares metadata saved to {json_path}")

def compute_gc_count(fasta_path):
    gc_count = 0
    with open(fasta_path, 'r') as f:
        for line in f:
            if line.startswith('>'):
                continue
            u = line.strip().upper()
            gc_count += u.count('G')
            gc_count += u.count('C')
    return gc_count

def main():
    parser = argparse.ArgumentParser(description="Generate secret shares for secure multi-party computation")
    parser.add_argument("--data-id", type=str, default="genomic_001", help="Data identifier (default: genomic_001)")
    args = parser.parse_args()
    
    # Get the directory paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    layer2_dir = os.path.join(base_dir, "layer-2")
    genome_path = os.path.join(base_dir, "data/genome.fna")
    
    # Compute statistic from genomic data
    value = compute_gc_count(genome_path)
    
    # Generate and save shares
    shares = generate_shares(value)
    save_shares_to_files(shares, layer2_dir)
    
    # Update shares.json
    update_shares_json(args.data_id, current_dir)
    
    print(f"Secret sharing complete. Computed GC count: {value}, Sum of shares: {sum(shares)}")

if __name__ == "__main__":
    main()
