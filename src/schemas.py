"""
Pentagon Protocol - Robust Pydantic Schemas
Simplified schemas with better defaults, validation, and truncation recovery
"""

import re
import json
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any, Tuple, Dict
from datetime import datetime


# ============================================================
# UTILITY FUNCTIONS FOR ROBUST JSON PARSING
# ============================================================

def extract_json_from_text(text: str) -> Optional[str]:
    """Extract JSON from text with multiple strategies."""
    if not text:
        return None
    
    # Strategy 1: Text is already valid JSON
    text = text.strip()
    if text.startswith('{') and text.endswith('}'):
        return text
    if text.startswith('[') and text.endswith(']'):
        return text
    
    # Strategy 2: Extract from markdown code blocks
    patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
        r'`([\s\S]*?)`',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        for match in matches:
            match = match.strip()
            if match.startswith('{') or match.startswith('['):
                return match
    
    # Strategy 3: Find JSON object in text
    brace_start = text.find('{')
    brace_end = text.rfind('}')
    if brace_start != -1 and brace_end > brace_start:
        return text[brace_start:brace_end + 1]
    
    # Strategy 4: Find JSON array
    bracket_start = text.find('[')
    bracket_end = text.rfind(']')
    if bracket_start != -1 and bracket_end > bracket_start:
        return text[bracket_start:bracket_end + 1]
    
    return None


