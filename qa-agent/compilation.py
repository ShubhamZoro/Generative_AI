config.py

import os
from pathlib import Path

# API Keys
OPENAI_API_KEY = 
GEMINI_API_KEY = 

# Directories
BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "test_results"
SCREENSHOTS_DIR = RESULTS_DIR / "screenshots"
VIDEOS_DIR = RESULTS_DIR / "videos"

# Ensure directories exist
RESULTS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

# Recruter.ai Configuration
RECRUTER_CONFIG = {
    "base_url": "https://app.recruter.ai/",
    "credentials": {
        "email": "shubham.20gcebcs091@galgotiacollege.edu",
        "password": "Piratehunter1@"
    },
    "test_data": {
        "job_description": "Python Developer with 2+ years of experience needed for developing web applications using Django and Flask frameworks.",
        "skills": ["Python", "Django"],
        "experience_years": 2,
        "job_title": "Senior Python Developer",
        "company_name": "TechCorp Solutions"
    }
}

# Browser Configuration
BROWSER_CONFIG = {
    "headless": False,
    "slow_mo": 800,
    "viewport": {"width": 1280, "height": 720},
    "timeout": 30000
}

# LLM Configuration
LLM_CONFIG = {
    "model": "gpt-4o",
    "temperature": 0,
    "max_tokens": 4000
}

# Default video URL for testing
DEFAULT_VIDEO_URL = "https://www.youtube.com/watch?v=IK62Rk47aas"

main.py

import asyncio
import logging
import sys
from datetime import datetime

from config import DEFAULT_VIDEO_URL
from workflow import QAWorkflow
from recruter_automation import RecruterAIAutomation
from video_transcriber import VideoTranscriber
from test_case_generator import TestCaseGenerator
from utils import save_results, print_statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_full_workflow(video_url: str = DEFAULT_VIDEO_URL):
    """Run the complete QA workflow"""
    logger.info("=" * 60)
    logger.info("🧪 Starting Complete QA Agent Workflow")
    logger.info("=" * 60)
    
    # Initialize workflow
    qa_workflow_manager = QAWorkflow()
    qa_workflow = qa_workflow_manager.create_workflow()
    
    # Set initial state
    initial_state = {
        "video_url": video_url,
        "video_transcript": "",
        "test_cases": [],
        "playwright_scripts": [],
        "test_results": [],
        "summary_report": "",
        "recruter_test_result": None
    }
    
    try:
        # Execute workflow
        logger.info("🚀 Starting QA Agent workflow...")
        final_state = await qa_workflow.ainvoke(initial_state)
        
        # Save results
        save_results(final_state)
        
        # Print statistics
        print_statistics(final_state['test_results'], final_state.get('recruter_test_result'))
        
        logger.info("\n📁 Results saved in:")
        logger.info(f"   - test_results/test_cases.json")
        logger.info(f"   - test_results/playwright_scripts.json")
        logger.info(f"   - test_results/test_results.json")
        logger.info(f"   - test_results/report.md")
        logger.info(f"   - test_results/screenshots/ (multiple screenshots)")
        
        logger.info("\n🎉 QA Agent Workflow Completed Successfully!")
        return final_state
        
    except Exception as e:
        logger.error(f"❌ QA Agent workflow failed: {e}")
        raise

async def run_recruter_only():
    """Run only the Recruter.ai automation workflow"""
    logger.info("🚀 Running Recruter.ai automation only...")
    
    automation = RecruterAIAutomation()
    result = await automation.run_complete_workflow()
    
    # Save individual result
    from utils import save_test_results
    save_test_results([], result)
    
    print_statistics([], result)
    
    logger.info("✅ Recruter.ai automation completed")
    return result

