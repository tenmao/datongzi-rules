#!/usr/bin/env python3
"""Development utility script for datongzi-rules."""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests with coverage."""
    print("Running tests with coverage...")
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=src/datongzi_rules",
        "--cov-report=term-missing",
        "--cov-report=html"
    ]
    return subprocess.run(cmd).returncode


def run_unit_tests():
    """Run only unit tests."""
    print("Running unit tests...")
    cmd = [sys.executable, "-m", "pytest", "tests/unit/", "-v"]
    return subprocess.run(cmd).returncode


def run_integration_tests():
    """Run only integration tests."""
    print("Running integration tests...")
    cmd = [sys.executable, "-m", "pytest", "tests/integration/", "-v"]
    return subprocess.run(cmd).returncode


def run_examples():
    """Run all example scripts."""
    print("Running examples...")
    examples_dir = Path("examples")
    
    if not examples_dir.exists():
        print("No examples directory found.")
        return 1
    
    for example in examples_dir.glob("*.py"):
        print(f"\nRunning {example.name}...")
        result = subprocess.run([sys.executable, str(example)])
        if result.returncode != 0:
            print(f"Example {example.name} failed!")
            return 1
    
    return 0


def run_benchmark():
    """Run performance benchmarks."""
    print("Running performance benchmarks...")
    benchmark_file = Path("tests/benchmark/test_performance.py")
    
    if benchmark_file.exists():
        cmd = [sys.executable, "-m", "pytest", str(benchmark_file), "-v"]
        return subprocess.run(cmd).returncode
    else:
        print("No benchmark tests found.")
        return 0


def clean():
    """Clean cache and generated files."""
    print("Cleaning cache and generated files...")
    
    import shutil
    
    patterns = [
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.egg-info",
    ]
    
    for pattern in patterns:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removed {path}")
    
    print("Clean complete!")
    return 0


def check():
    """Run all checks (tests + examples)."""
    print("=" * 60)
    print("Running all checks...")
    print("=" * 60)
    
    # Run tests
    result = run_tests()
    if result != 0:
        print("\n❌ Tests failed!")
        return result
    
    # Run examples
    result = run_examples()
    if result != 0:
        print("\n❌ Examples failed!")
        return result
    
    print("\n" + "=" * 60)
    print("✅ All checks passed!")
    print("=" * 60)
    return 0


def show_help():
    """Show help message."""
    print("""
datongzi-rules development utility

Usage:
    python run.py <command>

Commands:
    test        Run all tests with coverage
    unit        Run only unit tests
    integration Run only integration tests
    examples    Run all example scripts
    benchmark   Run performance benchmarks
    check       Run all checks (tests + examples)
    clean       Clean cache and generated files
    help        Show this help message

Examples:
    python run.py test
    python run.py check
    python run.py clean
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return 1
    
    command = sys.argv[1]
    
    commands = {
        "test": run_tests,
        "unit": run_unit_tests,
        "integration": run_integration_tests,
        "examples": run_examples,
        "benchmark": run_benchmark,
        "check": check,
        "clean": clean,
        "help": show_help,
    }
    
    if command not in commands:
        print(f"Unknown command: {command}")
        show_help()
        return 1
    
    return commands[command]()


if __name__ == "__main__":
    sys.exit(main())
