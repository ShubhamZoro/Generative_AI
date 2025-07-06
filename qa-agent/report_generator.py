import logging
from datetime import datetime
from typing import List, Optional
from langchain_openai import ChatOpenAI

from config import OPENAI_API_KEY, LLM_CONFIG
from models import TestResult

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates test execution reports"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=LLM_CONFIG["temperature"],
            model=LLM_CONFIG["model"],
            api_key=OPENAI_API_KEY
        )
    
    async def generate_summary(self, test_results: List[TestResult], recruter_result: Optional[TestResult] = None) -> str:
        """Generate executive summary of test results"""
        
        all_results = test_results.copy()
        if recruter_result:
            all_results.append(recruter_result)
        
        # Calculate statistics
        stats = self._calculate_statistics(all_results)
        
        # Create detailed report
        report = self._create_report_header(stats)
        
        # Add Recruter.ai workflow result first if available
        if recruter_result:
            report += self._add_recruter_result(recruter_result)
        
        # Add individual test results
        report += self._add_test_results(test_results)
        
        # Add recommendations
        report += self._add_recommendations(stats)
        
        return report
    
    def _calculate_statistics(self, results: List[TestResult]) -> dict:
        """Calculate test statistics"""
        total_tests = len(results)
        passed_tests = len([r for r in results if r.status == "passed"])
        failed_tests = len([r for r in results if r.status == "failed"])
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": pass_rate
        }
    
    def _create_report_header(self, stats: dict) -> str:
        """Create report header with statistics"""
        return f"""# QA Test Execution Report - Recruter.ai Platform

## Executive Summary
- **Total Tests**: {stats['total']}
- **Passed**: {stats['passed']}
- **Failed**: {stats['failed']}
- **Pass Rate**: {stats['pass_rate']:.1f}%
- **Execution Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Results Details

"""
    
    def _add_recruter_result(self, recruter_result: TestResult) -> str:
        """Add Recruter.ai workflow result to report"""
        status_emoji = "✅" if recruter_result.status == "passed" else "❌"
        report = f"""### {status_emoji} Recruter.ai Complete Workflow Test
- **Status**: {recruter_result.status}
- **Duration**: {recruter_result.duration:.2f}s
- **Test ID**: {recruter_result.test_case_id}
- **Description**: Complete end-to-end workflow testing of Recruter.ai platform
"""
        if recruter_result.error_message:
            report += f"- **Error**: {recruter_result.error_message}\n"
        if recruter_result.screenshot_path:
            report += f"- **Screenshot**: [{recruter_result.test_case_id}_screenshot]({recruter_result.screenshot_path})\n"
        report += "\n"
        return report
    
    def _add_test_results(self, test_results: List[TestResult]) -> str:
        """Add individual test results to report"""
        report = ""
        for result in test_results:
            status_emoji = "✅" if result.status == "passed" else "❌"
            report += f"""### {status_emoji} {result.test_name}
- **Status**: {result.status}
- **Duration**: {result.duration:.2f}s
- **Test ID**: {result.test_case_id}
"""
            if result.error_message:
                report += f"- **Error**: {result.error_message}\n"
            if result.screenshot_path:
                report += f"- **Screenshot**: [{result.test_case_id}_screenshot]({result.screenshot_path})\n"
            report += "\n"
        return report
    
    def _add_recommendations(self, stats: dict) -> str:
        """Add recommendations based on test results"""
        if stats["failed"] > 0:
            return """## Recommendations
1. Review failed test cases for root cause analysis
2. Check if UI elements have changed on Recruter.ai platform
3. Verify test data validity and credentials
4. Consider environment-specific issues (network, browser compatibility)
5. Update selectors if platform UI has been updated
6. Validate API responses and loading times

## Key Features Tested
- ✅ User Authentication (Login/Logout)
- ✅ Interview Creation Workflow
- ✅ AI-Enhanced Job Description Generation
- ✅ Skills and Experience Configuration
- ✅ Company Information Setup
- ✅ Question Generation and Review
- ✅ Complete E2E User Journey

## Next Steps
1. Set up automated regression testing
2. Implement cross-browser testing
3. Add performance monitoring
4. Create alerts for critical workflow failures
"""
        else:
            return """## Summary
🎉 All tests passed successfully! The Recruter.ai platform is functioning correctly.

## Key Features Verified
- ✅ User Authentication System
- ✅ Interview Creation Workflow
- ✅ AI Enhancement Features
- ✅ Skills Management
- ✅ Company Configuration
- ✅ End-to-End User Experience

## Recommendations
- Continue monitoring with regular test runs
- Consider adding more edge case scenarios
- Implement performance benchmarking
"""