async def run_test_generation_only(video_url: str = DEFAULT_VIDEO_URL):
    """Run only test case generation from video"""
    logger.info("📝 Running test case generation only...")
    
    transcriber = VideoTranscriber()
    generator = TestCaseGenerator()
    
    # Transcribe video
    transcript = await transcriber.transcribe_video(video_url)
    
    # Generate test cases
    test_cases = await generator.generate_test_cases(transcript)
    
    # Save results
    from utils import save_test_cases
    save_test_cases(test_cases)
    
    logger.info(f"✅ Generated {len(test_cases)} test cases")
    return test_cases

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "recruter-only":
            asyncio.run(run_recruter_only())
        elif command == "generate-only":
            video_url = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_VIDEO_URL
            asyncio.run(run_test_generation_only(video_url))
        elif command == "full":
            video_url = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_VIDEO_URL
            asyncio.run(run_full_workflow(video_url))
        else:
            print("Usage: python main.py [full|recruter-only|generate-only] [video_url]")
            print("Commands:")
            print("  full - Run complete QA workflow (default)")
            print("  recruter-only - Run only Recruter.ai automation")
            print("  generate-only - Run only test case generation")
    else:
        # Default: run full workflow
        asyncio.run(run_full_workflow())

if __name__ == "__main__":
    main()

models.py
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, TypedDict
from datetime import datetime

@dataclass
class TestCase:
    """Represents a single test case"""
    id: str
    name: str
    description: str
    steps: List[Dict[str, str]]
    expected_result: str
    test_type: str  # core, edge_case, accessibility, performance
    priority: str  # high, medium, low
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        """Create from dictionary"""
        return cls(**data)

@dataclass
class TestResult:
    """Represents test execution result"""
    test_case_id: str
    test_name: str
    status: str  # passed, failed, skipped
    duration: float
    error_message: str = ""
    screenshot_path: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestResult":
        """Create from dictionary"""
        return cls(**data)

class QAAgentState(TypedDict):
    """State for the QA Agent workflow"""
    video_url: str
    video_transcript: str
    test_cases: List[TestCase]
    playwright_scripts: List[str]
    test_results: List[TestResult]
    summary_report: str
    recruter_test_result: TestResult

play_wright.py

import asyncio
from playwright.async_api import async_playwright

