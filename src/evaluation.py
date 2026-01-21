"""
Pentagon Protocol - Comprehensive Evaluation Framework
Evaluates experiment results from the Pentagon vs Baseline comparison
Includes expected features verification from VibePrompts dataset
"""

import os
import json
import ast
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
load_dotenv()

# ============================================
# DeepSeek Client Setup
# ============================================

def get_deepseek_client():
    """Get OpenAI-compatible client configured for DeepSeek."""
    from openai import OpenAI
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError(
            "DEEPSEEK_API_KEY not found. Please set it in your .env file."
        )
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

def llm_call(prompt: str, max_tokens: int = 1000) -> str:
    """Make a call to DeepSeek API."""
    try:
        client = get_deepseek_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM call failed: {e}")
        return ""

# ============================================
# Load VibePrompts Dataset
# ============================================

def load_vibe_prompts(prompts_file: str) -> Dict[str, Dict[str, Any]]:
    """Load VibePrompts dataset and index by prompt ID."""
    with open(prompts_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    prompts_index = {}
    for prompt in data.get("prompts", []):
        prompts_index[prompt["id"]] = prompt
    
    return prompts_index

# ============================================
# 1. Expected Features Evaluation (NEW)
# ============================================

def extract_code_content(pentagon_result: Dict[str, Any], baseline_result: Dict[str, Any]) -> Dict[str, str]:
    """Extract all code content from both results."""
    
    # Pentagon code
    pentagon_code = ""
    phases = pentagon_result.get("phases", {})
    
    # User stories
    user_stories_data = phases.get("user_stories", {}).get("data", {})
    pentagon_code += f"USER STORIES:\n{json.dumps(user_stories_data, indent=2)}\n\n"
    
    # System design
    system_design_data = phases.get("system_design", {}).get("data", {})
    pentagon_code += f"SYSTEM DESIGN:\n{json.dumps(system_design_data, indent=2)}\n\n"
    
    # Backend
    backend_data = phases.get("backend_code", {}).get("data", {})
    for f in backend_data.get("files", []):
        pentagon_code += f"BACKEND FILE {f.get('filename', '')}:\n{f.get('content', '')}\n\n"
    
    # Frontend
    frontend_data = phases.get("frontend_code", {}).get("data", {})
    for f in frontend_data.get("files", []):
        pentagon_code += f"FRONTEND FILE {f.get('filename', '')}:\n{f.get('content', '')}\n\n"
    
    # Test report
    test_report_data = phases.get("test_report", {}).get("data", {})
    pentagon_code += f"TEST REPORT:\n{json.dumps(test_report_data, indent=2)}\n\n"
    
    # Baseline code
    baseline_code = ""
    output = baseline_result.get("output", {})
    
    baseline_code += f"USER STORIES:\n{json.dumps(output.get('user_stories', []), indent=2)}\n\n"
    baseline_code += f"BACKEND CODE:\n{output.get('backend_code', '')}\n\n"
    baseline_code += f"FRONTEND CODE:\n{output.get('frontend_code', '')}\n\n"
    
    return {
        "pentagon": pentagon_code,
        "baseline": baseline_code
    }

def check_feature_keyword_based(feature: str, code: str) -> Dict[str, Any]:
    """Check if a feature is implemented using keyword matching."""
    code_lower = code.lower()
    feature_lower = feature.lower()
    
    # Extract key terms from feature
    key_terms = re.findall(r'\b\w+\b', feature_lower)
    key_terms = [t for t in key_terms if len(t) > 2 and t not in ['the', 'and', 'for', 'with', 'that', 'this']]
    
    # Check for presence of key terms
    terms_found = []
    terms_missing = []
    
    for term in key_terms:
        if term in code_lower:
            terms_found.append(term)
        else:
            terms_missing.append(term)
    
    # Calculate confidence
    if len(key_terms) == 0:
        confidence = 0.5
    else:
        confidence = len(terms_found) / len(key_terms)
    
    # Determine if implemented (threshold: 60% of terms found)
    implemented = confidence >= 0.6
    
    return {
        "feature": feature,
        "implemented": implemented,
        "confidence": round(confidence, 2),
        "terms_found": terms_found,
        "terms_missing": terms_missing
    }

def check_features_llm_based(features: List[str], code: str, max_code_length: int = 12000) -> List[Dict[str, Any]]:
    """Use LLM to check if features are implemented."""
    
    # Truncate code if too long
    if len(code) > max_code_length:
        code = code[:max_code_length] + "\n... [truncated]"
    
    features_list = "\n".join([f"{i+1}. {f}" for i, f in enumerate(features)])
    
    prompt = f"""Analyze the following code and determine which features are implemented.

EXPECTED FEATURES:
{features_list}

CODE TO ANALYZE:
```
{code}
```

For each feature, determine if it is:
- "implemented": fully or partially implemented in the code
- "not_implemented": not found in the code
- "partial": some aspects present but incomplete

Respond in this exact JSON format:
{{
    "features": [
        {{"feature": "feature text", "status": "implemented/not_implemented/partial", "evidence": "brief explanation"}}
    ]
}}"""
    
    response = llm_call(prompt, max_tokens=2000)
    
    try:
        result = json.loads(response)
        return result.get("features", [])
    except json.JSONDecodeError:
        # Try to extract JSON
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
                return result.get("features", [])
            except:
                pass
        
        # Fallback to keyword-based
        return []

def evaluate_expected_features(
    prompt_id: str,
    pentagon_result: Dict[str, Any],
    baseline_result: Dict[str, Any],
    vibe_prompts: Dict[str, Dict[str, Any]],
    use_llm: bool = True
) -> Dict[str, Any]:
    """
    Evaluate expected features implementation for both Pentagon and Baseline.
    """
    
    # Get expected features from VibePrompts
    prompt_info = vibe_prompts.get(prompt_id, {})
    expected_features = prompt_info.get("expected_features", [])
    
    if not expected_features:
        return {
            "error": f"No expected features found for prompt {prompt_id}",
            "pentagon": {"implemented": 0, "total": 0, "percentage": 0},
            "baseline": {"implemented": 0, "total": 0, "percentage": 0}
        }
    
    # Extract code content
    code_content = extract_code_content(pentagon_result, baseline_result)
    
    # Evaluate Pentagon
    pentagon_features = []
    if use_llm:
        llm_results = check_features_llm_based(expected_features, code_content["pentagon"])
        if llm_results:
            for llm_result in llm_results:
                pentagon_features.append({
                    "feature": llm_result.get("feature", ""),
                    "implemented": llm_result.get("status") in ["implemented", "partial"],
                    "status": llm_result.get("status", "unknown"),
                    "evidence": llm_result.get("evidence", ""),
                    "method": "llm"
                })
    
    # Fallback or supplement with keyword-based
    if not pentagon_features:
        for feature in expected_features:
            result = check_feature_keyword_based(feature, code_content["pentagon"])
            result["method"] = "keyword"
            result["status"] = "implemented" if result["implemented"] else "not_implemented"
            pentagon_features.append(result)
    
    # Evaluate Baseline
    baseline_features = []
    if use_llm:
        llm_results = check_features_llm_based(expected_features, code_content["baseline"])
        if llm_results:
            for llm_result in llm_results:
                baseline_features.append({
                    "feature": llm_result.get("feature", ""),
                    "implemented": llm_result.get("status") in ["implemented", "partial"],
                    "status": llm_result.get("status", "unknown"),
                    "evidence": llm_result.get("evidence", ""),
                    "method": "llm"
                })
    
    # Fallback or supplement with keyword-based
    if not baseline_features:
        for feature in expected_features:
            result = check_feature_keyword_based(feature, code_content["baseline"])
            result["method"] = "keyword"
            result["status"] = "implemented" if result["implemented"] else "not_implemented"
            baseline_features.append(result)
    
    # Calculate statistics
    pentagon_implemented = sum(1 for f in pentagon_features if f.get("implemented", False))
    baseline_implemented = sum(1 for f in baseline_features if f.get("implemented", False))
    total_features = len(expected_features)
    
    return {
        "prompt_id": prompt_id,
        "prompt_description": prompt_info.get("description", ""),
        "complexity": prompt_info.get("complexity", "unknown"),
        "total_expected_features": total_features,
        "expected_features_list": expected_features,
        "pentagon": {
            "implemented_count": pentagon_implemented,
            "total": total_features,
            "percentage": round((pentagon_implemented / total_features) * 100, 1) if total_features > 0 else 0,
            "features_detail": pentagon_features
        },
        "baseline": {
            "implemented_count": baseline_implemented,
            "total": total_features,
            "percentage": round((baseline_implemented / total_features) * 100, 1) if total_features > 0 else 0,
            "features_detail": baseline_features
        },
        "comparison": {
            "pentagon_advantage": pentagon_implemented - baseline_implemented,
            "pentagon_percentage_advantage": round(
                ((pentagon_implemented / total_features) - (baseline_implemented / total_features)) * 100, 1
            ) if total_features > 0 else 0,
            "winner": "Pentagon" if pentagon_implemented > baseline_implemented else (
                "Baseline" if baseline_implemented > pentagon_implemented else "Tie"
            )
        }
    }

# ============================================
# 2. Pipeline Success Evaluation
# ============================================

def evaluate_pentagon_pipeline(pentagon_result: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Pentagon pipeline success."""
    phases = ["user_stories", "system_design", "backend_code", "frontend_code", "test_report"]
    phase_details = {}
    succeeded = 0
    
    phases_data = pentagon_result.get("phases", {})
    
    for phase in phases:
        phase_info = phases_data.get(phase, {})
        phase_success = phase_info.get("success", False)
        has_data = bool(phase_info.get("data"))
        has_error = bool(phase_info.get("error"))
        
        phase_details[phase] = {
            "success": phase_success,
            "has_data": has_data,
            "has_error": has_error
        }
        
        if phase_success and has_data:
            succeeded += 1
    
    return {
        "phases_succeeded": succeeded,
        "total_phases": len(phases),
        "success_rate": succeeded / len(phases),
        "phase_details": phase_details,
        "overall_success": pentagon_result.get("success", False)
    }

def evaluate_baseline_pipeline(baseline_result: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Baseline pipeline success."""
    output = baseline_result.get("output", {})
    
    has_user_stories = bool(output.get("user_stories"))
    has_backend = bool(output.get("backend_code"))
    has_frontend = bool(output.get("frontend_code"))
    has_test = bool(output.get("test_summary"))
    
    components = {
        "user_stories": has_user_stories,
        "backend_code": has_backend,
        "frontend_code": has_frontend,
        "test_summary": has_test
    }
    
    succeeded = sum(1 for v in components.values() if v)
    
    return {
        "components_succeeded": succeeded,
        "total_components": len(components),
        "success_rate": succeeded / len(components),
        "component_details": components,
        "overall_success": baseline_result.get("success", False)
    }

# ============================================
# 3. Code Executability Evaluation
# ============================================

def check_python_syntax(code: str) -> Dict[str, Any]:
    """Check Python code for syntax errors."""
    if not code or not code.strip():
        return {"valid": False, "error": "Empty code"}
    try:
        ast.parse(code)
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {"valid": False, "error": str(e)}

def check_html_structure(code: str) -> Dict[str, Any]:
    """Check HTML code for basic structure."""
    if not code or not code.strip():
        return {"valid": False, "issues": ["Empty code"]}
    
    issues = []
    code_lower = code.lower()
    
    if "<html" not in code_lower:
        issues.append("Missing <html> tag")
    if "<head" not in code_lower:
        issues.append("Missing <head> tag")
    if "<body" not in code_lower:
        issues.append("Missing <body> tag")
    
    script_opens = len(re.findall(r'<script[^>]*>', code, re.IGNORECASE))
    script_closes = len(re.findall(r'</script>', code, re.IGNORECASE))
    if script_opens != script_closes:
        issues.append(f"Mismatched script tags: {script_opens} opens, {script_closes} closes")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }

def evaluate_pentagon_executability(pentagon_result: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate code executability for Pentagon output."""
    phases = pentagon_result.get("phases", {})
    
    backend_data = phases.get("backend_code", {}).get("data", {})
    backend_files = backend_data.get("files", [])
    
    backend_results = []
    for f in backend_files:
        content = f.get("content", "")
        filename = f.get("filename", "unknown")
        check = check_python_syntax(content)
        backend_results.append({
            "filename": filename,
            "valid": check["valid"],
            "error": check.get("error")
        })
    
    backend_valid = all(r["valid"] for r in backend_results) if backend_results else False
    
    frontend_data = phases.get("frontend_code", {}).get("data", {})
    frontend_files = frontend_data.get("files", [])
    
    frontend_results = []
    for f in frontend_files:
        content = f.get("content", "")
        filename = f.get("filename", "unknown")
        check = check_html_structure(content)
        frontend_results.append({
            "filename": filename,
            "valid": check["valid"],
            "issues": check.get("issues", [])
        })
    
    frontend_valid = all(r["valid"] for r in frontend_results) if frontend_results else False
    
    return {
        "backend": {
            "files_checked": len(backend_results),
            "all_valid": backend_valid,
            "details": backend_results
        },
        "frontend": {
            "files_checked": len(frontend_results),
            "all_valid": frontend_valid,
            "details": frontend_results
        },
        "overall_score": (1.0 if backend_valid else 0.0) * 0.5 + (1.0 if frontend_valid else 0.0) * 0.5
    }

def evaluate_baseline_executability(baseline_result: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate code executability for Baseline output."""
    output = baseline_result.get("output", {})
    
    backend_code = output.get("backend_code", "")
    backend_check = check_python_syntax(backend_code)
    
    frontend_code = output.get("frontend_code", "")
    frontend_check = check_html_structure(frontend_code)
    
    return {
        "backend": {
            "valid": backend_check["valid"],
            "error": backend_check.get("error")
        },
        "frontend": {
            "valid": frontend_check["valid"],
            "issues": frontend_check.get("issues", [])
        },
        "overall_score": (1.0 if backend_check["valid"] else 0.0) * 0.5 + (1.0 if frontend_check["valid"] else 0.0) * 0.5
    }

# ============================================
# 4. QA Test Results Evaluation
# ============================================

def evaluate_qa_results(pentagon_result: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate QA test results from Pentagon."""
    phases = pentagon_result.get("phases", {})
    test_report = phases.get("test_report", {}).get("data", {})
    
    if not test_report:
        return {
            "has_qa": False,
            "overall_status": "missing",
            "test_cases": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "pass_rate": 0.0
        }
    
    overall_status = test_report.get("overall_status", "unknown")
    test_cases = test_report.get("test_cases", [])
    
    passed = sum(1 for tc in test_cases if tc.get("status") == "pass")
    failed = sum(1 for tc in test_cases if tc.get("status") == "fail")
    skipped = sum(1 for tc in test_cases if tc.get("status") == "skip")
    total = len(test_cases)
    
    return {
        "has_qa": True,
        "overall_status": overall_status,
        "test_cases": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": passed / total if total > 0 else 0.0,
        "recommendations_count": len(test_report.get("recommendations", []))
    }

# ============================================
# 5. User Stories Quality Evaluation
# ============================================

def evaluate_user_stories(pentagon_result: Dict[str, Any], baseline_result: Dict[str, Any]) -> Dict[str, Any]:
    """Compare user stories between Pentagon and Baseline."""
    
    pentagon_phases = pentagon_result.get("phases", {})
    pentagon_stories_data = pentagon_phases.get("user_stories", {}).get("data", {})
    pentagon_stories = pentagon_stories_data.get("stories", [])
    
    baseline_output = baseline_result.get("output", {})
    baseline_stories = baseline_output.get("user_stories", [])
    
    def analyze_stories(stories: List[Dict]) -> Dict[str, Any]:
        if not stories:
            return {"count": 0, "has_priorities": False, "has_descriptions": False}
        
        has_priorities = all("priority" in s for s in stories)
        has_descriptions = all("description" in s and len(s.get("description", "")) > 10 for s in stories)
        has_ids = all("id" in s for s in stories)
        
        priority_counts = defaultdict(int)
        for s in stories:
            priority_counts[s.get("priority", "unknown")] += 1
        
        return {
            "count": len(stories),
            "has_priorities": has_priorities,
            "has_descriptions": has_descriptions,
            "has_ids": has_ids,
            "priority_distribution": dict(priority_counts)
        }
    
    return {
        "pentagon": analyze_stories(pentagon_stories),
        "baseline": analyze_stories(baseline_stories)
    }

# ============================================
# 6. System Design Evaluation (Pentagon Only)
# ============================================

def evaluate_system_design(pentagon_result: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate system design quality (Pentagon only)."""
    phases = pentagon_result.get("phases", {})
    design_data = phases.get("system_design", {}).get("data", {})
    
    if not design_data:
        return {
            "has_design": False,
            "models_count": 0,
            "endpoints_count": 0,
            "has_architecture_notes": False
        }
    
    models = design_data.get("models", [])
    endpoints = design_data.get("endpoints", [])
    architecture_notes = design_data.get("architecture_notes", "")
    
    model_details = []
    for model in models:
        model_details.append({
            "name": model.get("name", "unknown"),
            "fields_count": len(model.get("fields", []))
        })
    
    endpoint_methods = defaultdict(int)
    for ep in endpoints:
        endpoint_methods[ep.get("method", "UNKNOWN")] += 1
    
    return {
        "has_design": True,
        "models_count": len(models),
        "models": model_details,
        "endpoints_count": len(endpoints),
        "endpoint_methods": dict(endpoint_methods),
        "has_architecture_notes": bool(architecture_notes),
        "architecture_notes_length": len(architecture_notes)
    }

# ============================================
# 7. Execution Efficiency Evaluation
# ============================================

def evaluate_efficiency(pentagon_result: Dict[str, Any], baseline_result: Dict[str, Any]) -> Dict[str, Any]:
    """Compare execution efficiency between Pentagon and Baseline."""
    
    pentagon_time = pentagon_result.get("execution_time_seconds", 0)
    baseline_time = baseline_result.get("execution_time_seconds", 0)
    
    pentagon_phases = pentagon_result.get("phases_succeeded", 0)
    
    return {
        "pentagon": {
            "execution_time_seconds": round(pentagon_time, 2),
            "phases_succeeded": pentagon_phases,
            "time_per_phase": round(pentagon_time / pentagon_phases, 2) if pentagon_phases > 0 else 0
        },
        "baseline": {
            "execution_time_seconds": round(baseline_time, 2)
        },
        "comparison": {
            "pentagon_slower_by_seconds": round(pentagon_time - baseline_time, 2),
            "pentagon_slower_by_factor": round(pentagon_time / baseline_time, 2) if baseline_time > 0 else 0
        }
    }

# ============================================
# 8. Code Quality Evaluation (LLM-based)
# ============================================

def evaluate_code_quality_llm(prompt: str, pentagon_result: Dict[str, Any], baseline_result: Dict[str, Any]) -> Dict[str, Any]:
    """Use LLM to evaluate code quality."""
    
    pentagon_phases = pentagon_result.get("phases", {})
    pentagon_backend = ""
    pentagon_frontend = ""
    
    backend_data = pentagon_phases.get("backend_code", {}).get("data", {})
    for f in backend_data.get("files", []):
        pentagon_backend += f.get("content", "") + "\n"
    
    frontend_data = pentagon_phases.get("frontend_code", {}).get("data", {})
    for f in frontend_data.get("files", []):
        pentagon_frontend += f.get("content", "") + "\n"
    
    baseline_output = baseline_result.get("output", {})
    baseline_backend = baseline_output.get("backend_code", "")
    baseline_frontend = baseline_output.get("frontend_code", "")
    
    evaluation_prompt = f"""Evaluate code quality for both implementations.

REQUIREMENT: {prompt}

PENTAGON BACKEND (first 3000 chars):
{pentagon_backend[:3000]}

PENTAGON FRONTEND (first 3000 chars):
{pentagon_frontend[:3000]}

BASELINE BACKEND (first 3000 chars):
{baseline_backend[:3000]}

BASELINE FRONTEND (first 3000 chars):
{baseline_frontend[:3000]}

Rate each on a scale of 1-10:
1. Code structure (organization, modularity)
2. Readability (naming, comments)
3. API design (RESTful, clear endpoints)
4. Error handling (validation, edge cases)

Respond in this exact JSON format:
{{
    "pentagon": {{
        "code_structure": <score>,
        "readability": <score>,
        "api_design": <score>,
        "error_handling": <score>,
        "notes": "<brief notes>"
    }},
    "baseline": {{
        "code_structure": <score>,
        "readability": <score>,
        "api_design": <score>,
        "error_handling": <score>,
        "notes": "<brief notes>"
    }}
}}"""
    
    response = llm_call(evaluation_prompt, max_tokens=800)
    
    try:
        result = json.loads(response)
        for key in ["pentagon", "baseline"]:
            if key in result:
                scores = [result[key].get(m, 5) for m in ["code_structure", "readability", "api_design", "error_handling"]]
                result[key]["average"] = round(sum(scores) / len(scores), 2)
        return result
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
                for key in ["pentagon", "baseline"]:
                    if key in result:
                        scores = [result[key].get(m, 5) for m in ["code_structure", "readability", "api_design", "error_handling"]]
                        result[key]["average"] = round(sum(scores) / len(scores), 2)
                return result
            except:
                pass
        return {
            "pentagon": {"average": 5, "notes": "Could not parse evaluation"},
            "baseline": {"average": 5, "notes": "Could not parse evaluation"}
        }

# ============================================
# 9. Single Prompt Comprehensive Evaluation
# ============================================

def evaluate_single_prompt(
    prompt_result: Dict[str, Any],
    vibe_prompts: Dict[str, Dict[str, Any]],
    use_llm: bool = True
) -> Dict[str, Any]:
    """Comprehensive evaluation for a single prompt result."""
    
    prompt = prompt_result.get("prompt", "")
    prompt_id = prompt_result.get("prompt_id", "unknown")
    complexity = prompt_result.get("complexity", "unknown")
    
    pentagon = prompt_result.get("pentagon", {})
    baseline = prompt_result.get("baseline", {})
    
    evaluation = {
        "prompt_id": prompt_id,
        "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
        "complexity": complexity,
        "timestamp": datetime.now().isoformat(),
        
        # 1. Expected Features (NEW - Primary metric)
        "expected_features": evaluate_expected_features(
            prompt_id, pentagon, baseline, vibe_prompts, use_llm
        ),
        
        # 2. Pipeline Success
        "pipeline": {
            "pentagon": evaluate_pentagon_pipeline(pentagon),
            "baseline": evaluate_baseline_pipeline(baseline)
        },
        
        # 3. Code Executability
        "executability": {
            "pentagon": evaluate_pentagon_executability(pentagon),
            "baseline": evaluate_baseline_executability(baseline)
        },
        
        # 4. QA Results (Pentagon only)
        "qa_results": evaluate_qa_results(pentagon),
        
        # 5. User Stories
        "user_stories": evaluate_user_stories(pentagon, baseline),
        
        # 6. System Design (Pentagon only)
        "system_design": evaluate_system_design(pentagon),
        
        # 7. Efficiency
        "efficiency": evaluate_efficiency(pentagon, baseline)
    }
    
    # 8. LLM-based code quality (optional)
    if use_llm:
        try:
            evaluation["code_quality_llm"] = evaluate_code_quality_llm(prompt, pentagon, baseline)
        except Exception as e:
            evaluation["code_quality_llm"] = {"error": str(e)}
    
    # Calculate summary scores
    evaluation["summary"] = calculate_summary_scores(evaluation)
    
    return evaluation

# ============================================
# 10. Summary Score Calculation
# ============================================

def calculate_summary_scores(evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate summary scores from evaluation results."""
    
    # Expected Features scores (NEW - weighted heavily)
    expected_features = evaluation.get("expected_features", {})
    pentagon_features_pct = expected_features.get("pentagon", {}).get("percentage", 0) / 100
    baseline_features_pct = expected_features.get("baseline", {}).get("percentage", 0) / 100
    
    # Pipeline scores
    pentagon_pipeline = evaluation["pipeline"]["pentagon"]["success_rate"]
    baseline_pipeline = evaluation["pipeline"]["baseline"]["success_rate"]
    
    # Executability scores
    pentagon_exec = evaluation["executability"]["pentagon"]["overall_score"]
    baseline_exec = evaluation["executability"]["baseline"]["overall_score"]
    
    # QA score (Pentagon only)
    pentagon_qa = evaluation["qa_results"]["pass_rate"]
    
    # LLM quality scores if available
    quality_eval = evaluation.get("code_quality_llm", {})
    pentagon_quality = quality_eval.get("pentagon", {}).get("average", 5) / 10
    baseline_quality = quality_eval.get("baseline", {}).get("average", 5) / 10
    
    # Weighted composite scores
    # Pentagon: Features (30%) + Pipeline (15%) + Exec (15%) + QA (20%) + Quality (20%)
    pentagon_composite = (
        pentagon_features_pct * 0.30 +
        pentagon_pipeline * 0.15 +
        pentagon_exec * 0.15 +
        pentagon_qa * 0.20 +
        pentagon_quality * 0.20
    )
    
    # Baseline: Features (40%) + Pipeline (20%) + Exec (20%) + Quality (20%)
    baseline_composite = (
        baseline_features_pct * 0.40 +
        baseline_pipeline * 0.20 +
        baseline_exec * 0.20 +
        baseline_quality * 0.20
    )
    
    return {
        "pentagon": {
            "features_score": round(pentagon_features_pct, 3),
            "pipeline_score": round(pentagon_pipeline, 3),
            "executability_score": round(pentagon_exec, 3),
            "qa_score": round(pentagon_qa, 3),
            "quality_score": round(pentagon_quality, 3),
            "composite_score": round(pentagon_composite, 3)
        },
        "baseline": {
            "features_score": round(baseline_features_pct, 3),
            "pipeline_score": round(baseline_pipeline, 3),
            "executability_score": round(baseline_exec, 3),
            "quality_score": round(baseline_quality, 3),
            "composite_score": round(baseline_composite, 3)
        },
        "comparison": {
            "features_advantage": round(pentagon_features_pct - baseline_features_pct, 3),
            "composite_advantage": round(pentagon_composite - baseline_composite, 3),
            "pentagon_wins": pentagon_composite > baseline_composite
        }
    }

# ============================================
# 11. Full Experiment Evaluation
# ============================================

def evaluate_full_experiment(
    experiment_data: Dict[str, Any],
    vibe_prompts: Dict[str, Dict[str, Any]],
    use_llm: bool = True
) -> Dict[str, Any]:
    """Evaluate complete experiment results."""
    
    print("=" * 60)
    print("PENTAGON PROTOCOL - COMPREHENSIVE EVALUATION")
    print("=" * 60)
    
    results = experiment_data.get("results", [])
    total_prompts = len(results)
    
    print(f"\nEvaluating {total_prompts} prompts...")
    print(f"Expected features loaded: {len(vibe_prompts)} prompts")
    
    prompt_evaluations = []
    
    for i, prompt_result in enumerate(results):
        prompt_id = prompt_result.get("prompt_id", f"P{i+1}")
        print(f"\n[{i+1}/{total_prompts}] Evaluating {prompt_id}...")
        
        evaluation = evaluate_single_prompt(prompt_result, vibe_prompts, use_llm=use_llm)
        prompt_evaluations.append(evaluation)
        
        # Print quick summary
        summary = evaluation["summary"]
        features = evaluation["expected_features"]
        
        print(f"  Expected Features: Pentagon {features['pentagon']['percentage']:.1f}% vs Baseline {features['baseline']['percentage']:.1f}%")
        print(f"  Composite Score:   Pentagon {summary['pentagon']['composite_score']:.3f} vs Baseline {summary['baseline']['composite_score']:.3f}")
        print(f"  Winner: {'Pentagon' if summary['comparison']['pentagon_wins'] else 'Baseline'}")
    
    # Aggregate results
    aggregate = calculate_aggregate_results(prompt_evaluations)
    
    # Generate final report
    final_report = {
        "experiment_date": experiment_data.get("experiment_date"),
        "evaluation_date": datetime.now().isoformat(),
        "total_prompts": total_prompts,
        "vibe_prompts_version": "2.0",
        "prompt_evaluations": prompt_evaluations,
        "aggregate": aggregate,
        "conclusions": generate_conclusions(aggregate)
    }
    
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    
    return final_report

# ============================================
# 12. Aggregate Results Calculation
# ============================================

def calculate_aggregate_results(evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregate statistics across all prompts."""
    
    if not evaluations:
        return {}
    
    # Collect scores
    pentagon_scores = {
        "features": [],
        "pipeline": [],
        "executability": [],
        "qa": [],
        "quality": [],
        "composite": []
    }
    
    baseline_scores = {
        "features": [],
        "pipeline": [],
        "executability": [],
        "quality": [],
        "composite": []
    }
    
    pentagon_wins = 0
    features_wins = 0
    
    # By complexity
    by_complexity = defaultdict(lambda: {
        "pentagon_features": [],
        "baseline_features": [],
        "pentagon_composite": [],
        "baseline_composite": []
    })
    
    for eval_result in evaluations:
        summary = eval_result["summary"]
        complexity = eval_result.get("complexity", "unknown")
        
        # Pentagon scores
        pentagon_scores["features"].append(summary["pentagon"]["features_score"])
        pentagon_scores["pipeline"].append(summary["pentagon"]["pipeline_score"])
        pentagon_scores["executability"].append(summary["pentagon"]["executability_score"])
        pentagon_scores["qa"].append(summary["pentagon"]["qa_score"])
        pentagon_scores["quality"].append(summary["pentagon"]["quality_score"])
        pentagon_scores["composite"].append(summary["pentagon"]["composite_score"])
        
        # Baseline scores
        baseline_scores["features"].append(summary["baseline"]["features_score"])
        baseline_scores["pipeline"].append(summary["baseline"]["pipeline_score"])
        baseline_scores["executability"].append(summary["baseline"]["executability_score"])
        baseline_scores["quality"].append(summary["baseline"]["quality_score"])
        baseline_scores["composite"].append(summary["baseline"]["composite_score"])
        
        # Wins
        if summary["comparison"]["pentagon_wins"]:
            pentagon_wins += 1
        
        if summary["comparison"]["features_advantage"] > 0:
            features_wins += 1
        
        # By complexity
        by_complexity[complexity]["pentagon_features"].append(summary["pentagon"]["features_score"])
        by_complexity[complexity]["baseline_features"].append(summary["baseline"]["features_score"])
        by_complexity[complexity]["pentagon_composite"].append(summary["pentagon"]["composite_score"])
        by_complexity[complexity]["baseline_composite"].append(summary["baseline"]["composite_score"])
    
    def calc_stats(scores: List[float]) -> Dict[str, float]:
        if not scores:
            return {"mean": 0, "min": 0, "max": 0, "std": 0}
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return {
            "mean": round(mean, 3),
            "min": round(min(scores), 3),
            "max": round(max(scores), 3),
            "std": round(variance ** 0.5, 3)
        }
    
    pentagon_stats = {k: calc_stats(v) for k, v in pentagon_scores.items()}
    baseline_stats = {k: calc_stats(v) for k, v in baseline_scores.items()}
    
    # Complexity breakdown
    complexity_stats = {}
    for complexity, scores in by_complexity.items():
        complexity_stats[complexity] = {
            "count": len(scores["pentagon_composite"]),
            "pentagon_features_mean": round(sum(scores["pentagon_features"]) / len(scores["pentagon_features"]), 3) if scores["pentagon_features"] else 0,
            "baseline_features_mean": round(sum(scores["baseline_features"]) / len(scores["baseline_features"]), 3) if scores["baseline_features"] else 0,
            "pentagon_composite_mean": round(sum(scores["pentagon_composite"]) / len(scores["pentagon_composite"]), 3) if scores["pentagon_composite"] else 0,
            "baseline_composite_mean": round(sum(scores["baseline_composite"]) / len(scores["baseline_composite"]), 3) if scores["baseline_composite"] else 0
        }
    
    return {
        "pentagon": pentagon_stats,
        "baseline": baseline_stats,
        "comparison": {
            "pentagon_wins": pentagon_wins,
            "baseline_wins": len(evaluations) - pentagon_wins,
            "pentagon_win_rate": round(pentagon_wins / len(evaluations), 3),
            "features_win_rate": round(features_wins / len(evaluations), 3),
            "average_features_advantage": round(
                pentagon_stats["features"]["mean"] - baseline_stats["features"]["mean"], 3
            ),
            "average_composite_advantage": round(
                pentagon_stats["composite"]["mean"] - baseline_stats["composite"]["mean"], 3
            )
        },
        "by_complexity": complexity_stats
    }

# ============================================
# 13. Conclusions Generation
# ============================================

def generate_conclusions(aggregate: Dict[str, Any]) -> Dict[str, Any]:
    """Generate conclusions from aggregate results."""
    
    pentagon = aggregate.get("pentagon", {})
    baseline = aggregate.get("baseline", {})
    comparison = aggregate.get("comparison", {})
    by_complexity = aggregate.get("by_complexity", {})
    
    conclusions = {
        "overall_winner": "Pentagon" if comparison.get("pentagon_win_rate", 0) > 0.5 else "Baseline",
        "composite_win_rate": comparison.get("pentagon_win_rate", 0),
        "features_win_rate": comparison.get("features_win_rate", 0),
        "key_findings": []
    }
    
    # Key findings
    features_adv = comparison.get("average_features_advantage", 0)
    if features_adv > 0.1:
        conclusions["key_findings"].append(
            f"Pentagon implements {features_adv*100:.1f}% more expected features on average"
        )
    elif features_adv < -0.1:
        conclusions["key_findings"].append(
            f"Baseline implements {abs(features_adv)*100:.1f}% more expected features on average"
        )
    
    if comparison.get("pentagon_win_rate", 0) >= 0.8:
        conclusions["key_findings"].append(
            "Pentagon Protocol significantly outperforms Baseline across most prompts"
        )
    elif comparison.get("pentagon_win_rate", 0) >= 0.6:
        conclusions["key_findings"].append(
            "Pentagon Protocol shows consistent improvement over Baseline"
        )
    
    # QA advantage
    if pentagon.get("qa", {}).get("mean", 0) > 0.7:
        conclusions["key_findings"].append(
            f"Pentagon's built-in QA achieves {pentagon['qa']['mean']*100:.1f}% test pass rate"
        )
    
    # Composite scores
    conclusions["key_findings"].append(
        f"Average composite: Pentagon {pentagon.get('composite', {}).get('mean', 0):.3f} vs Baseline {baseline.get('composite', {}).get('mean', 0):.3f}"
    )
    
    # Complexity analysis
    for complexity, stats in by_complexity.items():
        features_diff = stats["pentagon_features_mean"] - stats["baseline_features_mean"]
        if features_diff > 0.05:
            conclusions["key_findings"].append(
                f"Pentagon excels in {complexity} prompts: {stats['pentagon_features_mean']*100:.1f}% vs {stats['baseline_features_mean']*100:.1f}% features"
            )
    
    return conclusions

# ============================================
# 14. Report Generation for Thesis
# ============================================

def generate_thesis_tables(evaluation_report: Dict[str, Any]) -> str:
    """Generate markdown tables for thesis Chapter 5."""
    
    md = "# Chapter 5: Results and Analysis\n\n"
    
    # Table 1: Expected Features Results (NEW - Primary table)
    md += "## Table 5.1: Expected Features Implementation Rate\n\n"
    md += "| Prompt ID | Complexity | Expected Features | Pentagon | Baseline | Advantage |\n"
    md += "|-----------|------------|-------------------|----------|----------|----------|\n"
    
    for eval_result in evaluation_report.get("prompt_evaluations", []):
        prompt_id = eval_result.get("prompt_id", "")
        complexity = eval_result.get("complexity", "")
        features = eval_result.get("expected_features", {})
        
        total = features.get("total_expected_features", 0)
        p_pct = features.get("pentagon", {}).get("percentage", 0)
        b_pct = features.get("baseline", {}).get("percentage", 0)
        adv = p_pct - b_pct
        
        md += f"| {prompt_id} | {complexity} | {total} | {p_pct:.1f}% | {b_pct:.1f}% | {adv:+.1f}% |\n"
    
    # Add averages row
    aggregate = evaluation_report.get("aggregate", {})
    p_avg = aggregate.get("pentagon", {}).get("features", {}).get("mean", 0) * 100
    b_avg = aggregate.get("baseline", {}).get("features", {}).get("mean", 0) * 100
    md += f"| **Average** | - | - | **{p_avg:.1f}%** | **{b_avg:.1f}%** | **{p_avg-b_avg:+.1f}%** |\n"
    
    # Table 2: Overall Metric Comparison
    md += "\n## Table 5.2: Overall Experimental Results\n\n"
    md += "| Metric | Pentagon | Baseline | Advantage |\n"
    md += "|--------|----------|----------|----------|\n"
    
    pentagon = aggregate.get("pentagon", {})
    baseline = aggregate.get("baseline", {})
    
    metrics = [
        ("Expected Features (%)", "features", 100),
        ("Pipeline Success Rate", "pipeline", 1),
        ("Code Executability", "executability", 1),
        ("QA Pass Rate", "qa", 1),
        ("Code Quality (LLM)", "quality", 1),
        ("Composite Score", "composite", 1)
    ]
    
    for label, key, multiplier in metrics:
        p_val = pentagon.get(key, {}).get("mean", 0) * multiplier
        b_val = baseline.get(key, {}).get("mean", 0) * multiplier if key != "qa" else "N/A"
        
        if b_val != "N/A":
            adv = p_val - b_val
            adv_str = f"+{adv:.1f}" if adv > 0 else f"{adv:.1f}"
            if multiplier == 100:
                md += f"| {label} | {p_val:.1f}% | {b_val:.1f}% | {adv_str}% |\n"
            else:
                md += f"| {label} | {p_val:.3f} | {b_val:.3f} | {adv_str} |\n"
        else:
            md += f"| {label} | {p_val:.3f} | N/A | N/A |\n"
    
    # Table 3: Results by Complexity
    md += "\n## Table 5.3: Results by Complexity Level\n\n"
    md += "| Complexity | Count | Pentagon Features | Baseline Features | Pentagon Composite | Baseline Composite |\n"
    md += "|------------|-------|-------------------|-------------------|--------------------|--------------------|n"
    
    for complexity, stats in aggregate.get("by_complexity", {}).items():
        md += f"| {complexity} | {stats['count']} | {stats['pentagon_features_mean']*100:.1f}% | {stats['baseline_features_mean']*100:.1f}% | {stats['pentagon_composite_mean']:.3f} | {stats['baseline_composite_mean']:.3f} |\n"
    
    # Table 4: Detailed Feature Analysis (sample)
    md += "\n## Table 5.4: Feature Implementation Details (Sample - VP01)\n\n"
    
    # Find VP01
    for eval_result in evaluation_report.get("prompt_evaluations", []):
        if eval_result.get("prompt_id") == "VP01":
            features = eval_result.get("expected_features", {})
            md += "| Feature | Pentagon | Baseline |\n"
            md += "|---------|----------|----------|\n"
            
            p_details = features.get("pentagon", {}).get("features_detail", [])
            b_details = features.get("baseline", {}).get("features_detail", [])
            
            expected = features.get("expected_features_list", [])
            for i, feat in enumerate(expected):
                p_status = "✓" if i < len(p_details) and p_details[i].get("implemented") else "✗"
                b_status = "✓" if i < len(b_details) and b_details[i].get("implemented") else "✗"
                md += f"| {feat} | {p_status} | {b_status} |\n"
            break
    
    # Conclusions
    md += "\n## Key Findings\n\n"
    conclusions = evaluation_report.get("conclusions", {})
    for finding in conclusions.get("key_findings", []):
        md += f"- {finding}\n"
    
    md += f"\n**Overall Winner: {conclusions.get('overall_winner', 'Unknown')}**\n"
    md += f"- Composite Win Rate: {conclusions.get('composite_win_rate', 0)*100:.1f}%\n"
    md += f"- Features Win Rate: {conclusions.get('features_win_rate', 0)*100:.1f}%\n"
    
    return md

# ============================================
# Main Entry Point
# ============================================

def run_evaluation(
    experiment_json_path: str,
    prompts_json_path: str,
    output_dir: str = "evaluation_output",
    use_llm: bool = True
) -> Dict[str, Any]:
    """
    Main function to run evaluation on experiment results.
    
    Args:
        experiment_json_path: Path to experiment_results.json
        prompts_json_path: Path to vibe_prompts.json (with expected features)
        output_dir: Directory to save evaluation outputs
        use_llm: Whether to use LLM for quality evaluation
    
    Returns:
        Complete evaluation report
    """
    
    # Load experiment data
    print(f"Loading experiment data from: {experiment_json_path}")
    with open(experiment_json_path, 'r', encoding='utf-8') as f:
        experiment_data = json.load(f)
    
    # Load VibePrompts
    print(f"Loading VibePrompts from: {prompts_json_path}")
    vibe_prompts = load_vibe_prompts(prompts_json_path)
    print(f"Loaded {len(vibe_prompts)} prompts with expected features")
    
    # Run evaluation
    evaluation_report = evaluate_full_experiment(experiment_data, vibe_prompts, use_llm=use_llm)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save evaluation report
    report_path = os.path.join(output_dir, "evaluation_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation_report, f, indent=2, default=str)
    print(f"\nEvaluation report saved to: {report_path}")
    
    # Generate thesis tables
    thesis_md = generate_thesis_tables(evaluation_report)
    tables_path = os.path.join(output_dir, "thesis_tables.md")
    with open(tables_path, 'w', encoding='utf-8') as f:
        f.write(thesis_md)
    print(f"Thesis tables saved to: {tables_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    
    aggregate = evaluation_report.get("aggregate", {})
    comparison = aggregate.get("comparison", {})
    conclusions = evaluation_report.get("conclusions", {})
    
    print(f"\n📊 Expected Features Implementation:")
    print(f"   Pentagon: {aggregate.get('pentagon', {}).get('features', {}).get('mean', 0)*100:.1f}%")
    print(f"   Baseline: {aggregate.get('baseline', {}).get('features', {}).get('mean', 0)*100:.1f}%")
    print(f"   Advantage: {comparison.get('average_features_advantage', 0)*100:+.1f}%")
    
    print(f"\n🏆 Overall Results:")
    print(f"   Winner: {conclusions.get('overall_winner', 'Unknown')}")
    print(f"   Pentagon Win Rate: {comparison.get('pentagon_win_rate', 0)*100:.1f}%")
    
    print("\n📝 Key Findings:")
    for finding in conclusions.get("key_findings", []):
        print(f"   • {finding}")
    
    return evaluation_report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) >= 3:
        experiment_path = sys.argv[1]
        prompts_path = sys.argv[2]
    else:
        experiment_path = r"output\full_experiment_20260119_004837.json"
        prompts_path = "data/prompts/vibe_prompts.json"
    
    # use_llm = "--no-llm" not in sys.argv
    
    run_evaluation(experiment_path, prompts_path, use_llm=True)
