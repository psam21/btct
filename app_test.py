#!/usr/bin/env python3
"""Test actual app functionality by importing and running components"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit to prevent actual UI rendering during test
class MockStreamlit:
    def set_page_config(self, **kwargs): pass
    def title(self, text): print(f"TITLE: {text}")
    def header(self, text): print(f"HEADER: {text}")
    def write(self, text): print(f"WRITE: {text}")
    def error(self, text): print(f"ERROR: {text}")
    def success(self, text): print(f"SUCCESS: {text}")
    def dataframe(self, df): print(f"DATAFRAME: {len(df)} rows")
    def sidebar(self): return self
    def selectbox(self, label, options): return options[0] if options else None
    def button(self, label): return False
    def empty(self): return self
    
# Replace streamlit with mock
sys.modules['streamlit'] = MockStreamlit()

print("=== APP COMPONENT TEST ===")

# Test app components
try:
    print("1. Testing main app...")
    import app
    print("   ✅ App module imports successfully")
    
    # Test if we can call main without streamlit runtime
    print("2. Testing app main function...")
    app.main()
    print("   ✅ App main function runs without errors")
    
except Exception as e:
    print(f"   ❌ App test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== APP COMPONENT TEST COMPLETE ===")