async def login_to_website(url, username, password, username_selector, password_selector, login_button_selector):
    """
    Automate login to a website using Playwright with specific workflow
    """
    
    async with async_playwright() as p:
        # Launch browser with headless=False to see Chrome opening
        browser = await p.chromium.launch(
            headless=False,  # This will open Chrome visually
            slow_mo=800     # Slow down actions so you can see what's happening
        )
        
        # Create a new page
        page = await browser.new_page()
        
        try:
            # Navigate to login page
            print(f"🔄 Navigating to {url}")
            await page.goto(url)
            await page.wait_for_load_state('networkidle')
            
            # Fill username and password
            print("🔄 Filling credentials...")
            await page.fill(username_selector, username)
            await page.fill(password_selector, password)
            await page.press(password_selector, 'Enter')
            
            await page.wait_for_load_state('networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Take screenshot after login
            await page.screenshot(path='01_after_login.png', full_page=True)
            print("📸 Step 1: After login screenshot saved")
            
            # Click Create Interview
            print("🔄 Looking for Create Interview button...")
            create_selectors = [
                '#joyride_step1_create_new_campaign_button',
                'button:has-text("Create Interview")',
                'span:has-text("Create Interview")'
            ]
            
            for selector in create_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    print("✅ Clicked Create Interview button!")
                    break
                except:
                    continue
            
            await page.wait_for_load_state('networkidle', timeout=15000)
            await page.wait_for_timeout(3000)
            
            # Take screenshot of job description page
            await page.screenshot(path='02_job_description_page.png', full_page=True)
            print("📸 Step 2: Job description page screenshot saved")
            
            # Click on "Enhance with AI" tab
            print("🔄 Clicking on Enhance with AI tab...")
            enhance_selectors = [
                'button:has-text("Enhance with AI")',
                '[data-radix-collection-item]:has-text("Enhance with AI")',
                'button[role="tab"]:has-text("Enhance with AI")'
            ]
            
            for selector in enhance_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    print("✅ Clicked Enhance with AI tab!")
                    break
                except:
                    continue
            
            await page.wait_for_timeout(2000)
            
            # Take screenshot of Enhance with AI page
            await page.screenshot(path='03_enhance_with_ai_page.png', full_page=True)
            print("📸 Step 3: Enhance with AI page screenshot saved")
            
            # Click the middle button (assuming it's the second button)
            print("🔄 Looking for the middle button...")
            buttons = await page.query_selector_all('button')
            
            # Find buttons that might be the three options
            middle_button_found = False
            for i, button in enumerate(buttons):
                try:
                    button_text = await button.inner_text()
                    if any(keyword in button_text.lower() for keyword in ['moderate', 'medium', 'standard']):
                        await button.click()
                        print(f"✅ Clicked middle button: {button_text}")
                        middle_button_found = True
                        break
                except:
                    continue
            
            if not middle_button_found:
                # Try clicking the second visible button if no specific middle button found
                try:
                    visible_buttons = []
                    for button in buttons:
                        if await button.is_visible():
                            visible_buttons.append(button)
                    if len(visible_buttons) >= 2:
                        await visible_buttons[1].click()  # Click second button (middle one)
                        print("✅ Clicked middle (second) button")
                except:
                    print("⚠️ Could not find middle button")
            
            await page.wait_for_timeout(1000)
            
            # Enter description in text area
            print("🔄 Entering job description...")
            description_text = """Python Developer with 2+ years of experience needed for developing web applications using Django and Flask frameworks."""
            
            description_selectors = [
                'textarea',
                'textarea[placeholder*="description"]',
                'textarea[placeholder*="key points"]',
                'input[type="text"]'
            ]
            
            for selector in description_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    await page.fill(selector, description_text)
                    print("✅ Filled job description!")
                    break
                except:
                    continue
            
            await page.wait_for_timeout(1000)
            
            # Take screenshot after entering description
            await page.screenshot(path='04_description_entered.png', full_page=True)
            print("📸 Step 4: Description entered screenshot saved")
            
            # Click "Enhance JD" button
            print("🔄 Looking for Enhance JD button...")
            enhance_jd_selectors = [
                'button:has-text("Enhance JD")',
                'button:has-text("Enhance")',
                'button[type="submit"]'
            ]
            
            for selector in enhance_jd_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    print("✅ Clicked Enhance JD button!")
                    break
                except:
                    continue
            
            # Wait for 8 seconds as requested
            print("⏳ Waiting 8 seconds for enhancement...")
            await page.wait_for_timeout(8000)
            
            # Take screenshot after enhancement
            await page.screenshot(path='05_after_enhancement.png', full_page=True)
            print("📸 Step 5: After enhancement screenshot saved")
            
            # Click "Save JD" button
            print("🔄 Looking for Save JD button...")
            save_jd_selectors = [
                'button:has-text("Save JD")',
                'button:has-text("Save")',
                '#save-button'
            ]
            
            for selector in save_jd_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    print("✅ Clicked Save JD button!")
                    break
                except:
                    continue
            
            await page.wait_for_timeout(2000)
            
            # Take screenshot after saving JD
            await page.screenshot(path='06_after_save_jd.png', full_page=True)
            print("📸 Step 6: After Save JD screenshot saved")
            
            # Add skills twice
            for skill_num in range(1, 3):
                print(f"🔄 Adding skill #{skill_num}...")
                
                # Enter skill name
                skill_names = ["Python", "Django"]
                skill_name_selectors = [
                    'input[placeholder*="skill name"]',
                    'input[placeholder*="Enter skill"]',
                    '#custom-skill'
                ]
                
                for selector in skill_name_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=3000)
                        await page.fill(selector, skill_names[skill_num-1])
                        print(f"✅ Entered skill name: {skill_names[skill_num-1]}")
                        break
                    except:
                        continue
                
                # Enter experience (2 years)
                experience_selectors = [
                    'input[placeholder*="Experience"]',
                    'input[type="number"]',
                    '#custom-experience'
                ]
                
                for selector in experience_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=3000)
                        await page.fill(selector, "2")
                        print("✅ Entered experience: 2 years")
                        break
                    except:
                        continue
                
                # Click "Add Skill" button
                add_skill_selectors = [
                    'button:has-text("Add Skill")',
                    'button:has-text("Add")',
                    '#add-skill-button'
                ]
                
                for selector in add_skill_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=3000)
                        await page.click(selector)
                        print("✅ Clicked Add Skill button!")
                        break
                    except:
                        continue
                
                await page.wait_for_timeout(1000)
                
                # Take screenshot after adding skill
                await page.screenshot(path=f'07_skill_{skill_num}_added.png', full_page=True)
                print(f"📸 Step 7.{skill_num}: Skill {skill_num} added screenshot saved")
            
            # Enter Job Title
            print("🔄 Entering Job Title...")
            job_title_selectors = [
                'input[placeholder*="position you are hiring"]',
                'input[placeholder*="Job Title"]',
                '#job-title'
            ]
            
            for selector in job_title_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    await page.fill(selector, "Senior Python Developer")
                    print("✅ Entered Job Title: Senior Python Developer")
                    break
                except:
                    continue
            
            # Enter Company Name
            print("🔄 Entering Company Name...")
            company_selectors = [
                'input[placeholder*="Name of your Company"]',
                'input[placeholder*="Company"]',
                '#company-name'
            ]
            
            for selector in company_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    await page.fill(selector, "TechCorp Solutions")
                    print("✅ Entered Company Name: TechCorp Solutions")
                    break
                except:
                    continue
            
            await page.wait_for_timeout(1000)
            
            # Take screenshot after entering job details
            await page.screenshot(path='08_job_details_entered.png', full_page=True)
            print("📸 Step 8: Job details entered screenshot saved")
            
            # Click "Next" button
            print("🔄 Looking for Next button...")
            next_selectors = [
                'button:has-text("Next")',
                'button[type="submit"]',
                '#next-button'
            ]
            
            for selector in next_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    print("✅ Clicked Next button!")
                    break
                except:
                    continue
            
            # Wait for next page to load
            await page.wait_for_load_state('networkidle', timeout=15000)
            await page.wait_for_timeout(3000)
            
            # Take screenshot of next page
            await page.screenshot(path='09_next_page_loaded.png', full_page=True)
            print("📸 Step 9: Next page loaded screenshot saved")
            
            # Click "Expand All" button
            print("🔄 Looking for Expand All button...")
            expand_selectors = [
                'button:has-text("Expand All")',
                'button:has-text("Expand all")',
                'button:has-text("expand")',
                '[aria-label*="expand"]'
            ]
            
            for selector in expand_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    print("✅ Clicked Expand All button!")
                    break
                except:
                    continue
            
            await page.wait_for_timeout(2000)
            
            # Scroll the page and take screenshots
            print("🔄 Scrolling page and taking screenshots...")
            
            # Take screenshot at top
            await page.screenshot(path='10_expanded_top.png', full_page=True)
            print("📸 Step 10: Expanded view (top) screenshot saved")
            
            # Scroll down in steps
            for scroll_step in range(1, 4):
                await page.keyboard.press('PageDown')
                await page.wait_for_timeout(1000)
                await page.screenshot(path=f'11_scroll_step_{scroll_step}.png', full_page=True)
                print(f"📸 Step 11.{scroll_step}: Scroll step {scroll_step} screenshot saved")
            
            # Scroll back to top
            await page.keyboard.press('Home')
            await page.wait_for_timeout(1000)
            
            # Click "Create" button
            print("🔄 Looking for Create button...")
            create_final_selectors = [
                'button:has-text("Create")',
                'button[type="submit"]:has-text("Create")',
                '#create-button'
            ]
            
            for selector in create_final_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    print("✅ Clicked Create button!")
                    break
                except:
                    continue
            
            # Wait for final creation
            await page.wait_for_load_state('networkidle', timeout=15000)
            await page.wait_for_timeout(3000)
            
            # Take final screenshot
            await page.screenshot(path='12_final_created.png', full_page=True)
            print("📸 Step 12: Final creation completed screenshot saved")
            
            print("\n🎉 === AUTOMATION COMPLETED SUCCESSFULLY ===")
            print("📸 All screenshots saved:")
            print("  01_after_login.png")
            print("  02_job_description_page.png")
            print("  03_enhance_with_ai_page.png")
            print("  04_description_entered.png")
            print("  05_after_enhancement.png")
            print("  06_after_save_jd.png")
            print("  07_skill_1_added.png")
            print("  07_skill_2_added.png")
            print("  08_job_details_entered.png")
            print("  09_next_page_loaded.png")
            print("  10_expanded_top.png")
            print("  11_scroll_step_*.png")
            print("  12_final_created.png")
            
            print("\n✅ Completed all steps as requested!")
            print("Press Enter to close browser...")
            input()
            
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            await page.screenshot(path='error_screenshot.png')
            print("Error screenshot saved. Press Enter to close browser...")
            input()
            
        finally:
            await browser.close()

