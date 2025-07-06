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