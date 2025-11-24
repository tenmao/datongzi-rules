#!/usr/bin/env python3
"""
Cross-language test runner.

This script runs tests against both Python and Rust implementations
and compares the results to ensure consistency.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add python src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python" / "src"))

from datongzi_rules import Card, Rank, Suit, Deck, GameConfig


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_success(msg: str) -> None:
    """Print success message in green."""
    print(f"{Colors.GREEN}✓{Colors.ENDC} {msg}")


def print_error(msg: str) -> None:
    """Print error message in red."""
    print(f"{Colors.RED}✗{Colors.ENDC} {msg}")


def print_info(msg: str) -> None:
    """Print info message in blue."""
    print(f"{Colors.BLUE}ℹ{Colors.ENDC} {msg}")


def load_test_cases() -> Dict[str, Any]:
    """Load test cases from JSON file."""
    test_file = Path(__file__).parent / "test_cases.json"
    with open(test_file, 'r') as f:
        return json.load(f)


def run_python_tests(test_cases: Dict[str, Any]) -> Dict[str, Any]:
    """Run tests using Python implementation."""
    print_info("Running Python tests...")
    results = {}

    # Test card basics
    for suite in test_cases['test_suites'].get('card_basics', []):
        suite_results = []
        for test_case in suite['tests']:
            test_id = test_case['id']
            try:
                if 'card1' in test_case['input']:
                    # Card comparison test
                    c1_data = test_case['input']['card1']
                    c2_data = test_case['input']['card2']
                    card1 = Card(
                        Suit[c1_data['suit']],
                        Rank[c2_data['rank'].upper()]
                    )
                    card2 = Card(
                        Suit[c2_data['suit']],
                        Rank[c2_data['rank'].upper()]
                    )
                    result = {
                        'card1_greater': card1 > card2
                    }
                else:
                    # Single card test
                    card_data = test_case['input']
                    card = Card(
                        Suit[card_data['suit']],
                        Rank[card_data['rank'].upper()]
                    )
                    result = {
                        'is_scoring_card': card.is_scoring_card,
                        'score_value': card.score_value
                    }

                suite_results.append({
                    'test_id': test_id,
                    'passed': result == test_case['expected'],
                    'result': result,
                    'expected': test_case['expected']
                })
            except Exception as e:
                suite_results.append({
                    'test_id': test_id,
                    'passed': False,
                    'error': str(e)
                })

        results[suite['name']] = suite_results

    # Test deck operations
    for suite in test_cases['test_suites'].get('deck_operations', []):
        suite_results = []
        for test_case in suite['tests']:
            test_id = test_case['id']
            try:
                num_decks = test_case['input']['num_decks']
                deck = Deck.create_standard_deck(num_decks)
                result = {'card_count': len(deck.cards)}

                suite_results.append({
                    'test_id': test_id,
                    'passed': result == test_case['expected'],
                    'result': result,
                    'expected': test_case['expected']
                })
            except Exception as e:
                suite_results.append({
                    'test_id': test_id,
                    'passed': False,
                    'error': str(e)
                })

        results[suite['name']] = suite_results

    # Test config validation
    for suite in test_cases['test_suites'].get('config_validation', []):
        suite_results = []
        for test_case in suite['tests']:
            test_id = test_case['id']
            try:
                config = GameConfig(**test_case['input'])
                try:
                    config.validate()
                    result = {'is_valid': True}
                except Exception as e:
                    result = {
                        'is_valid': False,
                        'error': str(e)
                    }

                # Check if result matches expected
                passed = result['is_valid'] == test_case['expected']['is_valid']
                if not passed and 'error_contains' in test_case['expected']:
                    passed = test_case['expected']['error_contains'] in result.get('error', '')

                suite_results.append({
                    'test_id': test_id,
                    'passed': passed,
                    'result': result,
                    'expected': test_case['expected']
                })
            except Exception as e:
                suite_results.append({
                    'test_id': test_id,
                    'passed': False,
                    'error': str(e)
                })

        results[suite['name']] = suite_results

    return results


def run_rust_tests(test_cases: Dict[str, Any]) -> Dict[str, Any]:
    """Run tests using Rust implementation."""
    print_info("Running Rust tests...")
    print_info("Note: Rust tests will be implemented in Phase 2+")
    # Placeholder - will be implemented when Rust code is complete
    return {}


def compare_results(python_results: Dict[str, Any], rust_results: Dict[str, Any]) -> bool:
    """Compare Python and Rust results."""
    print(f"\n{Colors.BOLD}Test Results Summary{Colors.ENDC}")
    print("=" * 60)

    total_tests = 0
    passed_tests = 0

    for suite_name, suite_results in python_results.items():
        print(f"\n{Colors.BOLD}{suite_name}{Colors.ENDC}")
        for test_result in suite_results:
            total_tests += 1
            test_id = test_result['test_id']

            if test_result['passed']:
                passed_tests += 1
                print_success(f"{test_id}")
            else:
                print_error(f"{test_id}")
                if 'error' in test_result:
                    print(f"  Error: {test_result['error']}")
                else:
                    print(f"  Expected: {test_result['expected']}")
                    print(f"  Got:      {test_result['result']}")

    print(f"\n{Colors.BOLD}Summary{Colors.ENDC}")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        print_success(f"\nAll {total_tests} tests passed!")
        return True
    else:
        print_error(f"\n{total_tests - passed_tests} tests failed")
        return False


def main() -> int:
    """Main entry point."""
    print(f"{Colors.BOLD}Cross-Language Consistency Tests{Colors.ENDC}")
    print("=" * 60)

    try:
        # Load test cases
        test_cases = load_test_cases()
        print_info(f"Loaded {len(test_cases['test_suites'])} test suites")

        # Run Python tests
        python_results = run_python_tests(test_cases)

        # Save Python results
        results_file = Path(__file__).parent / "results_python.json"
        with open(results_file, 'w') as f:
            json.dump(python_results, f, indent=2)
        print_info(f"Python results saved to {results_file}")

        # Run Rust tests (placeholder)
        rust_results = run_rust_tests(test_cases)

        # Compare results
        all_passed = compare_results(python_results, rust_results)

        return 0 if all_passed else 1

    except Exception as e:
        print_error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
