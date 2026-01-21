"""
Pentagon Protocol - Enhanced Task Definitions
With guardrails and structured output enforcement
"""
from typing import List
from crewai import Task, Agent
from .schemas import (
    UserStoriesOutput, SystemDesign, BackendCode, FrontendCode, TestReport,
    validate_user_stories, validate_system_design, validate_backend_code,
    validate_frontend_code, validate_test_report
)


# ============================================================
# TASK TEMPLATES WITH STRICT JSON REQUIREMENTS
# ============================================================

def create_user_stories_task(agent: Agent, vibe_prompt: str) -> Task:
    """Create Product Owner task for generating user stories."""
    return Task(
        description=f"""You are the Product Owner. Analyze this vibe prompt and create user stories.

Vibe Prompt: {vibe_prompt}

Return ONLY this JSON structure (no markdown, no extra text):
{{
    "stories": [
        {{
            "id": "US001",
            "title": "Short title",
            "description": "As a user, I want X so that Y",
            "priority": "high"
        }}
    ],
    "summary": "Brief project summary"
}}

CRITICAL RULES:
- Return ONLY valid JSON
- Create 5-10 user stories MAXIMUM (focus on core features)
- Keep descriptions under 100 characters
- Priority must be: high, medium, or low
- No markdown, no code blocks, no extra text""",
        expected_output="""Valid JSON with stories array and summary""",
        agent=agent,
        output_json=UserStoriesOutput,
    )


def create_system_design_task(agent: Agent, context_tasks: List[Task]) -> Task:
    """Create Architect task for system design."""
    return Task(
        description="""You are the Architect. Design a simple system based on the user stories.

Return ONLY this JSON structure (no markdown, no extra text):
{
    "models": [
        {
            "name": "Item",
            "fields": ["id: int", "name: str", "created_at: datetime"]
        }
    ],
    "endpoints": [
        {
            "method": "GET",
            "path": "/api/items",
            "description": "Get all items"
        }
    ],
    "architecture_notes": "Brief notes"
}

CRITICAL RULES:
- Return ONLY valid JSON
- Create 2-4 data models MAXIMUM
- Create 5-8 API endpoints MAXIMUM (core CRUD operations only)
- Keep descriptions under 50 characters
- No markdown, no code blocks, no extra text""",
        expected_output="""Valid JSON with models, endpoints, and architecture_notes""",
        agent=agent,
        context=context_tasks,
        output_json=SystemDesign,
    )


def create_backend_task(agent: Agent, context_tasks: List[Task]) -> Task:
    """Create Backend Engineer task for writing backend code."""
    return Task(
        description="""You are the Backend Engineer. Write a MINIMAL FastAPI backend.

Return ONLY this JSON structure (no markdown, no extra text):
{
    "files": [
        {
            "filename": "main.py",
            "content": "from fastapi import FastAPI\\napp = FastAPI()\\n...",
            "description": "Main FastAPI app"
        }
    ],
    "setup_instructions": "pip install fastapi uvicorn && uvicorn main:app --reload"
}

CRITICAL RULES:
- Return ONLY valid JSON
- ESCAPE all newlines as \\n
- ESCAPE all quotes as \\"
- ESCAPE all backslashes as \\\\
- Create ONLY main.py (single file)
- Keep code under 40 lines
- Use simple in-memory dict storage
- Include CORS middleware
- Implement only 3-4 core endpoints
- No complex validation, no database
- No markdown, no code blocks""",
        expected_output="""Valid JSON with files array and setup_instructions""",
        agent=agent,
        context=context_tasks,
        output_json=BackendCode,
    )


def create_frontend_task(agent: Agent, context_tasks: List[Task]) -> Task:
    """Create Frontend Engineer task for writing frontend code."""
    return Task(
        description="""You are the Frontend Engineer. Write a MINIMAL HTML/JS frontend.

Return ONLY this JSON structure (no markdown, no extra text):
{
    "files": [
        {
            "filename": "index.html",
            "content": "<!DOCTYPE html>\\n<html>\\n...",
            "description": "Main HTML page"
        }
    ],
    "setup_instructions": "Open index.html in browser"
}

CRITICAL RULES:
- Return ONLY valid JSON
- ESCAPE all newlines as \\n
- ESCAPE all quotes as \\"
- ESCAPE all backslashes as \\\\
- Create ONLY index.html (single file with inline CSS/JS)
- Keep code under 50 lines
- Use fetch() for API calls
- Simple, functional UI only
- No frameworks, no external dependencies
- No markdown, no code blocks""",
        expected_output="""Valid JSON with files array and setup_instructions""",
        agent=agent,
        context=context_tasks,
        output_json=FrontendCode,
    )


def create_qa_task(agent: Agent, context_tasks: List[Task]) -> Task:
    """Create QA Engineer task for validation."""
    return Task(
        description="""You are the QA Engineer. Validate the implementation.

Return ONLY this JSON structure (no markdown, no extra text):
{
    "overall_status": "pass",
    "test_cases": [
        {
            "id": "TC001",
            "description": "Test description",
            "status": "pass",
            "notes": "",
            "responsible_agent": ""
        }
    ],
    "summary": "Brief summary",
    "recommendations": [],
    "issues_by_agent": {
        "product_owner": [],
        "architect": [],
        "backend_engineer": [],
        "frontend_engineer": []
    }
}

CRITICAL RULES:
- Return ONLY valid JSON
- Create 3-5 test cases MAXIMUM
- For FAILED tests, set responsible_agent to one of: product_owner, architect, backend_engineer, frontend_engineer
- overall_status: "pass" if all tests pass, "fail" if any fail
- Keep descriptions under 50 characters
- No markdown, no code blocks""",
        expected_output="""Valid JSON with overall_status, test_cases, summary, recommendations, and issues_by_agent""",
        agent=agent,
        context=context_tasks,
        output_json=TestReport,
    )


def create_baseline_task(agent: Agent, vibe_prompt: str) -> Task:
    """Create single baseline task for comparison."""
    return Task(
        description=f"""Build a complete application for this requirement:

VIBE PROMPT: "{vibe_prompt}"

Return ONLY this JSON structure:
{{
    "user_stories": [
        {{"id": "US001", "title": "Feature", "description": "As a user...", "priority": "high"}}
    ],
    "backend_code": "from fastapi import FastAPI\\napp = FastAPI()\\n...",
    "frontend_code": "<!DOCTYPE html>\\n<html>...</html>",
    "test_summary": "pass"
}}

RULES:
- Return ONLY valid JSON
- ESCAPE all newlines as \\n
- Keep code under 50 lines each
- Use simple implementations
""",
        expected_output="A valid JSON object with user_stories, backend_code, frontend_code, and test_summary",
        agent=agent,
        guardrail_max_retries=5,
    )