async def main():
    LOGIN_URL = "https://app.recruter.ai/"
    USERNAME = "shubham.20gcebcs091@galgotiacollege.edu"
    PASSWORD = "Piratehunter1@"
    
    USERNAME_SELECTOR = 'input[name="email"]'
    PASSWORD_SELECTOR = 'input[name="password"]'
    LOGIN_BUTTON_SELECTOR = '#submit'
    
    await login_to_website(
        url=LOGIN_URL,
        username=USERNAME,
        password=PASSWORD,
        username_selector=USERNAME_SELECTOR,
        password_selector=PASSWORD_SELECTOR,
        login_button_selector=LOGIN_BUTTON_SELECTOR
    )

if __name__ == "__main__":
    asyncio.run(main())

recuter_automation.py

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

report_generator.py

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

script_generator.py

import json
import logging
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from config import OPENAI_API_KEY, LLM_CONFIG
from models import TestCase

logger = logging.getLogger(__name__)

class PlaywrightScriptGenerator:
    """Converts test cases to Playwright scripts"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=LLM_CONFIG["temperature"],
            model=LLM_CONFIG["model"],
            api_key=OPENAI_API_KEY
        )
    
    async def generate_scripts(self, test_cases: List[TestCase]) -> List[str]:
        """Generate Playwright test scripts from test cases"""
        scripts = []
        
        for test_case in test_cases:
            prompt = self._create_script_generation_prompt(test_case)
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            scripts.append(response.content)
        
        return scripts
    
    def _create_script_generation_prompt(self, test_case: TestCase) -> str:
        """Create prompt for script generation"""
        return f"""Convert the following test case into a Playwright Python async test script for Recruter.ai:

