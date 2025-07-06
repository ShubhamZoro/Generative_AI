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