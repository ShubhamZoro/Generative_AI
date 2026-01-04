from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from datetime import datetime
import time
import json
from openai import OpenAI
import PyPDF2
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

load_dotenv()

def send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, attachment_path):
    """Send email with Excel attachment using Gmail SMTP"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'html'))
        
        # Attach file
        filename = os.path.basename(attachment_path)
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {filename}')
        msg.attach(part)
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email to {recipient_email}: {e}")
        return False

def setup_chrome_driver():
    """Setup Chrome driver with headless options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    return webdriver.Chrome(options=chrome_options)

def read_resume(resume_file_path):
    """Read resume content from file (supports .txt and .pdf)"""
    try:
        if resume_file_path.lower().endswith('.pdf'):
            with open(resume_file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                resume_content = ""
                for page in pdf_reader.pages:
                    resume_content += page.extract_text() + "\n"
            print(f"✅ Resume loaded from PDF '{resume_file_path}' ({len(pdf_reader.pages)} pages)")
        else:
            with open(resume_file_path, 'r', encoding='utf-8') as f:
                resume_content = f.read()
            print(f"✅ Resume loaded from '{resume_file_path}'")
        
        return resume_content.strip()
    except FileNotFoundError:
        print(f"❌ Resume file not found: {resume_file_path}")
        return None
    except Exception as e:
        print(f"❌ Error reading resume: {e}")
        return None

def calculate_match_score_with_ai(job_title, job_skills, resume_content, client):
    """Use OpenAI API to calculate match score between job and resume"""
    
    prompt = f"""Analyze the match between this job and the candidate's resume.

Job Title: {job_title}
Required Skills: {job_skills}

Candidate Resume:
{resume_content}

Provide ONLY a JSON response with this exact structure (no markdown, no extra text):
{{
  "match_percentage": <number between 0-100>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill3", "skill4"],
  "brief_reason": "2-3 sentence explanation"
}}

Be strict but fair in your assessment. Consider:
1. Direct skill matches
2. Related/transferable skills
3. Experience level alignment
4. Domain knowledge overlap"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert recruiter analyzing job-candidate fit. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        result = json.loads(response_text)
        return result
        
    except Exception as e:
        print(f"    ⚠️ AI scoring error for '{job_title[:30]}...': {e}")
        return {
            "match_percentage": 0,
            "matching_skills": [],
            "missing_skills": [],
            "brief_reason": "Error calculating match"
        }

def scrape_naukri(driver, job_profile, location, experience, num_jobs):
    """Scrape jobs from Naukri.com"""
    jobs_data = []
    
    try:
        query = job_profile.lower().replace(' ', '-').replace('/', '-')
        loc_param = f"-in-{location.lower().replace(' ', '-')}" if location else ""
        
        exp_param = ""
        if experience and str(experience).strip():
            if '-' in str(experience):
                exp_range = str(experience).replace(' ', '')
                exp_param = f"&experience={exp_range}"
            else:
                exp_param = f"&experience={experience}"
        
        url = f"https://www.naukri.com/{query}-jobs{loc_param}?jobAge=1{exp_param}"
        
        print(f"  🔍 Naukri URL: {url}")
        
        driver.get(url)
        time.sleep(5)
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        
        job_wrappers = driver.find_elements(By.CLASS_NAME, "srp-jobtuple-wrapper")[:num_jobs]
        
        print(f"  Found {len(job_wrappers)} jobs on Naukri")
        
        for i, wrapper in enumerate(job_wrappers, 1):
            try:
                row1_div = wrapper.find_element(By.CLASS_NAME, "row1")
                job_link_elem = row1_div.find_element(By.TAG_NAME, "a")
                title = job_link_elem.text.strip()
                link = job_link_elem.get_attribute("href")
                
                skills = "N/A"
                try:
                    row5_div = wrapper.find_element(By.CLASS_NAME, "row5")
                    skill_items = row5_div.find_elements(By.TAG_NAME, "li")
                    if skill_items:
                        skills = ", ".join([item.text.strip() for item in skill_items if item.text.strip()])
                except:
                    skills = "N/A"
                
                jobs_data.append({
                    'Source': 'Naukri',
                    'Job Title': title,
                    'Skills': skills,
                    'Job Link': link,
                })
                
                print(f"    ✓ Naukri Job {i}: {title[:50]}")
                
            except Exception as e:
                print(f"    ✗ Error on Naukri job {i}: {e}")
    
    except Exception as e:
        print(f"  ❌ Error scraping Naukri: {e}")
    
    return jobs_data

def scrape_foundit(driver, job_profile, location, experience, num_jobs, freshness=1):
    """Scrape jobs from Foundit.in"""
    jobs_data = []
    
    try:
        url = f"https://www.foundit.in/search/{job_profile}-jobs-in-india?start=1&limit={num_jobs}&query={job_profile}&location={location}&queryDerived=true&jobCities={location}&experienceRanges={experience}%7E{experience}&jobFreshness={freshness}"
        
        print(f"  🔍 Foundit URL: {url}")
        
        driver.get(url)
        time.sleep(5)
        
        job_wrappers = driver.find_elements(By.CLASS_NAME, "jobCardWrapper")[:num_jobs]
        print(f"  Found {len(job_wrappers)} jobs on Foundit")
        
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
        
        for idx, job in enumerate(job_links):
            try:
                driver.get(job['link'])
                time.sleep(3)
                
                skills = []
                try:
                    key_skills_section = driver.find_element(By.ID, "skillSectionNew")
                    skill_tags = key_skills_section.find_elements(By.TAG_NAME, "a")
                    skills = [skill.text for skill in skill_tags if skill.text.strip()]
                except NoSuchElementException:
                    pass
                
                jobs_data.append({
                    'Source': 'Foundit',
                    'Job Title': job['title'],
                    'Skills': ", ".join(skills) if skills else "N/A",
                    'Job Link': job['link'],
                })
                
                print(f"    ✓ Foundit Job {idx + 1}: {job['title'][:50]}")
                
            except Exception as e:
                print(f"    ✗ Error processing Foundit job {idx + 1}: {e}")
    
    except Exception as e:
        print(f"  ❌ Error scraping Foundit: {e}")
    
    return jobs_data

def score_jobs_with_ai(jobs_data, resume_content, openai_api_key):
    """Score all jobs using AI and add ranking columns"""
    
    if not resume_content:
        print("\n⚠️ No resume content - skipping AI scoring")
        for job in jobs_data:
            job['Match %'] = 0
            job['Matching Skills'] = 'N/A'
            job['Missing Skills'] = 'N/A'
            job['Match Reason'] = 'No resume provided'
        return jobs_data
    
    if not openai_api_key:
        print("\n⚠️ No OpenAI API key - skipping AI scoring")
        for job in jobs_data:
            job['Match %'] = 0
            job['Matching Skills'] = 'N/A'
            job['Missing Skills'] = 'N/A'
            job['Match Reason'] = 'No API key provided'
        return jobs_data
    
    client = OpenAI(api_key=openai_api_key)
    
    print(f"\n🤖 AI Scoring {len(jobs_data)} jobs against your resume...")
    
    scored_jobs = []
    for idx, job in enumerate(jobs_data, 1):
        print(f"  Analyzing job {idx}/{len(jobs_data)}: {job['Job Title'][:40]}...", end='')
        
        result = calculate_match_score_with_ai(
            job['Job Title'],
            job['Skills'],
            resume_content,
            client
        )
        
        job['Match %'] = result['match_percentage']
        job['Matching Skills'] = ', '.join(result['matching_skills']) if result['matching_skills'] else 'None'
        job['Missing Skills'] = ', '.join(result['missing_skills']) if result['missing_skills'] else 'None'
        job['Match Reason'] = result['brief_reason']
        
        scored_jobs.append(job)
        print(f" ✓ {result['match_percentage']}%")
        
        time.sleep(0.5)
    
    scored_jobs.sort(key=lambda x: x['Match %'], reverse=True)
    
    print(f"\n✅ AI scoring complete! Jobs ranked by match percentage.")
    
    return scored_jobs

def create_email_body(user_id, num_jobs, top_matches):
    """Create HTML email body with job summary"""
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2c5aa0;">Your Personalized Job Matches</h2>
        <p>Hi <strong>{user_id}</strong>,</p>
        <p>We've analyzed <strong>{num_jobs}</strong> job opportunities and ranked them based on your resume.</p>
        
        <h3 style="color: #2c5aa0;">🏆 Top 3 Matches:</h3>
        <ol>
    """
    
    for i, job in enumerate(top_matches[:3], 1):
        html += f"""
            <li style="margin-bottom: 15px;">
                <strong>{job['Match %']}% Match</strong> - {job['Job Title']}<br>
                <span style="color: #666; font-size: 0.9em;">Source: {job['Source']}</span><br>
                <span style="color: #28a745; font-size: 0.9em;">Matching Skills: {job['Matching Skills'][:100]}</span>
            </li>
        """
    
    html += """
        </ol>
        <p>Please find the complete ranked list of jobs attached to this email.</p>
        <p style="color: #666; font-size: 0.9em; margin-top: 30px;">
            This is an automated email from your Job Scraper application.<br>
            Good luck with your job search!
        </p>
    </body>
    </html>
    """
    
    return html

def main():
    """Main function to process Excel input and scrape jobs"""
    
    print("=" * 70)
    print("JOB SCRAPER WITH AI MATCH SCORING & EMAIL (OpenAI + Gmail)")
    print("=" * 70)
    
    input_file = "job_profiles_template.xlsx"
    resume_file = "AI Resume.pdf"
    
    # Email configuration
    sender_email = os.getenv('GMAIL_EMAIL')  # Your Gmail address
    sender_password = os.getenv('GMAIL_APP_PASSWORD')  # Gmail App Password (not regular password!)
    if sender_email:
        print(sender_email, sender_password)
    else:
        print("No sender email found")
    
    # Get OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key:
        print("⚠️ WARNING: OPENAI_API_KEY not found. Jobs will be scraped but not scored.\n")
    
    if not sender_email or not sender_password:
        print("⚠️ WARNING: Gmail credentials not found. Excel files will be saved but not emailed.")
        print("   Set GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables to enable email.\n")
    
    resume_content = read_resume(resume_file)
    
    try:
        df_input = pd.read_excel(input_file)
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        return
    
    print("\n🚀 Starting headless browser...")
    driver = setup_chrome_driver()
    
    user_files_created = []
    
    try:
        for idx, row in df_input.iterrows():
            print(f"\n{'=' * 70}")
            print(f"PROCESSING USER {idx + 1} of {len(df_input)}")
            print(f"{'=' * 70}")
            
            user_jobs = []
            user_id = row.get('User ID', f'User_{idx + 1}')
            
            job_profiles = []
            for i in [1, 2, 3]:
                col_name = f'Job Profile {i}'
                if col_name in df_input.columns and pd.notna(row.get(col_name)):
                    job_profiles.append(row[col_name].replace(' ', '-').strip())
            
            experience = row.get('Experience Level', '')
            num_jobs = int(row.get('Number of Jobs', 10))
            location = 'India'
            
            print(f"👤 User: {user_id}")
            print(f"📋 Job Profiles: {', '.join(job_profiles)}")
            
            for job_profile in job_profiles:
                print(f"\n--- Scraping: {job_profile} ---")
                
                print(f"\n📍 Scraping NAUKRI for '{job_profile}'...")
                naukri_jobs = scrape_naukri(driver, job_profile, location, experience, num_jobs)
                user_jobs.extend(naukri_jobs)
                
                print(f"\n📍 Scraping FOUNDIT for '{job_profile}'...")
                foundit_jobs = scrape_foundit(driver, job_profile, location, experience, num_jobs)
                user_jobs.extend(foundit_jobs)
                
                print(f"\n  Total jobs scraped for '{job_profile}': {len(naukri_jobs) + len(foundit_jobs)}")
            
            if user_jobs:
                user_jobs = score_jobs_with_ai(user_jobs, resume_content, openai_api_key)
                
                df_user_output = pd.DataFrame(user_jobs)
                column_order = ['Match %', 'Source', 'Job Title', 'Skills', 'Matching Skills', 'Missing Skills', 'Match Reason', 'Job Link']
                df_user_output = df_user_output[column_order]
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_user_name = str(user_id).replace(' ', '_').replace('/', '_')
                output_filename = f'jobs_ranked_{safe_user_name}_{timestamp}.xlsx'
                
                df_user_output.to_excel(output_filename, index=False, sheet_name='Ranked Jobs')
                
                user_files_created.append({
                    'filename': output_filename,
                    'user_email': user_id,
                    'jobs': user_jobs
                })
                
                print(f"\n✅ Saved {len(user_jobs)} ranked jobs to '{output_filename}'")
                
                # Show top 3 matches
                print(f"\n🏆 Top 3 Matches for {user_id}:")
                for i, job in enumerate(user_jobs[:3], 1):
                    print(f"  {i}. {job['Match %']}% - {job['Job Title'][:50]}")
                
                # Send email if credentials are available
                if sender_email and sender_password:
                    print(f"\n📧 Sending email to {user_id}...")
                    
                    email_subject = f"Your Job Matches - {len(user_jobs)} Opportunities Ranked"
                    email_body = create_email_body(user_id, len(user_jobs), user_jobs)
                    
                    send_email_with_attachment(
                        sender_email=sender_email,
                        sender_password=sender_password,
                        recipient_email=user_id,
                        subject=email_subject,
                        body=email_body,
                        attachment_path=output_filename
                    )
                os.remove(output_filename)
            else:
                print(f"\n⚠️ No jobs found for {user_id}")
    
    finally:
        driver.quit()
        print("\n🔒 Browser closed")
    
    print("\n" + "=" * 70)
    print("SCRAPING COMPLETE!")
    print("=" * 70)
    if user_files_created:
        print(f"\n✅ Created and processed {len(user_files_created)} Excel files:")
        for file_info in user_files_created:
            print(f"   📄 {file_info['filename']}")
            if sender_email and sender_password:
                print(f"   📧 Emailed to: {file_info['user_email']}")
    else:
        print("\n❌ No files created - no jobs found!")

if __name__ == "__main__":
    main()