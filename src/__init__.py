"""
Pentagon Protocol - Schema-Guided Vibe Coding Framework
"""

from .schemas import (
    UserStory,
    UserStoriesOutput,
    DataModel,
    APIEndpoint,
    SystemDesign,
    CodeFile,
    BackendCode,
    FrontendCode,
    TestCase,
    TestReport,
    safe_parse_json,
    extract_json_from_text,
    fix_common_json_errors,
    validate_user_stories,
    validate_system_design,
    validate_backend_code,
    validate_frontend_code,
    validate_test_report,
)

from .agents import (
    get_llm,
    create_product_owner,
    create_architect,
    create_backend_engineer,
    create_frontend_engineer,
    create_qa_engineer,
    create_baseline_agent,
)

from .crew import (
    PentagonCrew,
    BaselineCrew,
)

__all__ = [
    # Schemas
    "UserStory",
    "UserStoriesOutput",
    "DataModel",
    "APIEndpoint",
    "SystemDesign",
    "CodeFile",
    "BackendCode",
    "FrontendCode",
    "TestCase",
    "TestReport",
    # Utilities
    "safe_parse_json",
    "extract_json_from_text",
    "fix_common_json_errors",
    # Guardrails
    "validate_user_stories",
    "validate_system_design",
    "validate_backend_code",
    "validate_frontend_code",
    "validate_test_report",
    # Agents
    "get_llm",
    "create_product_owner",
    "create_architect",
    "create_backend_engineer",
    "create_frontend_engineer",
    "create_qa_engineer",
    "create_baseline_agent",
    # Crews
    "PentagonCrew",
    "BaselineCrew",
]