def fix_common_json_errors(json_str: str) -> str:
    """Fix common JSON formatting errors from LLMs."""
    if not json_str:
        return json_str
    
    # Remove control characters
    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_str)
    
    # Fix trailing commas
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    # Fix unquoted keys (simple cases)
    json_str = re.sub(r'(\{|\,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
    
    # Fix single quotes to double quotes (careful with apostrophes)
    if re.search(r"'\w+':", json_str):
        json_str = re.sub(r"'([^']+)':", r'"\1":', json_str)
    
    return json_str


def repair_truncated_json(json_str: str) -> str:
    """Attempt to repair truncated JSON by closing open structures."""
    if not json_str:
        return json_str
    
    # Count open brackets and braces
    open_braces = json_str.count('{') - json_str.count('}')
    open_brackets = json_str.count('[') - json_str.count(']')
    
    # Check if we're inside a string (unmatched quotes)
    in_string = False
    escaped = False
    for char in json_str:
        if escaped:
            escaped = False
            continue
        if char == '\\':
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
    
    # If inside a string, close it
    if in_string:
        json_str += '"'
    
    # Remove trailing comma if present
    json_str = re.sub(r',\s*$', '', json_str)
    
    # Close open brackets and braces
    json_str += ']' * open_brackets
    json_str += '}' * open_braces
    
    return json_str


def extract_complete_array_items(json_str: str, array_key: str, item_pattern: str) -> List[Dict]:
    """Extract complete items from a potentially truncated array."""
    items = []
    
    # Find the array
    array_match = re.search(rf'"{array_key}"\s*:\s*\[', json_str)
    if not array_match:
        return items
    
    # Extract items using the pattern
    for match in re.finditer(item_pattern, json_str):
        try:
            item_str = match.group(0)
            # Try to parse as JSON
            item = json.loads(item_str)
            items.append(item)
        except json.JSONDecodeError:
            continue
    
    return items


def safe_parse_json(text: str, model_class: Optional[type] = None) -> Tuple[bool, Any]:
    """
    Safely parse JSON with multiple fallback strategies including truncation recovery.
    Returns (success, result_or_error)
    """
    if not text:
        return False, "Empty input"
    
    # Step 1: Extract JSON from text
    json_str = extract_json_from_text(text)
    if not json_str:
        return False, "No JSON found in text"
    
    # Step 2: Try parsing as-is
    try:
        data = json.loads(json_str)
        if model_class:
            return True, model_class.model_validate(data)
        return True, data
    except (json.JSONDecodeError, Exception):
        pass
    
    # Step 3: Fix common errors and retry
    fixed_json = fix_common_json_errors(json_str)
    try:
        data = json.loads(fixed_json)
        if model_class:
            return True, model_class.model_validate(data)
        return True, data
    except (json.JSONDecodeError, Exception):
        pass
    
    # Step 4: Repair truncated JSON and retry
    repaired_json = repair_truncated_json(fixed_json)
    try:
        data = json.loads(repaired_json)
        if model_class:
            return True, model_class.model_validate(data)
        return True, data
    except (json.JSONDecodeError, Exception):
        pass
    
    # Step 5: Try model-specific recovery
    if model_class:
        recovered = recover_truncated_output(text, model_class)
        if recovered:
            return True, recovered
    
    return False, f"Failed to parse JSON after all attempts"


def recover_truncated_output(text: str, model_class: type) -> Optional[Any]:
    """
    Attempt to recover valid data from truncated output based on model type.
    """
    try:
        if model_class == UserStoriesOutput:
            return _recover_user_stories(text)
        elif model_class == SystemDesign:
            return _recover_system_design(text)
        elif model_class == BackendCode:
            return _recover_backend_code(text)
        elif model_class == FrontendCode:
            return _recover_frontend_code(text)
        elif model_class == TestReport:
            return _recover_test_report(text)
    except Exception:
        pass
    return None


def _recover_user_stories(text: str) -> Optional['UserStoriesOutput']:
    """Recover user stories from truncated output."""
    # Pattern for complete user story objects
    story_pattern = r'\{\s*"id"\s*:\s*"([^"]+)"\s*,\s*"title"\s*:\s*"([^"]+)"\s*,\s*"description"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"priority"\s*:\s*"([^"]+)"\s*\}'
    
    stories = []
    for match in re.finditer(story_pattern, text):
        stories.append({
            "id": match.group(1),
            "title": match.group(2),
            "description": match.group(3).replace('\\"', '"').replace('\\n', '\n'),
            "priority": match.group(4)
        })
    
    if stories:
        # Extract summary if available
        summary_match = re.search(r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        summary = summary_match.group(1) if summary_match else ""
        
        return UserStoriesOutput(
            stories=[UserStory(**s) for s in stories],
            summary=summary
        )
    return None


def _recover_system_design(text: str) -> Optional['SystemDesign']:
    """Recover system design from truncated output."""
    # Pattern for complete model objects
    model_pattern = r'\{\s*"name"\s*:\s*"([^"]+)"\s*,\s*"fields"\s*:\s*\[((?:[^\]]*)?)\]\s*\}'
    
    models = []
    for match in re.finditer(model_pattern, text):
        fields_str = match.group(2)
        fields = re.findall(r'"([^"]+)"', fields_str)
        models.append({
            "name": match.group(1),
            "fields": fields
        })
    
    # Pattern for complete endpoint objects
    endpoint_pattern = r'\{\s*"method"\s*:\s*"([^"]+)"\s*,\s*"path"\s*:\s*"([^"]+)"\s*,\s*"description"\s*:\s*"((?:[^"\\]|\\.)*)"\s*\}'
    
    endpoints = []
    for match in re.finditer(endpoint_pattern, text):
        endpoints.append({
            "method": match.group(1),
            "path": match.group(2),
            "description": match.group(3).replace('\\"', '"')
        })
    
    if models or endpoints:
        # Extract architecture_notes if available
        notes_match = re.search(r'"architecture_notes"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        notes = notes_match.group(1) if notes_match else ""
        
        return SystemDesign(
            models=[DataModel(**m) for m in models] if models else [DataModel(name="Item", fields=["id: int", "name: str"])],
            endpoints=[APIEndpoint(**e) for e in endpoints] if endpoints else [APIEndpoint(method="GET", path="/api/items", description="Get all items")],
            architecture_notes=notes
        )
    return None


def _recover_backend_code(text: str) -> Optional['BackendCode']:
    """Recover backend code from truncated output."""
    # Pattern for complete file objects - more flexible
    file_pattern = r'\{\s*"filename"\s*:\s*"([^"]+)"\s*,\s*"content"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"description"\s*:\s*"((?:[^"\\]|\\.)*)"\s*\}'
    
    files = []
    for match in re.finditer(file_pattern, text, re.DOTALL):
        content = match.group(2)
        # Unescape the content
        content = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
        files.append({
            "filename": match.group(1),
            "content": content,
            "description": match.group(3)
        })
    
    # If no files found with description, try without description
    if not files:
        file_pattern_simple = r'\{\s*"filename"\s*:\s*"([^"]+)"\s*,\s*"content"\s*:\s*"((?:[^"\\]|\\.)*)"'
        for match in re.finditer(file_pattern_simple, text, re.DOTALL):
            content = match.group(2)
            content = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
            files.append({
                "filename": match.group(1),
                "content": content,
                "description": ""
            })
    
    if files:
        # Check if we have main.py
        has_main = any('main' in f['filename'].lower() for f in files)
        if has_main:
            # Extract setup_instructions if available
            setup_match = re.search(r'"setup_instructions"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
            setup = setup_match.group(1) if setup_match else "pip install fastapi uvicorn && uvicorn main:app --reload"
            
            return BackendCode(
                files=[CodeFile(**f) for f in files],
                setup_instructions=setup
            )
    return None


def _recover_frontend_code(text: str) -> Optional['FrontendCode']:
    """Recover frontend code from truncated output."""
    # Pattern for complete file objects
    file_pattern = r'\{\s*"filename"\s*:\s*"([^"]+)"\s*,\s*"content"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"description"\s*:\s*"((?:[^"\\]|\\.)*)"\s*\}'
    
    files = []
    for match in re.finditer(file_pattern, text, re.DOTALL):
        content = match.group(2)
        content = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
        files.append({
            "filename": match.group(1),
            "content": content,
            "description": match.group(3)
        })
    
    # If no files found with description, try without description
    if not files:
        file_pattern_simple = r'\{\s*"filename"\s*:\s*"([^"]+)"\s*,\s*"content"\s*:\s*"((?:[^"\\]|\\.)*)"'
        for match in re.finditer(file_pattern_simple, text, re.DOTALL):
            content = match.group(2)
            content = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
            files.append({
                "filename": match.group(1),
                "content": content,
                "description": ""
            })
    
    if files:
        # Check if we have index.html
        has_index = any('index' in f['filename'].lower() for f in files)
        if has_index:
            setup_match = re.search(r'"setup_instructions"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
            setup = setup_match.group(1) if setup_match else "Open index.html in browser"
            
            return FrontendCode(
                files=[CodeFile(**f) for f in files],
                setup_instructions=setup
            )
    return None


def _recover_test_report(text: str) -> Optional['TestReport']:
    """Recover test report from truncated output."""
    # Pattern for complete test case objects
    tc_pattern = r'\{\s*"id"\s*:\s*"([^"]+)"\s*,\s*"description"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"status"\s*:\s*"([^"]+)"\s*,\s*"notes"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"responsible_agent"\s*:\s*"([^"]*)"\s*\}'
    
    test_cases = []
    for match in re.finditer(tc_pattern, text):
        test_cases.append({
            "id": match.group(1),
            "description": match.group(2).replace('\\"', '"'),
            "status": match.group(3),
            "notes": match.group(4).replace('\\"', '"'),
            "responsible_agent": match.group(5)
        })
    
    # Try simpler pattern if no matches
    if not test_cases:
        tc_pattern_simple = r'\{\s*"id"\s*:\s*"([^"]+)"\s*,\s*"description"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"status"\s*:\s*"([^"]+)"'
        for match in re.finditer(tc_pattern_simple, text):
            test_cases.append({
                "id": match.group(1),
                "description": match.group(2).replace('\\"', '"'),
                "status": match.group(3),
                "notes": "",
                "responsible_agent": ""
            })
    
    if test_cases:
        # Extract overall_status
        status_match = re.search(r'"overall_status"\s*:\s*"([^"]+)"', text)
        overall_status = status_match.group(1) if status_match else "needs_review"
        
        # Extract summary
        summary_match = re.search(r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        summary = summary_match.group(1) if summary_match else ""
        
        # Extract recommendations
        recommendations = []
        rec_match = re.search(r'"recommendations"\s*:\s*\[((?:[^\]]*)?)\]', text)
        if rec_match:
            recommendations = re.findall(r'"([^"]+)"', rec_match.group(1))
        
        # Extract issues_by_agent
        issues_by_agent = {
            "product_owner": [],
            "architect": [],
            "backend_engineer": [],
            "frontend_engineer": []
        }
        
        return TestReport(
            overall_status=overall_status,
            test_cases=[TestCase(**tc) for tc in test_cases],
            summary=summary,
            recommendations=recommendations,
            issues_by_agent=issues_by_agent
        )
    return None


# ============================================================
# SIMPLIFIED SCHEMAS - Easier for LLMs to generate
# ============================================================

class UserStory(BaseModel):
    """Single user story - simplified"""
    id: str = Field(description="Unique ID like US001")
    title: str = Field(description="Short title")
    description: str = Field(description="As a user, I want...")
    priority: str = Field(default="medium", description="high/medium/low")
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        v = v.lower().strip()
        if v not in ['high', 'medium', 'low']:
            return 'medium'
        return v


class UserStoriesOutput(BaseModel):
    """Output from Product Owner"""
    stories: List[UserStory] = Field(description="List of user stories")
    summary: str = Field(default="", description="Brief summary")


class APIEndpoint(BaseModel):
    """API endpoint definition - simplified"""
    method: str = Field(description="GET/POST/PUT/DELETE")
    path: str = Field(description="URL path like /api/items")
    description: str = Field(description="What this endpoint does")
    
    @field_validator('method')
    @classmethod
    def validate_method(cls, v):
        v = v.upper().strip()
        if v not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            return 'GET'
        return v


class DataModel(BaseModel):
    """Data model definition - simplified"""
    name: str = Field(description="Model name like Task, User")
    fields: List[str] = Field(description="List of field names with types, e.g., 'id: int', 'name: str'")


class SystemDesign(BaseModel):
    """Output from Architect"""
    models: List[DataModel] = Field(description="Data models")
    endpoints: List[APIEndpoint] = Field(description="API endpoints")
    architecture_notes: str = Field(default="", description="Additional notes")


class CodeFile(BaseModel):
    """Single code file - simplified"""
    filename: str = Field(description="File name like main.py")
    content: str = Field(description="The actual code")
    description: str = Field(default="", description="What this file does")


class BackendCode(BaseModel):
    """Output from Backend Engineer"""
    files: List[CodeFile] = Field(description="List of code files")
    setup_instructions: str = Field(default="pip install fastapi uvicorn", description="How to run")


class FrontendCode(BaseModel):
    """Output from Frontend Engineer"""
    files: List[CodeFile] = Field(description="List of frontend files")
    setup_instructions: str = Field(default="Open index.html in browser", description="How to run")


class TestCase(BaseModel):
    """Single test case - simplified"""
    id: str = Field(description="Test ID like TC001")
    description: str = Field(description="What is being tested")
    status: str = Field(description="pass/fail/skip")
    notes: str = Field(default="", description="Additional notes")
    responsible_agent: str = Field(
        default="", 
        description="Agent responsible for this test case: product_owner, architect, backend_engineer, or frontend_engineer"
    )
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        v = v.lower().strip()
        if v not in ['pass', 'fail', 'skip', 'passed', 'failed', 'skipped']:
            return 'skip'
        if v == 'passed':
            return 'pass'
        if v in ['failed', 'skipped']:
            return v.replace('ed', '')
        return v
    
    @field_validator('responsible_agent')
    @classmethod
    def validate_responsible_agent(cls, v):
        v = v.lower().strip()
        valid_agents = ['product_owner', 'architect', 'backend_engineer', 'frontend_engineer', '']
        if v not in valid_agents:
            return ''
        return v


class TestReport(BaseModel):
    """Output from QA Engineer"""
    overall_status: str = Field(description="pass/fail/needs_review")
    test_cases: List[TestCase] = Field(description="List of test results")
    summary: str = Field(default="", description="Overall summary")
    recommendations: List[str] = Field(default_factory=list, description="Improvement suggestions")
    issues_by_agent: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "product_owner": [],
            "architect": [],
            "backend_engineer": [],
            "frontend_engineer": []
        },
        description="Issues categorized by responsible agent"
    )
    
    @field_validator('overall_status')
    @classmethod
    def validate_overall_status(cls, v):
        v = v.lower().strip()
        if v not in ['pass', 'fail', 'needs_review', 'passed', 'failed']:
            return 'needs_review'
        if v == 'passed':
            return 'pass'
        if v == 'failed':
            return 'fail'
        return v


# ============================================================
# GUARDRAIL FUNCTIONS
# ============================================================

def validate_user_stories(result) -> Tuple[bool, Any]:
    """Guardrail for user stories output."""
    try:
        raw = result.raw if hasattr(result, 'raw') else str(result)
        success, parsed = safe_parse_json(raw, UserStoriesOutput)
        
        if not success:
            return (False, f"Invalid JSON format: {parsed}. Please return valid JSON matching the schema.")
        
        if not parsed.stories or len(parsed.stories) == 0:
            return (False, "No user stories found. Please include at least 1 user story.")
        
        # Validate each story has required fields
        for story in parsed.stories:
            if not story.id or not story.title or not story.description:
                return (False, f"User story {story.id or 'unknown'} is missing required fields (id, title, description).")
        
        return (True, parsed.model_dump_json())
    except Exception as e:
        return (False, f"Validation error: {str(e)}. Please return valid JSON.")


def validate_system_design(result) -> Tuple[bool, Any]:
    """Guardrail for system design output."""
    try:
        raw = result.raw if hasattr(result, 'raw') else str(result)
        success, parsed = safe_parse_json(raw, SystemDesign)
        
        if not success:
            return (False, f"Invalid JSON format: {parsed}. Please return valid JSON matching the schema.")
        
        if not parsed.models:
            return (False, "No data models defined. Please include at least 1 data model.")
        
        if not parsed.endpoints:
            return (False, "No API endpoints defined. Please include at least 1 endpoint.")
        
        # Validate each model has required fields
        for model in parsed.models:
            if not model.name or not model.fields:
                return (False, f"Data model {model.name or 'unknown'} is missing required fields (name, fields).")
        
        # Validate each endpoint has required fields
        for endpoint in parsed.endpoints:
            if not endpoint.method or not endpoint.path or not endpoint.description:
                return (False, f"Endpoint {endpoint.path or 'unknown'} is missing required fields (method, path, description).")
        
        return (True, parsed.model_dump_json())
    except Exception as e:
        return (False, f"Validation error: {str(e)}. Please return valid JSON.")


def validate_backend_code(result) -> Tuple[bool, Any]:
    """Guardrail for backend code output."""
    try:
        raw = result.raw if hasattr(result, 'raw') else str(result)
        success, parsed = safe_parse_json(raw, BackendCode)
        
        if not success:
            return (False, f"Invalid JSON format: {parsed}. Please return valid JSON with smaller files (under 50 lines each).")
        
        if not parsed.files:
            return (False, "No code files provided. Please include at least main.py.")
        
        # Check that main.py exists
        has_main = any('main' in f.filename.lower() for f in parsed.files)
        if not has_main:
            return (False, "Missing main.py file. Please include a main.py file.")
        
        # Validate each file has required fields
        for file in parsed.files:
            if not file.filename or not file.content:
                return (False, f"Code file {file.filename or 'unknown'} is missing required fields (filename, content).")
        
        return (True, parsed.model_dump_json())
    except Exception as e:
        return (False, f"Validation error: {str(e)}. Please return valid JSON with smaller code files.")


def validate_frontend_code(result) -> Tuple[bool, Any]:
    """Guardrail for frontend code output."""
    try:
        raw = result.raw if hasattr(result, 'raw') else str(result)
        success, parsed = safe_parse_json(raw, FrontendCode)
        
        if not success:
            return (False, f"Invalid JSON format: {parsed}. Please return valid JSON with smaller files.")
        
        if not parsed.files:
            return (False, "No frontend files provided. Please include at least index.html.")
        
        # Check that index.html exists
        has_index = any('index' in f.filename.lower() for f in parsed.files)
        if not has_index:
            return (False, "Missing index.html file. Please include an index.html file.")
        
        # Validate each file has required fields
        for file in parsed.files:
            if not file.filename or not file.content:
                return (False, f"Frontend file {file.filename or 'unknown'} is missing required fields (filename, content).")
        
        return (True, parsed.model_dump_json())
    except Exception as e:
        return (False, f"Validation error: {str(e)}. Please return valid JSON with smaller files.")


def validate_test_report(result) -> Tuple[bool, Any]:
    """Guardrail for test report output."""
    try:
        raw = result.raw if hasattr(result, 'raw') else str(result)
        success, parsed = safe_parse_json(raw, TestReport)
        
        if not success:
            return (False, f"Invalid JSON format: {parsed}. Please return valid JSON matching the schema.")
        
        if not parsed.test_cases:
            return (False, "No test cases provided. Please include at least 1 test case.")
        
        # Validate each test case has required fields
        for tc in parsed.test_cases:
            if not tc.id or not tc.description or not tc.status:
                return (False, f"Test case {tc.id or 'unknown'} is missing required fields (id, description, status).")
        
        # Validate that failed test cases have responsible_agent
        failed_without_agent = [
            tc for tc in parsed.test_cases 
            if tc.status == 'fail' and not tc.responsible_agent
        ]
        if failed_without_agent:
            tc_ids = ", ".join(tc.id for tc in failed_without_agent)
            return (False, f"Failed test cases missing responsible_agent: {tc_ids}. Please specify which agent (product_owner, architect, backend_engineer, frontend_engineer) is responsible for each failed test.")
        
        # Validate responsible_agent values are valid
        valid_agents = ['product_owner', 'architect', 'backend_engineer', 'frontend_engineer', '']
        for tc in parsed.test_cases:
            if tc.responsible_agent and tc.responsible_agent not in valid_agents:
                return (False, f"Test case {tc.id} has invalid responsible_agent: {tc.responsible_agent}. Must be one of: product_owner, architect, backend_engineer, frontend_engineer.")
        
        # Validate consistency: if overall_status is 'pass', there should be no failed test cases
        if parsed.overall_status == 'pass':
            failed_tests = [tc for tc in parsed.test_cases if tc.status == 'fail']
            if failed_tests:
                return (False, f"overall_status is 'pass' but there are {len(failed_tests)} failed test cases. Please set overall_status to 'fail' or fix the test case statuses.")
        
        return (True, parsed.model_dump_json())
    except Exception as e:
        return (False, f"Validation error: {str(e)}. Please return valid JSON.")