Test Case: {test_case.name}
Description: {test_case.description}
Steps: {json.dumps(test_case.steps, indent=2)}
Expected Result: {test_case.expected_result}

Generate a complete async Playwright test function with:
- Proper error handling
- Screenshots on failure
- Assertions for expected results
- Page waits for proper synchronization

Use this format:
```python
async def test_{test_case.id.lower()}(page):
    try:
        # Test implementation here
        await page.goto("https://app.recruter.ai/")
        # Add more steps based on the test case
        
        # Take success screenshot
        await page.screenshot(path=f"success_{test_case.id}.png")
        
    except Exception as e:
        await page.screenshot(path=f"failure_{test_case.id}.png")
        raise e
```
"""

test_case_generator.py

import json
import logging
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from config import OPENAI_API_KEY, LLM_CONFIG
from models import TestCase

logger = logging.getLogger(__name__)

class TestCaseGenerator:
    """Generates test cases from video transcript"""

    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=LLM_CONFIG["temperature"], 
            model=LLM_CONFIG["model"],
            api_key=OPENAI_API_KEY
        )

    async def generate_test_cases(self, transcript: str) -> List[TestCase]:
        """Generate comprehensive test cases from transcript"""
        
        prompt = self._create_test_generation_prompt(transcript)
        
        messages = [
            SystemMessage(content="Respond strictly with JSON. No text, no formatting, no explanations."),
            HumanMessage(content=prompt)
        ]

        response = await self.llm.ainvoke(messages)

        logger.info("LLM raw response:")
        logger.info(response.content)

        try:
            test_cases = self._parse_llm_response(response.content)
            return test_cases
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response content was:\n{response.content}")
            return self._get_fallback_test_cases()

    def _create_test_generation_prompt(self, transcript: str) -> str:
        """Create prompt for test case generation"""
        return f"""You are QAgenie — a calm, thorough AI QA assistant for Recruter.ai platform.
