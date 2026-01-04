from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time

# Initialize the Chrome driver
driver = webdriver.Chrome()
job_profile = input("Enter job profile (e.g., AI/ML Engineer): ")
location = input("Enter location : ")
experience = input("Enter experience in years:")
fresheness = input("Enter job freshness in days (e.g., 1 for last 24 hours): ")


# URL to scrape
url = f"https://www.foundit.in/search/{job_profile}-jobs-in-india?start=1&limit=20&query={job_profile}&location={location}&queryDerived=true&jobCities={location}&experienceRanges={experience}%7E{experience}&jobFreshness={fresheness}"

# Navigate to the URL
driver.get(url)
time.sleep(5)  # Wait for page to load

# List to store job data
jobs_data = []

try:
    # Find all job cards
    job_wrappers = driver.find_elements(By.CLASS_NAME, "jobCardWrapper")
    print(f"Found {len(job_wrappers)} jobs")
    
    # Extract job titles and links
    job_links = []
    for wrapper in job_wrappers:
        try:
            h2_element = wrapper.find_element(By.CLASS_NAME, "jobCardTitle")
            a_tag = h2_element.find_element(By.TAG_NAME, "a")
            job_title = a_tag.text
            job_link = a_tag.get_attribute("href")
            job_links.append({"title": job_title, "link": job_link})
        except NoSuchElementException:
            continue
    
    print(f"Extracted {len(job_links)} job links")
    
    # Visit each job page to extract skills
    for idx, job in enumerate(job_links):
        print(f"Processing job {idx + 1}/{len(job_links)}: {job['title']}")
        
        try:
            # Navigate to job page
            driver.get(job['link'])
            time.sleep(3)  # Wait for page to load
            
            skills = []
            try:
                # Find the key_skills span
                key_skills_section = driver.find_element(By.ID, "skillSectionNew")
                # Find all 'a' tags within the key_skills section
                skill_tags = key_skills_section.find_elements(By.TAG_NAME, "a")
                skills = [skill.text for skill in skill_tags if skill.text.strip()]
            except NoSuchElementException:
                print(f"  No skills found for: {job['title']}")
            
            # Store job data
            jobs_data.append({
                "Job Title": job['title'],
                "Job Link": job['link'],
                "Skills": ", ".join(skills) if skills else "N/A"
            })
            
        except Exception as e:
            print(f"  Error processing job: {e}")
            jobs_data.append({
                "Job Title": job['title'],
                "Job Link": job['link'],
                "Skills": "Error"
            })
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(jobs_data)
    excel_filename = "foundit_jobs.xlsx"
    df.to_excel(excel_filename, index=False, engine='openpyxl')
    print(f"\nData saved to {excel_filename}")
    print(f"Total jobs scraped: {len(jobs_data)}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
    print("Browser closed")