import json
import logging
from pathlib import Path
from typing import List

from config import RESULTS_DIR
from models import QAAgentState, TestCase, TestResult

logger = logging.getLogger(__name__)

def save_results(state: QAAgentState):
    """Save all results to files"""
    
    # Save test cases
    save_test_cases(state['test_cases'])
    
    # Save scripts
    save_scripts(state['playwright_scripts'])
    
    # Save test results
    save_test_results(state['test_results'], state.get('recruter_test_result'))
    
    # Save report
    save_report(state['summary_report'])
    
    logger.info("💾 All results saved to test_results/ directory")

def save_test_cases(test_cases: List[TestCase]):
    """Save test cases to JSON file"""
    with open(RESULTS_DIR / "test_cases.json", "w") as f:
        test_cases_dict = [tc.to_dict() for tc in test_cases]
        json.dump(test_cases_dict, f, indent=2)

def save_scripts(scripts: List[str]):
    """Save Playwright scripts to JSON file"""
    with open(RESULTS_DIR / "playwright_scripts.json", "w") as f:
        scripts_data = [{"content": script} for script in scripts]
        json.dump(scripts_data, f, indent=2)

def save_test_results(test_results: List[TestResult], recruter_result: TestResult = None):
    """Save test results to JSON file"""
    all_results = test_results.copy()
    if recruter_result:
        all_results.append(recruter_result)
    
    with open(RESULTS_DIR / "test_results.json", "w") as f:
        results_dict = [result.to_dict() for result in all_results]
        json.dump(results_dict, f, indent=2)

def save_report(report: str):
    """Save report to markdown file"""
    with open(RESULTS_DIR / "report.md", "w") as f:
        f.write(report)

def load_test_cases() -> List[TestCase]:
    """Load test cases from JSON file"""
    test_cases_file = RESULTS_DIR / "test_cases.json"
    if not test_cases_file.exists():
        return []
    
    with open(test_cases_file, "r") as f:
        test_cases_data = json.load(f)
    
    return [TestCase.from_dict(tc_data) for tc_data in test_cases_data]

def load_test_results() -> List[TestResult]:
    """Load test results from JSON file"""
    results_file = RESULTS_DIR / "test_results.json"
    if not results_file.exists():
        return []
    
    with open(results_file, "r") as f:
        results_data = json.load(f)
    
    return [TestResult.from_dict(result_data) for result_data in results_data]

def print_statistics(test_results: List[TestResult], recruter_result: TestResult = None):
    """Print test execution statistics"""
    all_results = test_results.copy()
    if recruter_result:
        all_results.append(recruter_result)
    
    total_tests = len(all_results)
    passed_tests = len([r for r in all_results if r.status == "passed"])
    failed_tests = len([r for r in all_results if r.status == "failed"])
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    logger.info("=" * 60)
    logger.info("📊 Test Execution Statistics")
    logger.info("=" * 60)
    logger.info(f"   Total Tests: {total_tests}")
    logger.info(f"   Passed: {passed_tests}")
    logger.info(f"   Failed: {failed_tests}")
    logger.info(f"   Pass Rate: {pass_rate:.1f}%")
    
    if recruter_result:
        logger.info(f"\n🎯 Recruter.ai Workflow Status: {recruter_result.status.upper()}")
        logger.info(f"   Duration: {recruter_result.duration:.2f} seconds")
        if recruter_result.error_message:
            logger.error(f"   Error: {recruter_result.error_message}")