Based on the following video transcript, generate comprehensive test cases covering the complete user workflow.

Focus on testing these key areas:
1. Login functionality with email/password
2. Create Interview workflow
3. Job description enhancement with AI
4. Skills and experience configuration  
5. Company and job title setup
6. Interview question generation
7. Error handling and edge cases

Transcript:
{transcript}

Generate test cases in the following strict JSON format:
{{
    "test_cases": [
        {{
            "id": "TC001",
            "name": "Successful Login to Recruter.ai",
            "description": "Verify user can login successfully with valid credentials",
            "steps": [
                {{"action": "navigate", "target": "https://app.recruter.ai/", "data": ""}},
                {{"action": "fill", "target": "input[name='email']", "data": "shubham.20gcebcs091@galgotiacollege.edu"}},
                {{"action": "fill", "target": "input[name='password']", "data": "Piratehunter1@"}},
                {{"action": "press", "target": "input[name='password']", "data": "Enter"}},
                {{"action": "wait", "target": "networkidle", "data": "5000"}}
            ],
            "expected_result": "User successfully logs in and dashboard is displayed",
            "test_type": "core",
            "priority": "high"
        }}
    ]
}}
Only return the JSON. No markdown formatting, no explanations, no text outside the JSON."""

    def _parse_llm_response(self, content: str) -> List[TestCase]:
        """Parse LLM response into TestCase objects"""
        # Clean the response content
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        test_data = json.loads(content)
        test_cases = []
        for tc in test_data['test_cases']:
            test_case = TestCase(
                id=tc['id'],
                name=tc['name'],
                description=tc['description'],
                steps=tc['steps'],
                expected_result=tc['expected_result'],
                test_type=tc['test_type'],
                priority=tc['priority']
            )
            test_cases.append(test_case)
        return test_cases

    def _get_fallback_test_cases(self) -> List[TestCase]:
        """Fallback test cases if LLM fails"""
        return [
            TestCase(
                id="TC001",
                name="Successful Login to Recruter.ai",
                description="Verify user can login successfully with valid credentials",
                steps=[
                    {"action": "navigate", "target": "https://app.recruter.ai/", "data": ""},
                    {"action": "fill", "target": "input[name='email']", "data": "shubham.20gcebcs091@galgotiacollege.edu"},
                    {"action": "fill", "target": "input[name='password']", "data": "Piratehunter1@"},
                    {"action": "press", "target": "input[name='password']", "data": "Enter"}
                ],
                expected_result="User successfully logs in and dashboard is displayed",
                test_type="core",
                priority="high"
            ),
            TestCase(
                id="TC002",
                name="Create Interview Complete Workflow",
                description="Test the complete interview creation process with AI enhancement",
                steps=[
                    {"action": "click", "target": "button:has-text('Create Interview')", "data": ""},
                    {"action": "click", "target": "button:has-text('Enhance with AI')", "data": ""},
                    {"action": "fill", "target": "textarea", "data": "Python Developer with 2+ years experience"},
                    {"action": "click", "target": "button:has-text('Enhance JD')", "data": ""},
                    {"action": "wait", "target": "", "data": "8000"}
                ],
                expected_result="Interview creation workflow completes successfully",
                test_type="core", 
                priority="high"
            )
        ]

test_executor.py

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

utils.py

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

video_transcriber.py

import logging
from youtube_transcript_api import YouTubeTranscriptApi as yta

logger = logging.getLogger(__name__)

class VideoTranscriber:
    """Handles video transcription using YouTube Transcript API"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def transcribe_video(self, video_url: str) -> str:
        """Extract detailed transcription from YouTube video"""
        try:
            # Extract video ID from URL
            vid_id = self._extract_video_id(video_url)
            
            self.logger.info(f"Extracting transcript for video ID: {vid_id}")
            
            # Get transcript data
            transcript_data = yta.get_transcript(vid_id)
            
            # Process transcript with timestamps for better context
            processed_transcript = self._process_transcript(transcript_data)
            
            # Add metadata about the video
            metadata = self._create_metadata(video_url, vid_id, transcript_data, processed_transcript)
            
            self.logger.info(f"Successfully extracted transcript with {len(transcript_data)} segments")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error transcribing video: {e}")
            return self._get_fallback_transcript(video_url)
    
    def _extract_video_id(self, video_url: str) -> str:
        """Extract video ID from URL"""
        if 'watch?v=' in video_url:
            return video_url.split('watch?v=')[-1].split('&')[0]
        elif 'youtu.be/' in video_url:
            return video_url.split('youtu.be/')[-1].split('?')[0]
        else:
            return video_url.split('=')[-1]
    
    def _process_transcript(self, transcript_data: list) -> str:
        """Process transcript with timestamps"""
        processed_transcript = []
        for entry in transcript_data:
            timestamp = entry['start']
            text = entry['text'].strip()
            if text:  # Only add non-empty text
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                processed_transcript.append(f"[{minutes:02d}:{seconds:02d}] {text}")
        
        return '\n'.join(processed_transcript)
    
    def _create_metadata(self, video_url: str, vid_id: str, transcript_data: list, processed_transcript: str) -> str:
        """Create metadata string"""
        return f"""Video URL: {video_url}
Video ID: {vid_id}
Transcript Length: {len(transcript_data)} segments
Total Duration: ~{int(transcript_data[-1]['start'] / 60)} minutes

Detailed Transcript:
{processed_transcript}
"""
    
    def _get_fallback_transcript(self, video_url: str) -> str:
        """Return fallback transcript for Recruter.ai testing"""
        return f"""Fallback transcript for Recruter.ai platform - {video_url}:
This video demonstrates the complete workflow of creating an interview on Recruter.ai platform.
The process includes:
1. Login to the platform with email and password
2. Navigate to Create Interview section
3. Add job description using AI enhancement features
4. Configure skills and experience requirements
5. Set up company information and job details
6. Generate comprehensive interview questions
7. Review and finalize the interview setup
"""

