import json
import sys

try:
    from secretsharing import SecretSharer  # Install: pip install secretsharing
except ImportError:
    sys.exit("layer1_data_input.py requires the 'secretsharing' package (SecretSharer), which is not installed. "
             "Its PyPI release (0.2.6) supports Python 2 only; "
             "the pipeline itself uses layer-1/generate_shares.py and does not depend on it.")
except NameError:
    # secretsharing 0.2.6 (the PyPI release) uses Python 2 builtins such as `long` at import time
    sys.exit("The installed 'secretsharing' package does not support Python 3 (it fails on import). "
             "layer1_data_input.py needs a Python 3 compatible 'secretsharing'; "
             "the pipeline itself uses layer-1/generate_shares.py and does not depend on it.")

# Simulate tiny genomic data (e.g., allele counts for 3 patients)
data = {"patient1": 5, "patient2": 3, "patient3": 7}  # Simple integers for PoC

# Encrypt with Shamir's Secret Sharing (3 shares, 2 needed to reconstruct)
shares = SecretSharer.split_secret(str(sum(data.values())), 2, 3)

# Tag with metadata
metadata = {
    "data_id": "genomic_001",
    "consent": True,
    "timestamp": "2025-02-22",
    "shares": shares
}

# Save encrypted shares and metadata
with open("shares.json", "w") as f:
    json.dump(metadata, f)

print("Layer 1: Data encrypted and tagged:", shares)