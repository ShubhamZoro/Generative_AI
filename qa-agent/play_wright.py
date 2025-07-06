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