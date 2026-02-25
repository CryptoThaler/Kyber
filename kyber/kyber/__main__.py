"""KYBER CLI"""
import asyncio, sys

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        import subprocess
        subprocess.run([sys.executable, "examples/demo_basic.py"])
    else:
        print("KYBER Cybernetic Agent OS v1.0.0")
        print("Usage: kyber demo")

if __name__ == "__main__":
    main()
