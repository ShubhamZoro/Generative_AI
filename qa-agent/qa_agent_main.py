import os
import json
import asyncio
from typing import List, Dict, Any, TypedDict
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi as yta
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from playwright.async_api import async_playwright
import streamlit as st
from dataclasses import dataclass, asdict
import pandas as pd
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure API keys
OPENAI_API_KEY = ""

# Initialize models
llm = ChatOpenAI(temperature=0, model="gpt-4o", api_key=OPENAI_API_KEY)

# QA Agent System Prompt
QA_AGENT_PROMPT = """You are QAgenie — a calm, thorough AI QA assistant.
Your mission is to ensure flawless user experiences on Recruter.ai.
You carefully read help documents and watch training videos to understand user flows, edge cases, and expected UI behaviors.
You automatically generate complete, accurate, and maintainable frontend test cases in Playwright.
You run tests systematically, capture results, and summarize findings clearly with actionable insights.
You never skip edge cases and always consider accessibility, cross-browser compatibility, and user error handling.
You escalate ambiguous flows with clear context for clarification rather than guessing."""

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

class QAAgentState(TypedDict):
    """State for the QA Agent workflow"""
    video_url: str
    video_transcript: str
    test_cases: List[TestCase]
    playwright_scripts: List[str]
    test_results: List[TestResult]
    summary_report: str

class VideoTranscriber:
    """Handles video transcription using YouTube Transcript API"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def transcribe_video(self, video_url: str) -> str:
        """Extract detailed transcription from YouTube video"""
        try:
            # Extract video ID from URL
            if 'watch?v=' in video_url:
                vid_id = video_url.split('watch?v=')[-1].split('&')[0]
            elif 'youtu.be/' in video_url:
                vid_id = video_url.split('youtu.be/')[-1].split('?')[0]
            else:
                vid_id = video_url.split('=')[-1]
            
            self.logger.info(f"Extracting transcript for video ID: {vid_id}")
            
            # Get transcript data
            transcript_data = yta.get_transcript(vid_id)
            
            # Process transcript with timestamps for better context
            processed_transcript = []
            for entry in transcript_data:
                timestamp = entry['start']
                text = entry['text'].strip()
                if text:  # Only add non-empty text
                    minutes = int(timestamp // 60)
                    seconds = int(timestamp % 60)
                    processed_transcript.append(f"[{minutes:02d}:{seconds:02d}] {text}")
            
            # Join all text with proper spacing
            final_transcript = '\n'.join(processed_transcript)
            
            # Add metadata about the video
            metadata = f"""Video URL: {video_url}
Video ID: {vid_id}
Transcript Length: {len(transcript_data)} segments
Total Duration: ~{int(transcript_data[-1]['start'] / 60)} minutes

Detailed Transcript:
{final_transcript}
"""
            
            self.logger.info(f"Successfully extracted transcript with {len(transcript_data)} segments")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error transcribing video: {e}")
            # Fallback to basic extraction if detailed fails
            try:
                data = yta.get_transcript(vid_id)
                final_data = ''
                for val in data:
                    for key, value in val.items():
                        if key == 'text':
                            final_data += value + ' '
                return final_data.strip()
            except Exception as fallback_error:
                self.logger.error(f"Fallback transcription also failed: {fallback_error}")
                raise Exception(f"Failed to extract transcript: {str(e)}")

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import logging

logger = logging.getLogger(__name__)

class TestCaseGenerator:
    """Generates test cases from video transcript"""

    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o",api_key=OPENAI_API_KEY)

    async def generate_test_cases(self, transcript: str):
        """Generate comprehensive test cases from transcript"""

        prompt = """You are QAgenie — a calm, thorough AI QA assistant.
Your mission is to ensure flawless user experiences on Recruter.ai.
You carefully read help documents and watch training videos to understand user flows, edge cases, and expected UI behaviors.
You automatically generate complete, accurate, and maintainable frontend test cases in Playwright.
You run tests systematically, capture results, and summarize findings clearly with actionable insights.
You never skip edge cases and always consider accessibility, cross-browser compatibility, and user error handling.
You escalate ambiguous flows with clear context for clarification rather than guessing.

Based on the following video transcript of Recruter.ai, generate comprehensive test cases covering:
1. Core user flows (happy path)
2. Edge cases (invalid inputs, boundary conditions)
3. Error handling scenarios
4. Accessibility checks
5. Cross-browser compatibility tests
6. Performance considerations

Transcript:
{transcript}

Generate test cases in the following strict JSON format:
{
    "test_cases": [
        {
            "id": "TC001",
            "name": "Test case name",
            "description": "Detailed description",
            "steps": [
                {"action": "navigate", "target": "URL", "data": ""},
                {"action": "click", "target": "selector", "data": ""},
                {"action": "fill", "target": "selector", "data": "value"}
            ],
            "expected_result": "Expected outcome",
            "test_type": "core|edge_case|accessibility|performance",
            "priority": "high|medium|low"
        }
    ]
}
Only return the JSON. No markdown formatting, no explanations, no text outside the JSON."""

        messages = [
            SystemMessage(content="Respond strictly with JSON. No text, no formatting, no explanations."),
            HumanMessage(content=prompt)
        ]

        response = await self.llm.ainvoke(messages)

        logger.info("LLM raw response:")
        logger.info(response.content)

        try:
            test_data = json.loads(response.content)
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
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response content was:\n{response.content}")
            raise


class PlaywrightScriptGenerator:
    """Converts test cases to Playwright scripts"""
    
    def __init__(self):
        self.llm = llm
    
    async def generate_scripts(self, test_cases: List[TestCase]) -> List[str]:
        """Generate Playwright test scripts from test cases"""
        scripts = []
        
        for test_case in test_cases:
            prompt = f"""Convert the following test case into a Playwright Python async test script:

