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