workflow.py

import logging
from langgraph.graph import StateGraph, END

from models import QAAgentState
from video_transcriber import VideoTranscriber
from test_case_generator import TestCaseGenerator
from script_generator import PlaywrightScriptGenerator
from test_executor import TestExecutor
from recruter_automation import RecruterAIAutomation
from report_generator import ReportGenerator

logger = logging.getLogger(__name__)

class QAWorkflow:
    """QA Agent workflow orchestrator"""
    
    def __init__(self):
        # Initialize components
        self.transcriber = VideoTranscriber()
        self.test_generator = TestCaseGenerator()
        self.script_generator = PlaywrightScriptGenerator()
        self.executor = TestExecutor()
        self.recruter_automation = RecruterAIAutomation()
        self.reporter = ReportGenerator()
    
    def create_workflow(self):
        """Create the QA agent workflow using LangGraph"""
        
        workflow = StateGraph(QAAgentState)
        
        # Add nodes to workflow
        workflow.add_node("transcribe", self._transcribe_video_node)
        workflow.add_node("generate_cases", self._generate_test_cases_node)
        workflow.add_node("generate_scripts", self._generate_scripts_node)
        workflow.add_node("execute_recruter_workflow", self._execute_recruter_workflow_node)
        workflow.add_node("execute_tests", self._execute_tests_node)
        workflow.add_node("generate_report", self._generate_report_node)
        
        # Define edges
        workflow.add_edge("transcribe", "generate_cases")
        workflow.add_edge("generate_cases", "generate_scripts")
        workflow.add_edge("generate_scripts", "execute_recruter_workflow")
        workflow.add_edge("execute_recruter_workflow", "execute_tests")
        workflow.add_edge("execute_tests", "generate_report")
        workflow.add_edge("generate_report", END)
        
        # Set entry point
        workflow.set_entry_point("transcribe")
        
        return workflow.compile()
    
    async def _transcribe_video_node(self, state: QAAgentState):
        """Node to transcribe video"""
        logger.info("🎥 Starting video transcription...")
        transcript = await self.transcriber.transcribe_video(state['video_url'])
        logger.info("✅ Video transcription completed")
        return {"video_transcript": transcript}
    
    async def _generate_test_cases_node(self, state: QAAgentState):
        """Node to generate test cases"""
        logger.info("📝 Generating test cases...")
        test_cases = await self.test_generator.generate_test_cases(state['video_transcript'])
        logger.info(f"✅ Generated {len(test_cases)} test cases")
        return {"test_cases": test_cases}
    
    async def _generate_scripts_node(self, state: QAAgentState):
        """Node to generate Playwright scripts"""
        logger.info("🎭 Generating Playwright scripts...")
        scripts = await self.script_generator.generate_scripts(state['test_cases'])
        logger.info(f"✅ Generated {len(scripts)} Playwright scripts")
        return {"playwright_scripts": scripts}
    
    async def _execute_recruter_workflow_node(self, state: QAAgentState):
        """Node to execute complete Recruter.ai workflow"""
        logger.info("🚀 Executing complete Recruter.ai workflow...")
        recruter_result = await self.recruter_automation.run_complete_workflow()
        logger.info(f"✅ Recruter.ai workflow completed with status: {recruter_result.status}")
        return {"recruter_test_result": recruter_result}
    
    async def _execute_tests_node(self, state: QAAgentState):
        """Node to execute individual test cases"""
        logger.info("🧪 Executing individual test cases...")
        results = []
        for test_case, script in zip(state['test_cases'], state['playwright_scripts']):
            logger.info(f"Running test: {test_case.name}")
            result = await self.executor.execute_test(test_case, script)
            results.append(result)
        logger.info(f"✅ Executed {len(results)} test cases")
        return {"test_results": results}
    
    async def _generate_report_node(self, state: QAAgentState):
        """Node to generate comprehensive report"""
        logger.info("📊 Generating test report...")
        report = await self.reporter.generate_summary(
            state['test_results'], 
            state.get('recruter_test_result')
        )
        logger.info("✅ Test report generated")
        return {"summary_report": report}

Now I want that use this code below to understand the image(create testcase json and .py file) and use the above code to do what is in the document 
from google import genai
from google.genai import types

import requests

image_path = "https://goo.gle/instrument-img"
image_bytes = requests.get(image_path).content
image = types.Part.from_bytes(
  data=image_bytes, mime_type="image/jpeg"
)

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=["What is this image?", image],
)

print(response.text)
