#!/usr/bin/env python3
"""
Layer-2: Secure Computation Script
This script reads the secret shares from input files, computes their sum,
and saves the result to an output file for Layer-3.
"""

import os
import json
import hashlib
import argparse

def read_shares(layer2_dir, num_parties=3):
    """
    Read shares from input files in the layer-2 directory.
    """
    shares = []
    for i in range(num_parties):
        file_path = os.path.join(layer2_dir, f"Input-P{i}-0")
        try:
            with open(file_path, 'r') as f:
                share = int(f.read().strip())
                shares.append(share)
                print(f"Read share {i} from {file_path}: {share}")
        except FileNotFoundError:
            print(f"Warning: Input file {file_path} not found")
            return None
        except ValueError:
            print(f"Error: Invalid value in {file_path}")
            return None
    
    return shares

def compute_sum(shares):
    """
    Compute the sum of all shares.
    """
    if shares is None:
        return None
    
    result = sum(shares)
    print(f"Computed sum of shares: {result}")
    return result

def save_result(result, layer2_dir):
    """
    Save the computation result to an output file.
    """
    if result is None:
        print("Error: No result to save")
        return False
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(layer2_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the result
    output_path = os.path.join(output_dir, "result.txt")
    with open(output_path, 'w') as f:
        f.write(str(result))
    print(f"Result saved to {output_path}")
    
    # Generate hash of the result for blockchain
    result_hash = hashlib.sha256(str(result).encode()).hexdigest()
    hash_path = os.path.join(output_dir, "result_hash.txt")
    with open(hash_path, 'w') as f:
        f.write(result_hash)
    print(f"Result hash saved to {hash_path}: {result_hash}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Compute the sum of secret shares")
    parser.add_argument("--parties", type=int, default=3, help="Number of parties (default: 3)")
    args = parser.parse_args()
    
    # Get the directory paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Read shares, compute sum, and save result
    shares = read_shares(current_dir, args.parties)
    result = compute_sum(shares)
    success = save_result(result, current_dir)
    
    if success:
        print("Layer-2 computation completed successfully")
    else:
        print("Layer-2 computation failed")
        exit(1)

if __name__ == "__main__":
    main()