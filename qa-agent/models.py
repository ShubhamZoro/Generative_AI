from dataclasses import dataclass, asdict
from typing import List, Dict, Any, TypedDict
from datetime import datetime

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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        """Create from dictionary"""
        return cls(**data)

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
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestResult":
        """Create from dictionary"""
        return cls(**data)

class QAAgentState(TypedDict):
    """State for the QA Agent workflow"""
    video_url: str
    video_transcript: str
    test_cases: List[TestCase]
    playwright_scripts: List[str]
    test_results: List[TestResult]
    summary_report: str
    recruter_test_result: TestResult
