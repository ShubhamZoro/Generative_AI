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
