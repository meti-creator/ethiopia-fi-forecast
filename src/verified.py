"""
Verification script for Ethiopia FI Dashboard
Run this before streamlit to check everything is set up correctly.
"""
import sys

def check():
    print("="*50)
    print("ETHIOPIA FI DASHBOARD - SETUP CHECK")
    print("="*50)

    # Check Python version
    print(f"\nPython version: {sys.version}")

    # Check required packages
    packages = ['streamlit', 'plotly', 'pandas', 'numpy']
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"  [{pkg}] OK")
        except ImportError:
            print(f"  [{pkg}] MISSING - run: py -m pip install {pkg}")

    print("\n" + "="*50)
    print("If all packages show OK, you can run:")
    print("  py -m streamlit run app.py")
    print("="*50)

if __name__ == "__main__":
    check()