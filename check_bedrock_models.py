#!/usr/bin/env python3
"""Check which Bedrock models from pricing.csv you're authorized to use."""
import csv
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

try:
    import boto3
except ImportError:
    print("boto3 required: pip install boto3", file=sys.stderr)
    sys.exit(1)

# Load .env from ShinkaEvolve root (credentials for Bedrock)
root = Path(__file__).resolve().parent
load_dotenv(root / ".env", override=True)

pricing_path = root / "shinka/llm/providers/pricing.csv"
if not pricing_path.exists():
    print(f"pricing.csv not found at {pricing_path}", file=sys.stderr)
    sys.exit(1)

bedrock_models = []
with open(pricing_path) as f:
    for row in csv.DictReader(f):
        if row["provider"] == "bedrock":
            bedrock_models.append(row["model_name"])

if not bedrock_models:
    print("No bedrock models in pricing.csv", file=sys.stderr)
    sys.exit(1)

region = os.environ.get("AWS_REGION_NAME", "us-east-1")
client = boto3.client("bedrock", region_name=region)

print(f"Checking {len(bedrock_models)} Bedrock models (region: {region})\n")
print(f"{'Model':<55} {'Status'}")
print("-" * 70)

authorized = []
for model_id in bedrock_models:
    try:
        resp = client.get_foundation_model_availability(modelId=model_id)
        auth = resp.get("authorizationStatus", "?")
        if auth == "AUTHORIZED":
            authorized.append(model_id)
        print(f"{model_id:<55} {auth}")
    except Exception as e:
        print(f"{model_id:<55} ERROR: {e}")

print("-" * 70)
print(f"\nAuthorized: {len(authorized)} / {len(bedrock_models)}")
if authorized:
    print("\nAuthorized models:")
    for m in authorized:
        print(f"  - {m}")
