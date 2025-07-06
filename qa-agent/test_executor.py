import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from playwright.async_api import async_playwright

from config import BROWSER_CONFIG, SCREENSHOTS_DIR
from models import TestCase, TestResult

logger = logging.getLogger(__name__)

class TestExecutor:
    """Executes Playwright tests and captures results"""
    
    def __init__(self):
        self.screenshots_dir = SCREENSHOTS_DIR
        self.browser_config = BROWSER_CONFIG
    
    async def execute_test(self, test_case: TestCase, script: str) -> TestResult:
        """Execute a single test case"""
        start_time = datetime.now()
        test_result = TestResult(
            test_case_id=test_case.id,
            test_name=test_case.name,
            status="passed",
            duration=0,
            timestamp=start_time.isoformat()
        )
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.browser_config["headless"])
            context = await browser.new_context(
                viewport=self.browser_config["viewport"]
            )
            page = await context.new_page()
            
            try:
                # Execute test steps
                for step in test_case.steps:
                    await self._execute_step(page, step)
                
                # Take success screenshot
                screenshot_path = self.screenshots_dir / f"{test_case.id}_success.png"
                await page.screenshot(path=str(screenshot_path))
                test_result.screenshot_path = str(screenshot_path)
                
            except Exception as e:
                test_result.status = "failed"
                test_result.error_message = str(e)
                
                # Take failure screenshot
                screenshot_path = self.screenshots_dir / f"{test_case.id}_failure.png"
                await page.screenshot(path=str(screenshot_path))
                test_result.screenshot_path = str(screenshot_path)
                
                logger.error(f"Test {test_case.name} failed: {e}")
            
            finally:
                await context.close()
                await browser.close()
        
        end_time = datetime.now()
        test_result.duration = (end_time - start_time).total_seconds()
        
        return test_result
    
    async def _execute_step(self, page, step: Dict[str, str]):
        """Execute a single test step"""
        action = step.get('action')
        target = step.get('target')
        data = step.get('data', '')
        
        if action == 'navigate':
            await page.goto(target)
        elif action == 'click':
            await page.click(target)
        elif action == 'fill':
            await page.fill(target, data)
        elif action == 'press':
            await page.press(target, data)
        elif action == 'wait':
            if target == 'networkidle':
                await page.wait_for_load_state('networkidle')
            else:
                await page.wait_for_timeout(int(data))
        elif action == 'assert_text':
            await page.wait_for_selector(f"{target}:has-text('{data}')")
        elif action == 'screenshot':
            await page.screenshot(path=data)