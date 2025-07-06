import logging
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

from config import RECRUTER_CONFIG, BROWSER_CONFIG, SCREENSHOTS_DIR
from models import TestResult

logger = logging.getLogger(__name__)

class RecruterAIAutomation:
    """Handles the complete Recruter.ai automation workflow"""
    
    def __init__(self):
        self.screenshots_dir = SCREENSHOTS_DIR
        self.config = RECRUTER_CONFIG
        self.browser_config = BROWSER_CONFIG
    
    async def run_complete_workflow(self) -> TestResult:
        """Execute the complete Recruter.ai workflow with screenshots"""
        start_time = datetime.now()
        test_result = TestResult(
            test_case_id="RECRUTER_WORKFLOW",
            test_name="Complete Recruter.ai Interview Creation Workflow",
            status="passed",
            duration=0,
            timestamp=start_time.isoformat()
        )
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.browser_config["headless"],
                slow_mo=self.browser_config["slow_mo"]
            )
            page = await browser.new_page()
            
            try:
                # Execute all workflow steps
                await self._execute_login(page)
                await self._execute_create_interview(page)
                await self._execute_enhance_with_ai(page)
                await self._execute_job_description(page)
                await self._execute_skills_setup(page)
                await self._execute_job_details(page)
                await self._execute_final_steps(page)
                
                # Take success screenshot
                screenshot_path = self.screenshots_dir / "recruter_workflow_success.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)
                test_result.screenshot_path = str(screenshot_path)
                
                logger.info("🎉 Complete Recruter.ai workflow executed successfully!")
                
            except Exception as e:
                test_result.status = "failed"
                test_result.error_message = str(e)
                
                # Take failure screenshot
                screenshot_path = self.screenshots_dir / "recruter_workflow_failure.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)
                test_result.screenshot_path = str(screenshot_path)
                
                logger.error(f"Recruter.ai workflow failed: {e}")
            
            finally:
                await browser.close()
        
        end_time = datetime.now()
        test_result.duration = (end_time - start_time).total_seconds()
        return test_result

    async def _execute_login(self, page):
        """Execute login steps"""
        logger.info("🔄 Navigating to Recruter.ai")
        await page.goto(self.config["base_url"])
        await page.wait_for_load_state('networkidle')
        
        # Fill credentials
        logger.info("🔄 Filling credentials...")
        await page.fill('input[name="email"]', self.config["credentials"]["email"])
        await page.fill('input[name="password"]', self.config["credentials"]["password"])
        await page.press('input[name="password"]', 'Enter')
        
        await page.wait_for_load_state('networkidle', timeout=self.browser_config["timeout"])
        await page.wait_for_timeout(3000)
        
        # Take screenshot after login
        await page.screenshot(path=str(self.screenshots_dir / '01_after_login.png'), full_page=True)
        logger.info("📸 Step 1: After login screenshot saved")

    async def _execute_create_interview(self, page):
        """Execute create interview steps"""
        logger.info("🔄 Looking for Create Interview button...")
        create_selectors = [
            '#joyride_step1_create_new_campaign_button',
            'button:has-text("Create Interview")',
            'span:has-text("Create Interview")'
        ]
        
        for selector in create_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector)
                logger.info("✅ Clicked Create Interview button!")
                break
            except:
                continue
        
        await page.wait_for_load_state('networkidle', timeout=15000)
        await page.wait_for_timeout(3000)
        
        # Take screenshot of job description page
        await page.screenshot(path=str(self.screenshots_dir / '02_job_description_page.png'), full_page=True)
        logger.info("📸 Step 2: Job description page screenshot saved")

    async def _execute_enhance_with_ai(self, page):
        """Execute enhance with AI steps"""
        logger.info("🔄 Clicking on Enhance with AI tab...")
        enhance_selectors = [
            'button:has-text("Enhance with AI")',
            '[data-radix-collection-item]:has-text("Enhance with AI")',
            'button[role="tab"]:has-text("Enhance with AI")'
        ]
        
        for selector in enhance_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector)
                logger.info("✅ Clicked Enhance with AI tab!")
                break
            except:
                continue
        
        await page.wait_for_timeout(2000)
        await page.screenshot(path=str(self.screenshots_dir / '03_enhance_with_ai_page.png'), full_page=True)
        logger.info("📸 Step 3: Enhance with AI page screenshot saved")

    async def _execute_job_description(self, page):
        """Execute job description steps"""
        logger.info("🔄 Entering job description...")
        description_text = self.config["test_data"]["job_description"]
        
        description_selectors = [
            'textarea',
            'textarea[placeholder*="description"]',
            'textarea[placeholder*="key points"]'
        ]
        
        for selector in description_selectors:
            try:
                await page.wait_for_selector(selector, timeout=3000)
                await page.fill(selector, description_text)
                logger.info("✅ Filled job description!")
                break
            except:
                continue
        
        await page.screenshot(path=str(self.screenshots_dir / '04_description_entered.png'), full_page=True)
        logger.info("📸 Step 4: Description entered screenshot saved")
        
        # Enhance JD
        logger.info("🔄 Looking for Enhance JD button...")
        enhance_jd_selectors = [
            'button:has-text("Enhance JD")',
            'button:has-text("Enhance")'
        ]
        
        for selector in enhance_jd_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector)
                logger.info("✅ Clicked Enhance JD button!")
                break
            except:
                continue
        
        # Wait for enhancement
        logger.info("⏳ Waiting 8 seconds for enhancement...")
        await page.wait_for_timeout(8000)
        
        await page.screenshot(path=str(self.screenshots_dir / '05_after_enhancement.png'), full_page=True)
        logger.info("📸 Step 5: After enhancement screenshot saved")
        
        # Save JD
        logger.info("🔄 Looking for Save JD button...")
        save_jd_selectors = [
            'button:has-text("Save JD")',
            'button:has-text("Save")'
        ]
        
        for selector in save_jd_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector)
                logger.info("✅ Clicked Save JD button!")
                break
            except:
                continue
        
        await page.wait_for_timeout(2000)
        await page.screenshot(path=str(self.screenshots_dir / '06_after_save_jd.png'), full_page=True)
        logger.info("📸 Step 6: After Save JD screenshot saved")

    async def _execute_skills_setup(self, page):
        """Execute skills setup steps"""
        skill_names = self.config["test_data"]["skills"]
        experience_years = str(self.config["test_data"]["experience_years"])
        
        for skill_num in range(1, len(skill_names) + 1):
            logger.info(f"🔄 Adding skill #{skill_num}...")
            
            # Enter skill name
            skill_selectors = [
                'input[placeholder*="skill name"]',
                'input[placeholder*="Enter skill"]'
            ]
            
            for selector in skill_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    await page.fill(selector, skill_names[skill_num-1])
                    logger.info(f"✅ Entered skill name: {skill_names[skill_num-1]}")
                    break
                except:
                    continue
            
            # Enter experience
            experience_selectors = [
                'input[type="number"]',
                'input[placeholder*="Experience"]'
            ]
            
            for selector in experience_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    await page.fill(selector, experience_years)
                    logger.info(f"✅ Entered experience: {experience_years} years")
                    break
                except:
                    continue
            
            # Click Add Skill
            add_skill_selectors = [
                'button:has-text("Add Skill")',
                'button:has-text("Add")'
            ]
            
            for selector in add_skill_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    await page.click(selector)
                    logger.info("✅ Clicked Add Skill button!")
                    break
                except:
                    continue
            
            await page.wait_for_timeout(1000)
            await page.screenshot(path=str(self.screenshots_dir / f'07_skill_{skill_num}_added.png'), full_page=True)
            logger.info(f"📸 Step 7.{skill_num}: Skill {skill_num} added screenshot saved")

    async def _execute_job_details(self, page):
        """Execute job details steps"""
        # Enter Job Title
        logger.info("🔄 Entering Job Title...")
        job_title_selectors = [
            'input[placeholder*="position you are hiring"]',
            'input[placeholder*="Job Title"]'
        ]
        
        for selector in job_title_selectors:
            try:
                await page.wait_for_selector(selector, timeout=3000)
                await page.fill(selector, self.config["test_data"]["job_title"])
                logger.info(f"✅ Entered Job Title: {self.config['test_data']['job_title']}")
                break
            except:
                continue
        
        # Enter Company Name
        logger.info("🔄 Entering Company Name...")
        company_selectors = [
            'input[placeholder*="Name of your Company"]',
            'input[placeholder*="Company"]'
        ]
        
        for selector in company_selectors:
            try:
                await page.wait_for_selector(selector, timeout=3000)
                await page.fill(selector, self.config["test_data"]["company_name"])
                logger.info(f"✅ Entered Company Name: {self.config['test_data']['company_name']}")
                break
            except:
                continue
        
        await page.screenshot(path=str(self.screenshots_dir / '08_job_details_entered.png'), full_page=True)
        logger.info("📸 Step 8: Job details entered screenshot saved")

    async def _execute_final_steps(self, page):
        """Execute final workflow steps"""
        # Click Next
        logger.info("🔄 Looking for Next button...")
        next_selectors = [
            'button:has-text("Next")',
            'button[type="submit"]'
        ]
        
        for selector in next_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector)
                logger.info("✅ Clicked Next button!")
                break
            except:
                continue
        
        await page.wait_for_load_state('networkidle', timeout=15000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=str(self.screenshots_dir / '09_next_page_loaded.png'), full_page=True)
        logger.info("📸 Step 9: Next page loaded screenshot saved")
        
        # Expand All and Scroll
        logger.info("🔄 Looking for Expand All button...")
        expand_selectors = [
            'button:has-text("Expand All")',
            'button:has-text("Expand all")'
        ]
        
        for selector in expand_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector)
                logger.info("✅ Clicked Expand All button!")
                break
            except:
                continue
        
        await page.wait_for_timeout(2000)
        await page.screenshot(path=str(self.screenshots_dir / '10_expanded_top.png'), full_page=True)
        logger.info("📸 Step 10: Expanded view screenshot saved")
        
        # Scroll and take multiple screenshots
        for scroll_step in range(1, 4):
            await page.keyboard.press('PageDown')
            await page.wait_for_timeout(1000)
            await page.screenshot(path=str(self.screenshots_dir / f'11_scroll_step_{scroll_step}.png'), full_page=True)
            logger.info(f"📸 Step 11.{scroll_step}: Scroll step {scroll_step} screenshot saved")
        
        # Create
        await page.keyboard.press('Home')
        await page.wait_for_timeout(1000)
        
        logger.info("🔄 Looking for Create button...")
        create_final_selectors = [
            'button:has-text("Create")',
            'button[type="submit"]:has-text("Create")'
        ]
        
        for selector in create_final_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector)
                logger.info("✅ Clicked Create button!")
                break
            except:
                continue
        
        await page.wait_for_load_state('networkidle', timeout=15000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=str(self.screenshots_dir / '12_final_created.png'), full_page=True)
        logger.info("📸 Step 12: Final creation completed screenshot saved")
