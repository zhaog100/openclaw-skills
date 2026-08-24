#!/usr/bin/env python3
"""
Public APIs Test Script - Stage 1 Material Optimization
Test Poof (Background Removal) and ShotOG (Cover Generation)
"""

import os
import time
from pathlib import Path

# Check Poof SDK
try:
    from poof import Poof
    POOF_AVAILABLE = True
except ImportError:
    POOF_AVAILABLE = False
    print("WARNING: Poof SDK not installed, skipping Poof test")
    print("   Install: pip install --break-system-packages poofbg")

# API Keys (from environment variables)
POOF_API_KEY = os.environ.get("POOF_API_KEY", "pk_b0e81ff5f19266dab29abd9c58eb4141")

# Test config
OUTPUT_DIR = "test_output"
Path(OUTPUT_DIR).mkdir(exist_ok=True)

print("=" * 60)
print("Public APIs Test - Stage 1 Material Optimization")
print("=" * 60)
print()

# ========== Poof API Test ==========
if POOF_AVAILABLE:
    print("Testing Poof API (Background Removal)")
    print("-" * 60)

    # Test image (if exists)
    test_image = "test_input.jpg"

    if not os.path.exists(test_image):
        print(f"WARNING: Test image not found: {test_image}")
        print("   Please prepare a test image (test_input.jpg)")
        print("   Or modify script to use existing image path")
    else:
        try:
            print(f"Processing image: {test_image}")
            print(f"API Key: {POOF_API_KEY[:8]}...{POOF_API_KEY[-4:]}")

            # Initialize client
            client = Poof(api_key=POOF_API_KEY)

            # Remove background
            print("Removing background...")
            result = client.remove(test_image)

            # Save result
            output_path = os.path.join(OUTPUT_DIR, "poof_output.png")
            result.save(output_path)

            print(f"SUCCESS! Output file: {output_path}")
            print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")

        except Exception as e:
            print(f"ERROR: {e}")
            print(f"   Type: {type(e).__name__}")
else:
    print("Skipping Poof test")

print()

# ========== ShotOG API Test ==========
print("Testing ShotOG API (Cover Generation)")
print("-" * 60)

import requests

SHOTOG_API = "https://shotog.2214962083.workers.dev/v1/og"

test_titles = [
    {"title": "Steam Eye Mask 10pcs", "template": "product", "subtitle": "Y15.9"},
    {"title": "Nap Magic", "template": "blog", "author": "Xiaomijiao"},
    {"title": "Limited Offer", "template": "announcement", "subtitle": "Buy 2 Get 1 Free"}
]

for i, params in enumerate(test_titles, 1):
    try:
        print(f"Generating cover {i}/{len(test_titles)}: {params['title']}")
        print(f"   Template: {params['template']}")

        # GET method (simple)
        params_str = "&".join([f"{k}={v}" for k, v in params.items() if v])
        url = f"{SHOTOG_API}?{params_str}"

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Save result
        output_path = os.path.join(OUTPUT_DIR, f"shotog_{i}.png")
        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"SUCCESS! Output file: {output_path}")
        print(f"File size: {len(response.content) / 1024:.1f} KB")

        # Avoid rate limiting
        if i < len(test_titles):
            print("Waiting 2 seconds...")
            time.sleep(2)

    except Exception as e:
        print(f"ERROR: {e}")
        print(f"   Type: {type(e).__name__}")

print()
print("=" * 60)
print("Test completed!")
print(f"Output directory: {OUTPUT_DIR}")
print("=" * 60)
print()

# ========== Query Account Info ==========
print("Querying account info")
print("-" * 60)

if POOF_AVAILABLE:
    try:
        from poof import Poof
        client = Poof(api_key=POOF_API_KEY)
        account = client.me()

        print(f"Plan: {account.get('plan', 'N/A')}")
        print(f"Max credits: {account.get('max_credits', 0)}")
        print(f"Used credits: {account.get('used_credits', 0)}")
        remaining = account.get('max_credits', 0) - account.get('used_credits', 0)
        print(f"Remaining: {remaining}")
    except Exception as e:
        print(f"WARNING: Poof account query failed: {e}")

print()
