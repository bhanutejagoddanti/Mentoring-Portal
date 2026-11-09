#!/usr/bin/env python3
"""Unified backend test runner.

Runs every feature test across the entire backend in a fixed order and prints
a live, color-coded PASS/FAIL/SKIP report plus a final summary.

Usage (from backend/):
    python tests/run_all_tests.py

Sections (organized execution order):
  1. Backend configuration and health
  2. Database and Supabase connectivity
  3. Authentication and authorization
  4. Common functionality
  5. Student features
  6. Mentor features
  7. Admin features
  8. Complete end-to-end workflows

Unit, API-integration, database, role/permission and E2E tests are all
executed through pytest internally; this runner only orchestrates discovery,
ordering, live reporting, failure details and the final summary.
Existing test modules are preserved (see SECTION_FILES) and discovered, never deleted.
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
TESTS = BACKEND / 'tests'
sys.path.insert(0, str(BACKEND))

# Organized execution order -> existing files (no duplicated test logic).
SECTIONS: list[tuple[str, list[str]]] = [
    ('Backend configuration and health', ['tests/test_auth.py::test_health_open', 'tests/test_auth.py::test_auth_health_open', 'tests/common/test_database.py::test_config_present']),
    ('Database and Supabase connectivity', ['tests/common/test_database.py']),
    ('Authentication and authorization', ['tests/test_auth.py', 'tests/test_authorization.py', 'tests/common/test_auth.py', 'tests/admin/test_authorization.py']),
    ('Common functionality', ['tests/test_utils.py', 'tests/test_communities.py', 'tests/test_help.py', 'tests/common/test_notifications.py']),
    ('Student features', ['tests/student/test_profile.py', 'tests/student/test_mentor_search.py', 'tests/student/test_mentorship.py', 'tests/test_mentorship.py']),
    ('Mentor features', ['tests/mentor/test_profile.py', 'tests/mentor/test_mentoring.py']),
    ('Admin features', ['tests/admin/test_dashboard.py', 'tests/admin/test_matching.py', 'tests/test_authorization.py', 'tests/test_help.py::test_help_routes_registered']),
    ('Complete end-to-end workflows', ['tests/test_e2e.py']),
]

# Fallback discovery: every test_*.py under tests/ (used to catch unlisted files).
def discover_all() -> list[str]:
    return sorted(str(p.relative_to(BACKEND)) for p in TESTS.rglob('test_*.py'))

GREEN, RED, YELLOW, RESET, BOLD = '\033[32m', '\033[31m', '\033[33m', '\033[0m', '\033[1m'


def run_pytest_selectors(selectors: list[str]) -> tuple[list[dict], float]:
    """Run pytest for selectors and return structured results from junitxml."""
    import subprocess
    tmp = tempfile.NamedTemporaryFile(suffix='.xml', delete=False)
    tmp_path = tmp.name
    tmp.close()
    cmd = [sys.executable, '-m', 'pytest', '-p', 'no:cacheprovider',
           '-o', 'addopts=', '--tb=short', '--junitxml', tmp_path, *selectors]
    started = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    elapsed = time.time() - started
    results: list[dict] = []
    try:
        tree = ET.parse(tmp_path)
        for tc in tree.getroot().iter('testcase'):
            name = f"{tc.get('classname', '')}::{tc.get('name', '')}".lstrip(':')
            t = float(tc.get('time', '0') or 0)
            failure = tc.find('failure')
            error = tc.find('error')
            skipped = tc.find('skipped')
            if failure is not None:
                results.append({'name': name, 'status': 'FAIL', 'time': t,
                                'detail': (failure.text or failure.get('message', ''))[:2000],
                                'expected': 'assertion holds (see error below)',
                                'actual': 'assertion failed (see error below)'})
            elif error is not None:
                results.append({'name': name, 'status': 'FAIL', 'time': t,
                                'detail': (error.text or error.get('message', ''))[:2000],
                                'expected': 'test completes without error',
                                'actual': 'exception raised (see error below)'})
            elif skipped is not None:
                results.append({'name': name, 'status': 'SKIP', 'time': t,
                                'detail': (skipped.text or skipped.get('message', 'skipped'))[:500]})
            else:
                results.append({'name': name, 'status': 'PASS', 'time': t})
        if not results and proc.returncode not in (0, 1):
            results.append({'name': 'pytest invocation', 'status': 'FAIL', 'time': elapsed,
                            'detail': (proc.stdout + proc.stderr)[-2000:],
                            'expected': 'pytest runs successfully', 'actual': f'exit code {proc.returncode}'})
    except Exception as exc:  # pragma: no cover
        results.append({'name': 'pytest result parsing', 'status': 'FAIL', 'time': elapsed,
                        'detail': str(exc), 'expected': 'junitxml produced', 'actual': 'parse failed'})
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    return results, elapsed


def main() -> int:
    print(f'{BOLD}BACKEND TEST RUNNER — IITM BS Mentoring Portal{RESET}')
    print(f'backend: {BACKEND}')
    discovered = discover_all()
    print(f'discovered test modules: {len(discovered)}')

    seen_files: set[str] = set()
    for section, selectors in SECTIONS:
        for sel in selectors:
            seen_files.add(sel.split('::')[0])

    all_results: list[dict] = []
    grand_started = time.time()
    for section, selectors in SECTIONS:
        print(f'\n{BOLD}--- {section} ---{RESET}')
        results, _ = run_pytest_selectors(selectors)
        for r in results:
            color = GREEN if r['status'] == 'PASS' else (RED if r['status'] == 'FAIL' else YELLOW)
            print(f"[{r['status']}] {r['name']} ({r['time']:.2f}s)")
            if r['status'] == 'FAIL':
                print(f"{color}  expected: {r.get('expected', '-')}{RESET}")
                print(f"{color}  actual:   {r.get('actual', '-')}{RESET}")
                print(f"{color}  error:    {r.get('detail', '')[:1200]}{RESET}")
            elif r['status'] == 'SKIP':
                print(f"{color}  skip: {r.get('detail', '')[:300]}{RESET}")
        all_results.extend(results)

    # Discover any test files not listed in sections (no silent omissions).
    unlisted = [f for f in discovered if f.replace('tests/', 'tests/') not in seen_files and not any(f == s.split('::')[0] for s in seen_files)]
    if unlisted:
        print(f'\n{BOLD}--- Discovered (not in sections) ---{RESET}')
        results, _ = run_pytest_selectors(unlisted)
        for r in results:
            color = GREEN if r['status'] == 'PASS' else (RED if r['status'] == 'FAIL' else YELLOW)
            print(f"[{r['status']}] {r['name']} ({r['time']:.2f}s)")
        all_results.extend(results)

    total = len(all_results)
    passed = sum(1 for r in all_results if r['status'] == 'PASS')
    failed = total - passed - sum(1 for r in all_results if r['status'] == 'SKIP')
    skipped = sum(1 for r in all_results if r['status'] == 'SKIP')
    rate = (passed / total * 100) if total else 0
    elapsed_total = time.time() - grand_started

    print('\n====================================')
    print('BACKEND TEST SUMMARY')
    print('====================================')
    print(f'Total Tests: {total}')
    print(f'Passed: {passed}')
    print(f'Failed: {failed}')
    print(f'Skipped: {skipped}')
    print(f'Success Rate: {rate:.1f}%')
    print(f'Elapsed: {elapsed_total:.1f}s')
    print('====================================')
    failures = [r for r in all_results if r['status'] == 'FAIL']
    if failures:
        print(f'\n{BOLD}FAILURES ({len(failures)}){RESET}')
        for r in failures:
            print(f"{RED}- {r['name']}{RESET}")
            print(f"  expected: {r.get('expected', '-')}")
            print(f"  actual:   {r.get('actual', '-')}")
            print(f"  error:    {r.get('detail', '')[:800]}")
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
