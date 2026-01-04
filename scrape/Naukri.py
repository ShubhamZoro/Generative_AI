from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
from datetime import datetime
import time

# User Input
job_profile = input("Enter job profile (e.g., AI/ML Engineer): ")
location = input("Enter location (e.g., Bangalore) or press Enter for all India: ")
experience = input("Enter experience in years (e.g., 2, 5, 0-2, 3-5) or press Enter to skip: ")
num_jobs = int(input("How many jobs to scrape (default 10): ") or 10)

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=chrome_options)

# Build Naukri URL
query = job_profile.lower().replace(' ', '-').replace('/', '-')
loc_param = f"-in-{location.lower().replace(' ', '-')}" if location else ""

# Build experience parameter
exp_param = ""
if experience:
    # Handle different experience formats
    if '-' in experience:
        # Range format like "2-5"
        exp_range = experience.replace(' ', '')
        exp_param = f"&experience={exp_range}"
    else:
        # Single number like "2" - treat as minimum
        exp_param = f"&experience={experience}"

url = f"https://www.naukri.com/{query}-jobs{loc_param}?jobAge=1{exp_param}"

print(f"\n🔍 Searching Naukri: {url}\n")

# Open page
driver.get(url)
time.sleep(5)

# Scroll page
driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
time.sleep(2)

# Find all job wrappers
job_wrappers = driver.find_elements(By.CLASS_NAME, "srp-jobtuple-wrapper")[:num_jobs]

print(f"Found {len(job_wrappers)} jobs\n")

# Store job data
jobs_data = []

for i, wrapper in enumerate(job_wrappers, 1):
    try:
        # Get row1 div
        row1_div = wrapper.find_element(By.CLASS_NAME, "row1")
        
        # Get job title and link from <a> tag
        job_link_elem = row1_div.find_element(By.TAG_NAME, "a")
        title = job_link_elem.text.strip()
        link = job_link_elem.get_attribute("href")
        
        # Get company
        try:
            company = wrapper.find_element(By.CLASS_NAME, "comp-name").text.strip()
        except:
            company = "N/A"
        
        # Get location
        try:
            job_location = wrapper.find_element(By.CLASS_NAME, "locWdth").text.strip()
        except:
            job_location = "N/A"
        
        # Get experience
        try:
            experience = wrapper.find_element(By.CLASS_NAME, "expwdth").text.strip()
        except:
            experience = "N/A"
        
        # Get salary
        try:
            salary = wrapper.find_element(By.CLASS_NAME, "sal-wrap").text.strip()
        except:
            salary = "Not Disclosed"
        
        # Get skills from row5 div
        skills = "N/A"
        try:
            row5_div = wrapper.find_element(By.CLASS_NAME, "row5")
            # Find all <li> tags inside row5
            skill_items = row5_div.find_elements(By.TAG_NAME, "li")
            if skill_items:
                # Extract text from each <li> and join with comma
                skills = ", ".join([item.text.strip() for item in skill_items if item.text.strip()])
        except:
            skills = "N/A"
        
        jobs_data.append({
            'Job Title': title,
            #'Company': company,
            #'Location': job_location,
            #'Experience': experience,
           # 'Salary': salary,
            'Skills': skills,
            'Job Link': link,
            #'Scraped On': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        
        print(f"✓ {i}. {title[:60]}")
        
    except Exception as e:
        print(f"✗ Error on job {i}: {e}")

# Close browser
driver.quit()

# Save to Excel
if jobs_data:
    df = pd.DataFrame(jobs_data)
    filename = f'naukri_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    df.to_excel(filename, index=False, sheet_name='Jobs')
    
    print(f"\n✅ Saved {len(jobs_data)} jobs to '{filename}'")
else:
    print("\n❌ No jobs found!")