Test Case: {test_case.name}
Description: {test_case.description}
Steps: {json.dumps(test_case.steps, indent=2)}
Expected Result: {test_case.expected_result}

Generate a complete async Playwright test function with:
- Proper error handling
- Screenshots on failure
- Assertions for expected results
- Accessibility checks if test_type is 'accessibility'
- Performance metrics if test_type is 'performance'

Use this format:
async def test_{{function_name}}(page):
    # Test implementation
    pass
"""
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            scripts.append(response.content)
        
        return scripts

class TestExecutor:
    """Executes Playwright tests and captures results"""
    
    def __init__(self):
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
        self.screenshots_dir = self.results_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
    
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
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                record_video_dir=str(self.results_dir / "videos")
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
        elif action == 'wait':
            await page.wait_for_timeout(int(data))
        elif action == 'assert_text':
            await page.wait_for_selector(f"{target}:has-text('{data}')")
        elif action == 'screenshot':
            await page.screenshot(path=data)

class ReportGenerator:
    """Generates test execution reports"""
    
    def __init__(self):
        self.llm = llm
    
    async def generate_summary(self, test_results: List[TestResult]) -> str:
        """Generate executive summary of test results"""
        
        # Calculate statistics
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r.status == "passed"])
        failed_tests = len([r for r in test_results if r.status == "failed"])
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Create detailed report
        report = f"""# QA Test Execution Report - Recruter.ai

## Executive Summary
- **Total Tests**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {failed_tests}
- **Pass Rate**: {pass_rate:.1f}%
- **Execution Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Results Details

"""
        
        # Add individual test results
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
        
        # Add recommendations
        if failed_tests > 0:
            report += """## Recommendations
1. Review failed test cases for root cause analysis
2. Check if UI elements have changed
3. Verify test data validity
4. Consider environment-specific issues
"""
        
        return report

# Create the LangGraph workflow
def create_qa_workflow():
    """Create the QA agent workflow using LangGraph"""
    
    workflow = StateGraph(QAAgentState)
    
    # Initialize components
    transcriber = VideoTranscriber()
    test_generator = TestCaseGenerator()
    script_generator = PlaywrightScriptGenerator()
    executor = TestExecutor()
    reporter = ReportGenerator()
    
    # Define nodes
    async def transcribe_video_node(state: QAAgentState):
        """Node to transcribe video"""
        transcript = await transcriber.transcribe_video(state['video_url'])
        return {"video_transcript": transcript}
    
    async def generate_test_cases_node(state: QAAgentState):
        """Node to generate test cases"""
        test_cases = await test_generator.generate_test_cases(state['video_transcript'])
        return {"test_cases": test_cases}
    
    async def generate_scripts_node(state: QAAgentState):
        """Node to generate Playwright scripts"""
        scripts = await script_generator.generate_scripts(state['test_cases'])
        return {"playwright_scripts": scripts}
    
    async def execute_tests_node(state: QAAgentState):
        """Node to execute tests"""
        results = []
        for test_case, script in zip(state['test_cases'], state['playwright_scripts']):
            result = await executor.execute_test(test_case, script)
            results.append(result)
        return {"test_results": results}
    
    async def generate_report_node(state: QAAgentState):
        """Node to generate report"""
        report = await reporter.generate_summary(state['test_results'])
        return {"summary_report": report}
    
    # Add nodes to workflow
    workflow.add_node("transcribe", transcribe_video_node)
    workflow.add_node("generate_cases", generate_test_cases_node)
    workflow.add_node("generate_scripts", generate_scripts_node)
    workflow.add_node("execute_tests", execute_tests_node)
    workflow.add_node("generate_report", generate_report_node)
    
    # Define edges
    workflow.add_edge("transcribe", "generate_cases")
    workflow.add_edge("generate_cases", "generate_scripts")
    workflow.add_edge("generate_scripts", "execute_tests")
    workflow.add_edge("execute_tests", "generate_report")
    workflow.add_edge("generate_report", END)
    
    # Set entry point
    workflow.set_entry_point("transcribe")
    
    return workflow.compile()

# Main execution
async def main():
    """Main execution function"""
    # Initialize workflow
    qa_workflow = create_qa_workflow()
    
    # Set initial state
    initial_state = {
        "video_url": "https://www.youtube.com/watch?v=IK62Rk47aas",
        "video_transcript": "",
        "test_cases": [],
        "playwright_scripts": [],
        "test_results": [],
        "summary_report": ""
    }
    
    # Execute workflow
    logger.info("Starting QA Agent workflow...")
    final_state = await qa_workflow.ainvoke(initial_state)
    
    # Save results
    with open("test_results/test_cases.json", "w") as f:
        test_cases_dict = [asdict(tc) for tc in final_state['test_cases']]
        json.dump(test_cases_dict, f, indent=2)
    
    with open("test_results/report.md", "w") as f:
        f.write(final_state['summary_report'])
    
    logger.info("QA Agent workflow completed!")
    return final_state

if __name__ == "__main__":
    asyncio.run(main())
