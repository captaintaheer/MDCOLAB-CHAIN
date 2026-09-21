from secretsharing import SecretSharer  # Install: pip3 install secretsharing
import json

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