#!/usr/bin/env python3
"""Simple test to check basic functionality"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== BASIC APP HEALTH CHECK ===")

try:
    print("1. Testing Python environment...")
    print("   - Testing requests...")
    import requests
    print("   - Testing pandas...")
    import pandas as pd
    print("   - Testing streamlit...")
    import streamlit as st
    print("   ✅ Basic dependencies work")
except Exception as e:
    print(f"   ❌ Basic dependencies failed: {e}")
    sys.exit(1)

try:
    print("2. Testing local imports...")
    from apis.models import Candlestick
    print("   ✅ APIs module works")
except Exception as e:
    print(f"   ❌ APIs module failed: {e}")

try:
    from logic.signal_engine import SignalEngine
    print("   ✅ Logic module works")
except Exception as e:
    print(f"   ❌ Logic module failed: {e}")

try:
    from ui.components import render_app
    print("   ✅ UI module works")
except Exception as e:
    print(f"   ❌ UI module failed: {e}")

print("\n=== HEALTH CHECK COMPLETE ===")
