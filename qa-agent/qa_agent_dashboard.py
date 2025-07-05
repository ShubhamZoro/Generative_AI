import streamlit as st
import pandas as pd
import json
from pathlib import Path
import asyncio
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from qa_agent import (
    create_qa_workflow, TestCase, TestResult, 
    VideoTranscriber, TestCaseGenerator, 
    PlaywrightScriptGenerator, TestExecutor, ReportGenerator
)
import os

# Page config
st.set_page_config(
    page_title="QAGenie - AI QA Agent",
    page_icon="🧪",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .test-passed {
        color: #28a745;
        font-weight: bold;
    }
    .test-failed {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🧪 QAGenie - AI-Powered QA Agent")
st.markdown("### Automated Test Case Generation & Execution for Recruter.ai")

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100?text=QAGenie", width=300)
    st.markdown("---")
    
    # Configuration
    st.subheader("⚙️ Configuration")
    
    # API Keys
    with st.expander("🔑 API Keys"):
        openai_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        google_key = st.text_input("Google API Key", type="password", value=os.getenv("GOOGLE_API_KEY", ""))
        
        if st.button("Save API Keys"):
            os.environ["OPENAI_API_KEY"] = openai_key
            os.environ["GOOGLE_API_KEY"] = google_key
            st.success("API Keys saved!")
    
    # Video URL
    video_url = st.text_input(
        "Video URL", 
        value="https://www.youtube.com/watch?v=IK62Rk47aas",
        help="Enter the URL of the Recruter.ai tutorial video"
    )
    
    st.markdown("---")
    
    # Actions
    st.subheader("🎬 Actions")
    
    if st.button("🚀 Run Full QA Pipeline", type="primary", use_container_width=True):
        st.session_state.run_pipeline = True
    
    if st.button("📋 Generate Test Cases Only", use_container_width=True):
        st.session_state.generate_only = True
    
    if st.button("▶️ Execute Existing Tests", use_container_width=True):
        st.session_state.execute_only = True

# Main content area
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📝 Test Cases", "🎭 Playwright Scripts", "📈 Results", "📄 Reports"])

# Tab 1: Dashboard
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    
    # Load existing results if available
    results_path = Path("test_results/test_results.json")
    if results_path.exists():
        with open(results_path, "r") as f:
            results_data = json.load(f)
            
        total_tests = len(results_data)
        passed_tests = len([r for r in results_data if r['status'] == 'passed'])
        failed_tests = len([r for r in results_data if r['status'] == 'failed'])
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        with col1:
            st.metric("Total Tests", total_tests, delta=None)
        with col2:
            st.metric("Passed", passed_tests, delta=f"{pass_rate:.1f}%")
        with col3:
            st.metric("Failed", failed_tests, delta=None)
        with col4:
            st.metric("Pass Rate", f"{pass_rate:.1f}%", delta=None)
        
        # Charts
        st.markdown("### Test Execution Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            fig_pie = px.pie(
                values=[passed_tests, failed_tests],
                names=['Passed', 'Failed'],
                title="Test Results Distribution",
                color_discrete_map={'Passed': '#28a745', 'Failed': '#dc3545'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Test types distribution
            test_types = {}
            for result in results_data:
                test_type = result.get('test_type', 'Unknown')
                test_types[test_type] = test_types.get(test_type, 0) + 1
            
            fig_bar = px.bar(
                x=list(test_types.keys()),
                y=list(test_types.values()),
                title="Test Cases by Type",
                labels={'x': 'Test Type', 'y': 'Count'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No test results found. Run the QA pipeline to generate results.")

# Tab 2: Test Cases
with tab2:
    st.markdown("### Generated Test Cases")
    
    test_cases_path = Path("test_results/test_cases.json")
    if test_cases_path.exists():
        with open(test_cases_path, "r") as f:
            test_cases = json.load(f)
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            test_type_filter = st.selectbox(
                "Filter by Type",
                ["All"] + list(set(tc['test_type'] for tc in test_cases))
            )
        with col2:
            priority_filter = st.selectbox(
                "Filter by Priority",
                ["All"] + list(set(tc['priority'] for tc in test_cases))
            )
        with col3:
            search_term = st.text_input("Search Test Cases")
        
        # Filter test cases
        filtered_cases = test_cases
        if test_type_filter != "All":
            filtered_cases = [tc for tc in filtered_cases if tc['test_type'] == test_type_filter]
        if priority_filter != "All":
            filtered_cases = [tc for tc in filtered_cases if tc['priority'] == priority_filter]
        if search_term:
            filtered_cases = [tc for tc in filtered_cases if search_term.lower() in tc['name'].lower() or search_term.lower() in tc['description'].lower()]
        
        # Display test cases
        for tc in filtered_cases:
            with st.expander(f"{tc['id']} - {tc['name']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Description:** {tc['description']}")
                    st.markdown(f"**Expected Result:** {tc['expected_result']}")
                with col2:
                    st.markdown(f"**Type:** `{tc['test_type']}`")
                    st.markdown(f"**Priority:** `{tc['priority']}`")
                
                st.markdown("**Steps:**")
                for i, step in enumerate(tc['steps'], 1):
                    st.markdown(f"{i}. **{step['action']}** on `{step['target']}` {f'with `{step['data']}`' if step.get('data') else ''}")
    else:
        st.info("No test cases found. Generate test cases first.")

# Tab 3: Playwright Scripts
with tab3:
    st.markdown("### Generated Playwright Scripts")
    
    scripts_path = Path("test_results/playwright_scripts.json")
    if scripts_path.exists():
        with open(scripts_path, "r") as f:
            scripts = json.load(f)
        
        for i, script in enumerate(scripts):
            with st.expander(f"Test Script {i+1}"):
                st.code(script['content'], language='python')
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Copy Script {i+1}", key=f"copy_{i}"):
                        st.write("Script copied to clipboard!")  # Note: Actual clipboard functionality requires JavaScript
                with col2:
                    if st.button(f"Download Script {i+1}", key=f"download_{i}"):
                        st.download_button(
                            label="Download",
                            data=script['content'],
                            file_name=f"test_script_{i+1}.py",
                            mime="text/plain"
                        )
    else:
        st.info("No Playwright scripts found. Generate test cases first.")

# Tab 4: Results
with tab4:
    st.markdown("### Test Execution Results")
    
    if results_path.exists():
        with open(results_path, "r") as f:
            results_data = json.load(f)
        
        # Convert to DataFrame for easy display
        df = pd.DataFrame(results_data)
        
        # Status filter
        status_filter = st.selectbox("Filter by Status", ["All", "Passed", "Failed"])
        if status_filter != "All":
            df = df[df['status'] == status_filter.lower()]
        
        # Display results
        for _, result in df.iterrows():
            status_color = "test-passed" if result['status'] == 'passed' else "test-failed"
            
            with st.expander(f"{result['test_name']} - {result['status'].upper()}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Test ID:** {result['test_case_id']}")
                    st.markdown(f"**Status:** <span class='{status_color}'>{result['status'].upper()}</span>", unsafe_allow_html=True)
                    if result.get('error_message'):
                        st.error(f"**Error:** {result['error_message']}")
                
                with col2:
                    st.markdown(f"**Duration:** {result['duration']:.2f}s")
                    st.markdown(f"**Timestamp:** {result['timestamp']}")
                
                with col3:
                    if result.get('screenshot_path') and Path(result['screenshot_path']).exists():
                        st.image(result['screenshot_path'], caption="Screenshot", width=200)
    else:
        st.info("No test results found. Execute tests first.")

# Tab 5: Reports
with tab5:
    st.markdown("### Test Execution Reports")
    
    report_path = Path("test_results/report.md")
    if report_path.exists():
        with open(report_path, "r") as f:
            report_content = f.read()
        
        # Display report
        st.markdown(report_content)
        
        # Download options
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="📥 Download Markdown Report",
                data=report_content,
                file_name=f"qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        
        with col2:
            # Convert to PDF would require additional library
            st.button("📄 Export as PDF", disabled=True, help="PDF export coming soon")
        
        with col3:
            # Email functionality would require SMTP setup
            st.button("📧 Email Report", disabled=True, help="Email functionality coming soon")
    else:
        st.info("No reports found. Run the full pipeline to generate reports.")

# Pipeline execution
async def run_pipeline(video_url: str):
    """Run the complete QA pipeline"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize workflow
        qa_workflow = create_qa_workflow()
        
        # Set initial state
        initial_state = {
            "video_url": video_url,
            "video_transcript": "",
            "test_cases": [],
            "playwright_scripts": [],
            "test_results": [],
            "summary_report": ""
        }
        
        # Execute workflow steps
        status_text.text("🎥 Transcribing video...")
        progress_bar.progress(20)
        
        # Run the workflow
        final_state = await qa_workflow.ainvoke(initial_state)
        
        progress_bar.progress(100)
        status_text.text("✅ Pipeline completed successfully!")
        
        # Save results
        save_results(final_state)
        
        return final_state
        
    except Exception as e:
        st.error(f"Pipeline execution failed: {str(e)}")
        return None

def save_results(state):
    """Save all results to files"""
    results_dir = Path("test_results")
    results_dir.mkdir(exist_ok=True)
    
    # Save test cases
    with open(results_dir / "test_cases.json", "w") as f:
        test_cases_dict = [tc.__dict__ if hasattr(tc, '__dict__') else tc for tc in state['test_cases']]
        json.dump(test_cases_dict, f, indent=2)
    
    # Save scripts
    with open(results_dir / "playwright_scripts.json", "w") as f:
        scripts_data = [{"content": script} for script in state['playwright_scripts']]
        json.dump(scripts_data, f, indent=2)
    
    # Save test results
    with open(results_dir / "test_results.json", "w") as f:
        results_dict = [result.__dict__ if hasattr(result, '__dict__') else result for result in state['test_results']]
        json.dump(results_dict, f, indent=2)
    
    # Save report
    with open(results_dir / "report.md", "w") as f:
        f.write(state['summary_report'])

# Handle button clicks
if st.session_state.get('run_pipeline'):
    with st.spinner("Running complete QA pipeline..."):
        asyncio.run(run_pipeline(video_url))
    st.session_state.run_pipeline = False
    st.rerun()

if st.session_state.get('generate_only'):
    with st.spinner("Generating test cases..."):
        # Run only test case generation
        asyncio.run(generate_test_cases_only(video_url))
    st.session_state.generate_only = False
    st.rerun()

if st.session_state.get('execute_only'):
    with st.spinner("Executing tests..."):
        # Run only test execution
        asyncio.run(execute_tests_only())
    st.session_state.execute_only = False
    st.rerun()

# Helper functions for partial execution
async def generate_test_cases_only(video_url: str):
    """Generate only test cases without execution"""
    transcriber = VideoTranscriber()
    generator = TestCaseGenerator()
    
    # Transcribe video
    transcript = await transcriber.transcribe_video(video_url)
    
    # Generate test cases
    test_cases = await generator.generate_test_cases(transcript)
    
    # Save test cases
    results_dir = Path("test_results")
    results_dir.mkdir(exist_ok=True)
    
    with open(results_dir / "test_cases.json", "w") as f:
        test_cases_dict = [tc.__dict__ for tc in test_cases]
        json.dump(test_cases_dict, f, indent=2)
    
    st.success(f"Generated {len(test_cases)} test cases!")

async def execute_tests_only():
    """Execute existing test cases"""
    test_cases_path = Path("test_results/test_cases.json")
    
    if not test_cases_path.exists():
        st.error("No test cases found. Generate test cases first!")
        return
    
    with open(test_cases_path, "r") as f:
        test_cases_data = json.load(f)
    
    # Convert back to TestCase objects
    test_cases = []
    for tc_data in test_cases_data:
        test_cases.append(TestCase(**tc_data))
    
    # Generate scripts and execute
    script_generator = PlaywrightScriptGenerator()
    executor = TestExecutor()
    
    scripts = await script_generator.generate_scripts(test_cases)
    
    results = []
    for test_case, script in zip(test_cases, scripts):
        result = await executor.execute_test(test_case, script)
        results.append(result)
    
    # Save results
    results_dir = Path("test_results")
    with open(results_dir / "test_results.json", "w") as f:
        results_dict = [result.__dict__ for result in results]
        json.dump(results_dict, f, indent=2)
    
    st.success(f"Executed {len(results)} tests!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Built with ❤️ by QAGenie | Powered by LangGraph, LangChain, and Playwright</p>
    </div>
    """,
    unsafe_allow_html=True
)