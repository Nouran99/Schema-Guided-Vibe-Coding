"""
Pentagon Protocol - Enhanced Crew Orchestration
With robust error handling, output saving, iterative QA feedback loop,
memory-efficient context management, manager coordination, and truncation recovery
"""

import gc
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional, List, Set
from pathlib import Path

from crewai import Crew, Process, Agent, Task

from .agents import (
    create_product_owner, create_architect, create_backend_engineer,
    create_frontend_engineer, create_qa_engineer, create_manager_agent,
    create_baseline_agent
)
from .tasks import (
    create_user_stories_task, create_system_design_task, create_backend_task,
    create_frontend_task, create_qa_task, create_baseline_task
)
from .schemas import (
    UserStoriesOutput, SystemDesign, BackendCode, FrontendCode, TestReport,
    safe_parse_json
)


# Agent identifiers for issue mapping
AGENT_PRODUCT_OWNER = "product_owner"
AGENT_ARCHITECT = "architect"
AGENT_BACKEND_ENGINEER = "backend_engineer"
AGENT_FRONTEND_ENGINEER = "frontend_engineer"
AGENT_QA_ENGINEER = "qa_engineer"
AGENT_MANAGER = "manager"

# Agent dependency chain (if an agent re-runs, downstream agents must also re-run)
AGENT_DEPENDENCIES = {
    AGENT_PRODUCT_OWNER: [AGENT_ARCHITECT, AGENT_BACKEND_ENGINEER, AGENT_FRONTEND_ENGINEER],
    AGENT_ARCHITECT: [AGENT_BACKEND_ENGINEER, AGENT_FRONTEND_ENGINEER],
    AGENT_BACKEND_ENGINEER: [AGENT_FRONTEND_ENGINEER],
    AGENT_FRONTEND_ENGINEER: [],
}


class ManagerDecision:
    """Represents the manager's decision about which agents need to re-run."""
    
    def __init__(self):
        self.should_continue: bool = False
        self.agents_to_rerun: List[str] = []
        self.reasoning: str = ""
        self.iteration_goal: str = ""


class ContextManager:
    """
    Manages context data for agents with memory-efficient subset extraction.
    Only stores and passes the minimum required data for each agent.
    """
    
    def __init__(self):
        self.vibe_prompt: str = ""
        self.user_stories: Optional[Dict] = None
        self.system_design: Optional[Dict] = None
        self.backend_code: Optional[Dict] = None
        self.frontend_code: Optional[Dict] = None
        self.test_report: Optional[Dict] = None
    
    def update_user_stories(self, data: Dict):
        """Store user stories data."""
        if data and data.get("success"):
            self.user_stories = data.get("data")
    
    def update_system_design(self, data: Dict):
        """Store system design data."""
        if data and data.get("success"):
            self.system_design = data.get("data")
    
    def update_backend_code(self, data: Dict):
        """Store backend code data."""
        if data and data.get("success"):
            self.backend_code = data.get("data")
    
    def update_frontend_code(self, data: Dict):
        """Store frontend code data."""
        if data and data.get("success"):
            self.frontend_code = data.get("data")
    
    def update_test_report(self, data: Dict):
        """Store test report data."""
        if data and data.get("success"):
            self.test_report = data.get("data")
    
    def _format_user_stories_summary(self) -> str:
        """Format user stories as a concise summary."""
        if not self.user_stories:
            return "No user stories available."
        
        stories = self.user_stories.get("stories", [])
        summary_parts = ["## User Stories:"]
        
        for story in stories:
            story_id = story.get("id", "N/A")
            title = story.get("title", "N/A")
            description = story.get("description", "N/A")
            priority = story.get("priority", "medium")
            summary_parts.append(f"- [{story_id}] ({priority}) {title}: {description}")
        
        if self.user_stories.get("summary"):
            summary_parts.append(f"\nSummary: {self.user_stories.get('summary')}")
        
        return "\n".join(summary_parts)
    
    def _format_system_design_summary(self) -> str:
        """Format system design as a concise summary."""
        if not self.system_design:
            return "No system design available."
        
        summary_parts = ["## System Design:"]
        
        # Models
        models = self.system_design.get("models", [])
        if models:
            summary_parts.append("\n### Data Models:")
            for model in models:
                name = model.get("name", "N/A")
                fields = model.get("fields", [])
                fields_str = ", ".join(fields) if fields else "no fields"
                summary_parts.append(f"- {name}: {fields_str}")
        
        # Endpoints
        endpoints = self.system_design.get("endpoints", [])
        if endpoints:
            summary_parts.append("\n### API Endpoints:")
            for endpoint in endpoints:
                method = endpoint.get("method", "GET")
                path = endpoint.get("path", "/")
                description = endpoint.get("description", "")
                summary_parts.append(f"- {method} {path}: {description}")
        
        if self.system_design.get("architecture_notes"):
            summary_parts.append(f"\nNotes: {self.system_design.get('architecture_notes')}")
        
        return "\n".join(summary_parts)
    
    def _format_backend_endpoints_summary(self) -> str:
        """Format only backend endpoints (not full code) for frontend context."""
        if not self.backend_code:
            return "No backend endpoints available."
        
        summary_parts = ["## Backend API Endpoints:"]
        
        files = self.backend_code.get("files", [])
        
        for file_info in files:
            filename = file_info.get("filename", "")
            if "main" in filename.lower() or "route" in filename.lower():
                content = file_info.get("content", "")
                lines = content.split("\n") if isinstance(content, str) else []
                for line in lines:
                    line = line.strip()
                    if line.startswith("@app.") or line.startswith("@router."):
                        summary_parts.append(f"- {line}")
        
        setup = self.backend_code.get("setup_instructions", "")
        if setup:
            summary_parts.append(f"\nSetup: {setup}")
        
        if len(summary_parts) == 1:
            summary_parts.append("\nBackend files:")
            for file_info in files:
                filename = file_info.get("filename", "")
                description = file_info.get("description", "")
                summary_parts.append(f"- {filename}: {description}")
        
        return "\n".join(summary_parts)
    
    def _format_backend_code_full(self) -> str:
        """Format full backend code for QA context."""
        if not self.backend_code:
            return "No backend code available."
        
        summary_parts = ["## Backend Code:"]
        
        files = self.backend_code.get("files", [])
        for file_info in files:
            filename = file_info.get("filename", "")
            content = file_info.get("content", "")
            description = file_info.get("description", "")
            
            summary_parts.append(f"\n### {filename}")
            if description:
                summary_parts.append(f"Description: {description}")
            summary_parts.append(f"```\n{content}\n```")
        
        setup = self.backend_code.get("setup_instructions", "")
        if setup:
            summary_parts.append(f"\nSetup: {setup}")
        
        return "\n".join(summary_parts)
    
    def _format_frontend_code_full(self) -> str:
        """Format full frontend code for QA context."""
        if not self.frontend_code:
            return "No frontend code available."
        
        summary_parts = ["## Frontend Code:"]
        
        files = self.frontend_code.get("files", [])
        for file_info in files:
            filename = file_info.get("filename", "")
            content = file_info.get("content", "")
            description = file_info.get("description", "")
            
            summary_parts.append(f"\n### {filename}")
            if description:
                summary_parts.append(f"Description: {description}")
            summary_parts.append(f"```\n{content}\n```")
        
        setup = self.frontend_code.get("setup_instructions", "")
        if setup:
            summary_parts.append(f"\nSetup: {setup}")
        
        return "\n".join(summary_parts)
    
    def _format_qa_feedback(self, agent_name: str) -> str:
        """Format QA feedback specific to an agent."""
        if not self.test_report:
            return ""
        
        feedback_parts = []
        
        issues_by_agent = self.test_report.get("issues_by_agent", {})
        agent_issues = issues_by_agent.get(agent_name, [])
        
        if agent_issues:
            feedback_parts.append("Issues found for your component:")
            for issue in agent_issues:
                feedback_parts.append(f"  - {issue}")
        
        test_cases = self.test_report.get("test_cases", [])
        failed_tests = [
            tc for tc in test_cases
            if isinstance(tc, dict) 
            and tc.get("status", "").lower() == "fail"
            and tc.get("responsible_agent") == agent_name
        ]
        
        if failed_tests:
            feedback_parts.append("\nFailed test cases:")
            for tc in failed_tests:
                feedback_parts.append(f"  - {tc.get('id', 'N/A')}: {tc.get('description', 'N/A')}")
                if tc.get('notes'):
                    feedback_parts.append(f"    Notes: {tc.get('notes')}")
        
        recommendations = self.test_report.get("recommendations", [])
        if recommendations:
            feedback_parts.append("\nRecommendations:")
            for rec in recommendations:
                feedback_parts.append(f"  - {rec}")
        
        return "\n".join(feedback_parts) if feedback_parts else ""
    
    def _format_previous_output_summary(self, agent_name: str) -> str:
        """Format previous output for an agent to reference during iteration."""
        if agent_name == AGENT_PRODUCT_OWNER and self.user_stories:
            return f"\n## Your Previous User Stories (to be updated):\n{self._format_user_stories_summary()}"
        elif agent_name == AGENT_ARCHITECT and self.system_design:
            return f"\n## Your Previous System Design (to be updated):\n{self._format_system_design_summary()}"
        elif agent_name == AGENT_BACKEND_ENGINEER and self.backend_code:
            files = self.backend_code.get("files", [])
            file_list = ", ".join(f.get("filename", "") for f in files)
            return f"\n## Your Previous Backend Files (to be updated): {file_list}"
        elif agent_name == AGENT_FRONTEND_ENGINEER and self.frontend_code:
            files = self.frontend_code.get("files", [])
            file_list = ", ".join(f.get("filename", "") for f in files)
            return f"\n## Your Previous Frontend Files (to be updated): {file_list}"
        return ""
    
    def _format_test_report_summary(self) -> str:
        """Format test report summary for manager context."""
        if not self.test_report:
            return "No test report available."
        
        summary_parts = ["## QA Test Report:"]
        
        overall_status = self.test_report.get("overall_status", "unknown")
        summary_parts.append(f"Overall Status: {overall_status}")
        
        summary = self.test_report.get("summary", "")
        if summary:
            summary_parts.append(f"Summary: {summary}")
        
        # Test cases
        test_cases = self.test_report.get("test_cases", [])
        if test_cases:
            passed = sum(1 for tc in test_cases if tc.get("status", "").lower() == "pass")
            failed = sum(1 for tc in test_cases if tc.get("status", "").lower() == "fail")
            summary_parts.append(f"\nTest Results: {passed} passed, {failed} failed, {len(test_cases)} total")
            
            # List failed tests
            failed_tests = [tc for tc in test_cases if tc.get("status", "").lower() == "fail"]
            if failed_tests:
                summary_parts.append("\nFailed Tests:")
                for tc in failed_tests:
                    responsible = tc.get("responsible_agent", "unknown")
                    summary_parts.append(f"  - [{tc.get('id')}] {tc.get('description')} (responsible: {responsible})")
                    if tc.get("notes"):
                        summary_parts.append(f"    Notes: {tc.get('notes')}")
        
        # Issues by agent
        issues_by_agent = self.test_report.get("issues_by_agent", {})
        has_issues = any(issues for issues in issues_by_agent.values())
        if has_issues:
            summary_parts.append("\nIssues by Agent:")
            for agent, issues in issues_by_agent.items():
                if issues:
                    summary_parts.append(f"  {agent}:")
                    for issue in issues:
                        summary_parts.append(f"    - {issue}")
        
        # Recommendations
        recommendations = self.test_report.get("recommendations", [])
        if recommendations:
            summary_parts.append("\nRecommendations:")
            for rec in recommendations:
                summary_parts.append(f"  - {rec}")
        
        return "\n".join(summary_parts)
    
    def get_context_for_product_owner(self, is_iteration: bool = False) -> str:
        """Get context for Product Owner."""
        context_parts = [f"## Project Requirements:\n{self.vibe_prompt}"]
        
        if is_iteration:
            prev_output = self._format_previous_output_summary(AGENT_PRODUCT_OWNER)
            if prev_output:
                context_parts.append(prev_output)
            
            qa_feedback = self._format_qa_feedback(AGENT_PRODUCT_OWNER)
            if qa_feedback:
                context_parts.append(f"\n## QA Feedback (Please address these issues):\n{qa_feedback}")
        
        return "\n\n".join(context_parts)
    
    def get_context_for_architect(self, is_iteration: bool = False) -> str:
        """Get context for Architect."""
        context_parts = [self._format_user_stories_summary()]
        
        if is_iteration:
            prev_output = self._format_previous_output_summary(AGENT_ARCHITECT)
            if prev_output:
                context_parts.append(prev_output)
            
            qa_feedback = self._format_qa_feedback(AGENT_ARCHITECT)
            if qa_feedback:
                context_parts.append(f"\n## QA Feedback (Please address these issues):\n{qa_feedback}")
        
        return "\n\n".join(context_parts)
    
    def get_context_for_backend_engineer(self, is_iteration: bool = False) -> str:
        """Get context for Backend Engineer."""
        context_parts = [
            self._format_user_stories_summary(),
            self._format_system_design_summary()
        ]
        
        if is_iteration:
            prev_output = self._format_previous_output_summary(AGENT_BACKEND_ENGINEER)
            if prev_output:
                context_parts.append(prev_output)
            
            qa_feedback = self._format_qa_feedback(AGENT_BACKEND_ENGINEER)
            if qa_feedback:
                context_parts.append(f"\n## QA Feedback (Please address these issues):\n{qa_feedback}")
        
        return "\n\n".join(context_parts)
    
    def get_context_for_frontend_engineer(self, is_iteration: bool = False) -> str:
        """Get context for Frontend Engineer."""
        context_parts = [
            self._format_user_stories_summary(),
            self._format_system_design_summary(),
            self._format_backend_endpoints_summary()
        ]
        
        if is_iteration:
            prev_output = self._format_previous_output_summary(AGENT_FRONTEND_ENGINEER)
            if prev_output:
                context_parts.append(prev_output)
            
            qa_feedback = self._format_qa_feedback(AGENT_FRONTEND_ENGINEER)
            if qa_feedback:
                context_parts.append(f"\n## QA Feedback (Please address these issues):\n{qa_feedback}")
        
        return "\n\n".join(context_parts)
    
    def get_context_for_qa_engineer(self) -> str:
        """Get context for QA Engineer."""
        context_parts = [
            self._format_user_stories_summary(),
            self._format_system_design_summary(),
            self._format_backend_code_full(),
            self._format_frontend_code_full()
        ]
        
        return "\n\n".join(context_parts)
    
    def get_context_for_manager(self, iteration: int, max_iterations: int) -> str:
        """Get context for Manager to make decisions."""
        context_parts = [
            f"## Iteration Status: {iteration}/{max_iterations}",
            f"\n## Original Requirements:\n{self.vibe_prompt}",
            f"\n{self._format_test_report_summary()}"
        ]
        
        return "\n\n".join(context_parts)
    
    def clear(self):
        """Clear all stored context data to free memory."""
        self.vibe_prompt = ""
        self.user_stories = None
        self.system_design = None
        self.backend_code = None
        self.frontend_code = None
        self.test_report = None


class PentagonCrew:
    """
    Pentagon Protocol - 5-Agent Hierarchical Framework with Manager Coordination
    Enhanced with iterative QA feedback loop, guardrails, retries,
    memory-efficient context management, truncation recovery, and robust output handling
    """
    
    MAX_QA_ITERATIONS = 5
    MAX_RETRIES = 2
    
    def __init__(self, verbose: bool = True, output_dir: str = "output"):
        self.verbose = verbose
        self.output_dir = output_dir
        self.execution_log = []
        self.context_manager = ContextManager()
        
    def _log(self, message: str):
        """Log execution progress."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.execution_log.append(log_entry)
        if self.verbose:
            print(log_entry)
    
    def _create_project_dir(self, vibe_prompt: str) -> Path:
        """Create project output directory."""
        safe_name = "".join(c if c.isalnum() or c in ' -_' else '_' for c in vibe_prompt[:40])
        safe_name = safe_name.strip().replace(' ', '_').lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = f"{safe_name}_{timestamp}"
        
        project_dir = Path(self.output_dir) / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        (project_dir / "phases").mkdir(exist_ok=True)
        (project_dir / "backend").mkdir(exist_ok=True)
        (project_dir / "frontend").mkdir(exist_ok=True)
        
        return project_dir
    
    def _save_json(self, path: Path, data: Any):
        """Save data as JSON."""
        with open(path, 'w', encoding='utf-8') as f:
            if isinstance(data, str):
                f.write(data)
            else:
                json.dump(data, f, indent=2, default=str)
    
    def _extract_output(self, task_output, schema_class=None) -> Dict[str, Any]:
        """Extract and validate output from task."""
        result = {
            "success": False,
            "data": None,
            "raw": "",
            "error": None
        }
        
        try:
            # Get raw output
            if hasattr(task_output, 'raw'):
                result["raw"] = task_output.raw
            elif hasattr(task_output, 'result'):
                result["raw"] = str(task_output.result)
            else:
                result["raw"] = str(task_output)
            
            # Try pydantic output first
            if hasattr(task_output, 'pydantic') and task_output.pydantic:
                result["data"] = task_output.pydantic.model_dump()
                result["success"] = True
                return result
            
            # Try json_dict
            if hasattr(task_output, 'json_dict') and task_output.json_dict:
                result["data"] = task_output.json_dict
                result["success"] = True
                return result
            
            # Parse raw output with recovery
            success, parsed = safe_parse_json(result["raw"], schema_class)
            if success:
                if hasattr(parsed, 'model_dump'):
                    result["data"] = parsed.model_dump()
                else:
                    result["data"] = parsed
                result["success"] = True
            else:
                result["error"] = parsed
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _execute_task_with_recovery(
        self,
        agent: Agent,
        task: Task,
        schema_class,
        max_retries: int = None
    ) -> Dict[str, Any]:
        """Execute a task with retry and truncation recovery."""
        if max_retries is None:
            max_retries = self.MAX_RETRIES
            
        last_error = None
        last_raw = ""
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self._log(f"    Retry attempt {attempt}/{max_retries}...")
                
                # Create a fresh crew for each attempt
                crew = Crew(
                    agents=[agent],
                    tasks=[task],
                    process=Process.sequential,
                    verbose=self.verbose
                )
                crew.kickoff()
                
                # Extract output
                output = self._extract_output(task.output, schema_class)
                
                if output.get("success"):
                    if attempt > 0:
                        self._log(f"    Success on retry {attempt}")
                    return output
                
                last_error = output.get("error", "Unknown extraction error")
                last_raw = output.get("raw", "")
                self._log(f"    Extraction failed: {last_error}")
                
            except Exception as e:
                last_error = str(e)
                self._log(f"    Attempt {attempt + 1} failed: {last_error}")
                
                # Try to extract raw output from task even on exception
                if hasattr(task, 'output') and task.output:
                    if hasattr(task.output, 'raw'):
                        last_raw = task.output.raw
                    else:
                        last_raw = str(task.output)
        
        # Final attempt: try to recover from last raw output
        if last_raw:
            self._log(f"    Attempting final recovery from raw output...")
            try:
                success, parsed = safe_parse_json(last_raw, schema_class)
                if success:
                    self._log(f"    Recovery successful!")
                    if hasattr(parsed, 'model_dump'):
                        return {
                            "success": True,
                            "data": parsed.model_dump(),
                            "raw": last_raw,
                            "error": None
                        }
                    else:
                        return {
                            "success": True,
                            "data": parsed,
                            "raw": last_raw,
                            "error": None
                        }
            except Exception as recovery_error:
                self._log(f"    Recovery failed: {recovery_error}")
        
        return {
            "success": False,
            "data": None,
            "raw": last_raw,
            "error": f"Failed after {max_retries + 1} attempts. Last error: {last_error}"
        }
    
    def _create_manager_decision_task(self, manager_agent: Agent, context: str) -> Task:
        """Create a task for the manager to decide which agents need to re-run."""
        return Task(
            description=f"""You are the Project Manager. Review the QA test report and decide which team members need to fix issues.

{context}

Based on the QA report, analyze:
1. Which agents are responsible for the failed tests?
2. Are there any dependency implications? (e.g., if architect needs changes, backend and frontend may need updates too)
3. Should we continue iterating or is the project good enough?

Return ONLY this JSON structure (no markdown, no extra text):
{{
    "should_continue": true,
    "agents_to_rerun": ["backend_engineer", "frontend_engineer"],
    "reasoning": "Brief explanation of why these agents need to re-run",
    "iteration_goal": "Specific goal for this iteration"
}}

RULES:
- should_continue: true if there are issues to fix, false if QA passed or issues are minor
- agents_to_rerun: list of agent identifiers that need to fix issues
  Valid values: "product_owner", "architect", "backend_engineer", "frontend_engineer"
- Include dependent agents (if architect re-runs, include backend_engineer and frontend_engineer)
- Keep reasoning and iteration_goal under 100 characters each
- Return ONLY valid JSON""",
            expected_output="""Valid JSON with should_continue, agents_to_rerun, reasoning, and iteration_goal""",
            agent=manager_agent
        )
    
    def _get_manager_decision(
        self, 
        manager_agent: Agent, 
        iteration: int,
        max_iterations: int
    ) -> ManagerDecision:
        """Get the manager's decision about which agents need to re-run."""
        decision = ManagerDecision()
        
        try:
            context = self.context_manager.get_context_for_manager(iteration, max_iterations)
            task = self._create_manager_decision_task(manager_agent, context)
            
            crew = Crew(
                agents=[manager_agent],
                tasks=[task],
                process=Process.sequential,
                verbose=self.verbose
            )
            crew.kickoff()
            
            # Extract manager's decision
            raw = task.output.raw if hasattr(task.output, 'raw') else str(task.output)
            success, parsed = safe_parse_json(raw)
            
            if success and isinstance(parsed, dict):
                decision.should_continue = parsed.get("should_continue", False)
                decision.agents_to_rerun = parsed.get("agents_to_rerun", [])
                decision.reasoning = parsed.get("reasoning", "")
                decision.iteration_goal = parsed.get("iteration_goal", "")
                
                # Validate agent names
                valid_agents = [AGENT_PRODUCT_OWNER, AGENT_ARCHITECT, AGENT_BACKEND_ENGINEER, AGENT_FRONTEND_ENGINEER]
                decision.agents_to_rerun = [a for a in decision.agents_to_rerun if a in valid_agents]
                
                # Add dependencies
                decision.agents_to_rerun = self._add_agent_dependencies(decision.agents_to_rerun)
            else:
                self._log(f"    Manager decision parsing failed, using fallback")
                decision = self._get_fallback_decision()
                
        except Exception as e:
            self._log(f"    Manager decision error: {e}, using fallback")
            decision = self._get_fallback_decision()
        
        return decision
    
    def _get_fallback_decision(self) -> ManagerDecision:
        """Get fallback decision based on QA report when manager fails."""
        decision = ManagerDecision()
        
        qa_output = {"success": True, "data": self.context_manager.test_report}
        
        if self._check_qa_passed(qa_output):
            decision.should_continue = False
            decision.reasoning = "QA passed, no issues found"
        else:
            agents_with_issues = self._get_agents_with_issues_from_report()
            if agents_with_issues:
                decision.should_continue = True
                decision.agents_to_rerun = self._add_agent_dependencies(list(agents_with_issues))
                decision.reasoning = f"Issues found for: {', '.join(agents_with_issues)}"
                decision.iteration_goal = "Fix identified issues"
            else:
                decision.should_continue = False
                decision.reasoning = "No specific agents identified with issues"
        
        return decision
    
    def _get_agents_with_issues_from_report(self) -> Set[str]:
        """Extract which agents have issues from the stored test report."""
        agents_with_issues = set()
        
        if not self.context_manager.test_report:
            return agents_with_issues
        
        data = self.context_manager.test_report
        
        # Check issues_by_agent field
        issues_by_agent = data.get("issues_by_agent", {})
        for agent, issues in issues_by_agent.items():
            if issues:
                agents_with_issues.add(agent)
        
        # Check test_cases for responsible_agent on failed tests
        test_cases = data.get("test_cases", [])
        for tc in test_cases:
            if isinstance(tc, dict):
                status = tc.get("status", "").lower()
                responsible_agent = tc.get("responsible_agent", "")
                if status == "fail" and responsible_agent:
                    agents_with_issues.add(responsible_agent)
        
        return agents_with_issues
    
    def _add_agent_dependencies(self, agents: List[str]) -> List[str]:
        """Add dependent agents and return in correct execution order."""
        agents_to_rerun = set(agents)
        
        # Add downstream dependencies
        for agent in agents:
            if agent in AGENT_DEPENDENCIES:
                agents_to_rerun.update(AGENT_DEPENDENCIES[agent])
        
        # Return in correct execution order
        execution_order = [
            AGENT_PRODUCT_OWNER,
            AGENT_ARCHITECT,
            AGENT_BACKEND_ENGINEER,
            AGENT_FRONTEND_ENGINEER
        ]
        
        return [agent for agent in execution_order if agent in agents_to_rerun]
    
    def _save_code_files(self, project_dir: Path, code_output: Dict, subfolder: str):
        """Save code files to disk."""
        if not code_output or "files" not in code_output:
            return
        
        target_dir = project_dir / subfolder
        for file_info in code_output["files"]:
            if isinstance(file_info, dict) and "filename" in file_info and "content" in file_info:
                filepath = target_dir / file_info["filename"]
                content = file_info["content"]
                if isinstance(content, str):
                    # Unescape content
                    content = content.replace('\\n', '\n').replace('\\t', '\t')
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._log(f"    Saved: {filepath}")
    
    def _create_readme(self, project_dir: Path, vibe_prompt: str, results: Dict):
        """Create README for the project."""
        test_report_data = results.get('phases', {}).get('test_report', {}).get('data', {})
        overall_status = test_report_data.get('overall_status', 'N/A') if test_report_data else 'N/A'
        
        readme_content = f"""# Generated Project

            ## Original Vibe Prompt
            {vibe_prompt}

            ## Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            ## Project Structure
            ```
            {project_dir.name}/
            ├── backend/          # Python FastAPI backend
            ├── frontend/         # HTML/CSS/JS frontend
            ├── phases/           # Intermediate outputs
            └── README.md
            ```

            ## How to Run

            ### Backend
            ```bash
            cd backend
            pip install fastapi uvicorn
            uvicorn main:app --reload --port 8000
            ```

            ### Frontend
            ```bash
            cd frontend
            # Open index.html in a browser
            # Or use a simple server:
            python -m http.server 3000
            ```

            ## Test Results
            - Overall Status: {overall_status}
            - QA Iterations: {results.get('qa_iterations', 'N/A')}
            - Success: {results.get('success', False)}

            ## Errors
            {chr(10).join(results.get('errors', [])) if results.get('errors') else 'None'}

            Generated by Pentagon Protocol - Schema-Guided Vibe Coding Framework
            """
        
        with open(project_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)

    def _check_qa_passed(self, qa_output: Dict[str, Any]) -> bool:
        """Check if QA has no issues (pass condition)."""
        if not qa_output or not qa_output.get("success"):
            return False
        
        data = qa_output.get("data", {})
        
        # Check overall_status is "pass"
        overall_status = data.get("overall_status", "").lower()
        if overall_status != "pass":
            return False
        
        # Check all test cases passed (no failed tests)
        test_cases = data.get("test_cases", [])
        for tc in test_cases:
            if isinstance(tc, dict) and tc.get("status", "").lower() == "fail":
                return False
        
        return True

    def _get_agents_with_issues(self, qa_output: Dict[str, Any]) -> Set[str]:
        """Extract which agents have issues from QA report."""
        agents_with_issues = set()
        
        if not qa_output or not qa_output.get("success"):
            return agents_with_issues
        
        data = qa_output.get("data", {})
        
        # Check issues_by_agent field first
        issues_by_agent = data.get("issues_by_agent", {})
        for agent, issues in issues_by_agent.items():
            if issues:
                agents_with_issues.add(agent)
        
        # Also check test_cases for responsible_agent on failed tests
        test_cases = data.get("test_cases", [])
        for tc in test_cases:
            if isinstance(tc, dict):
                status = tc.get("status", "").lower()
                responsible_agent = tc.get("responsible_agent", "")
                if status == "fail" and responsible_agent:
                    agents_with_issues.add(responsible_agent)
        
        return agents_with_issues

    def _save_phase_outputs(self, project_dir: Path, phase_outputs: Dict):
        """Save all phase outputs to disk."""
        phase_files = {
            "user_stories": "01_user_stories.json",
            "system_design": "02_system_design.json",
            "backend_code": "03_backend_code.json",
            "frontend_code": "04_frontend_code.json",
            "test_report": "05_test_report.json",
        }
        
        for phase_name, filename in phase_files.items():
            output = phase_outputs.get(phase_name)
            if output:
                save_data = output["data"] if output.get("success") else {
                    "raw": output.get("raw", ""),
                    "error": output.get("error")
                }
                self._save_json(project_dir / "phases" / filename, save_data)

    def _log_phase_results(self, phase_outputs: Dict):
        """Log results of each phase."""
        if phase_outputs.get("user_stories") and phase_outputs["user_stories"].get("success"):
            story_count = len(phase_outputs["user_stories"]["data"].get("stories", []))
            self._log(f"    User Stories: {story_count} stories created")
        elif phase_outputs.get("user_stories"):
            self._log(f"    User Stories: FAILED - {phase_outputs['user_stories'].get('error', 'Unknown error')[:50]}")
        
        if phase_outputs.get("system_design") and phase_outputs["system_design"].get("success"):
            model_count = len(phase_outputs["system_design"]["data"].get("models", []))
            endpoint_count = len(phase_outputs["system_design"]["data"].get("endpoints", []))
            self._log(f"    System Design: {model_count} models, {endpoint_count} endpoints")
        elif phase_outputs.get("system_design"):
            self._log(f"    System Design: FAILED - {phase_outputs['system_design'].get('error', 'Unknown error')[:50]}")
        
        if phase_outputs.get("backend_code") and phase_outputs["backend_code"].get("success"):
            file_count = len(phase_outputs["backend_code"]["data"].get("files", []))
            self._log(f"    Backend Code: {file_count} files created")
        elif phase_outputs.get("backend_code"):
            self._log(f"    Backend Code: FAILED - {phase_outputs['backend_code'].get('error', 'Unknown error')[:50]}")
        
        if phase_outputs.get("frontend_code") and phase_outputs["frontend_code"].get("success"):
            file_count = len(phase_outputs["frontend_code"]["data"].get("files", []))
            self._log(f"    Frontend Code: {file_count} files created")
        elif phase_outputs.get("frontend_code"):
            self._log(f"    Frontend Code: FAILED - {phase_outputs['frontend_code'].get('error', 'Unknown error')[:50]}")
        
        if phase_outputs.get("test_report") and phase_outputs["test_report"].get("success"):
            status = phase_outputs["test_report"]["data"].get("overall_status", "unknown")
            test_count = len(phase_outputs["test_report"]["data"].get("test_cases", []))
            self._log(f"    Test Report: {test_count} tests, Status: {status}")
        elif phase_outputs.get("test_report"):
            self._log(f"    Test Report: FAILED - {phase_outputs['test_report'].get('error', 'Unknown error')[:50]}")

    def _cleanup_memory(self):
        """Clean up memory after project completion."""
        self._log("Cleaning up memory...")
        
        # Clear context manager
        self.context_manager.clear()
        
        # Force garbage collection
        gc.collect()
        
        self._log("Memory cleanup complete.")

    def _create_task_with_context(
        self, 
        task_factory, 
        agent: Agent, 
        context_str: str,
        original_arg: Any = None
    ) -> Task:
        """Create a task with custom context string injected into description."""
        # Create the base task
        task = task_factory(agent, original_arg)
        
        # Inject context into task description
        if context_str:
            task.description = f"{task.description}\n\n--- CONTEXT ---\n{context_str}"
        
        return task

    def run(self, vibe_prompt: str) -> Dict[str, Any]:
        """
        Execute the Pentagon Protocol pipeline with iterative QA feedback.
        
        Args:
            vibe_prompt: The ambiguous user requirement
            
        Returns:
            Dict with execution results and outputs
        """
        start_time = time.time()
        self.execution_log = []
        self.context_manager = ContextManager()
        self.context_manager.vibe_prompt = vibe_prompt
        
        self._log(f"Starting Pentagon Protocol")
        self._log(f"Vibe Prompt: {vibe_prompt}")
        
        project_dir = self._create_project_dir(vibe_prompt)
        self._log(f"Output directory: {project_dir}")
        
        results = {
            "success": False,
            "vibe_prompt": vibe_prompt,
            "project_dir": str(project_dir),
            "phases": {},
            "errors": [],
            "qa_iterations": 0,
            "manager_decisions": [],
        }
        
        try:
            # ============================================================
            # INITIALIZE AGENTS
            # ============================================================
            self._log("\n" + "="*50)
            self._log("Initializing Agents")
            self._log("="*50)
            
            manager_agent = create_manager_agent()
            self._log(f"  Manager: {manager_agent.role}")
            
            agents = {
                AGENT_PRODUCT_OWNER: create_product_owner(),
                AGENT_ARCHITECT: create_architect(),
                AGENT_BACKEND_ENGINEER: create_backend_engineer(),
                AGENT_FRONTEND_ENGINEER: create_frontend_engineer(),
                AGENT_QA_ENGINEER: create_qa_engineer(),
            }
            
            for name, agent in agents.items():
                self._log(f"  {name}: {agent.role}")
            
            # Store current outputs for each phase
            phase_outputs = {
                "user_stories": None,
                "system_design": None,
                "backend_code": None,
                "frontend_code": None,
                "test_report": None,
            }
            
            # ============================================================
            # INITIAL RUN: All agents work on their tasks
            # ============================================================
            self._log("\n" + "="*50)
            self._log("INITIAL RUN: Full Pipeline Execution")
            self._log("="*50)
            
            # Phase 1: Product Owner - User Stories
            self._log("\n  Phase 1: Product Owner - User Stories")
            po_context = self.context_manager.get_context_for_product_owner(is_iteration=False)
            po_task = self._create_task_with_context(
                create_user_stories_task,
                agents[AGENT_PRODUCT_OWNER],
                po_context,
                vibe_prompt
            )
            
            phase_outputs["user_stories"] = self._execute_task_with_recovery(
                agents[AGENT_PRODUCT_OWNER],
                po_task,
                UserStoriesOutput
            )
            self.context_manager.update_user_stories(phase_outputs["user_stories"])
            
            if not phase_outputs["user_stories"].get("success"):
                error_msg = phase_outputs["user_stories"].get("error", "Unknown error")
                self._log(f"    WARNING: User stories generation failed: {error_msg[:100]}")
                results["errors"].append(f"User Stories: {error_msg}")
            
            # Phase 2: Architect - System Design
            self._log("\n  Phase 2: Architect - System Design")
            arch_context = self.context_manager.get_context_for_architect(is_iteration=False)
            arch_task = self._create_task_with_context(
                create_system_design_task,
                agents[AGENT_ARCHITECT],
                arch_context,
                []
            )
            
            phase_outputs["system_design"] = self._execute_task_with_recovery(
                agents[AGENT_ARCHITECT],
                arch_task,
                SystemDesign
            )
            self.context_manager.update_system_design(phase_outputs["system_design"])
            
            if not phase_outputs["system_design"].get("success"):
                error_msg = phase_outputs["system_design"].get("error", "Unknown error")
                self._log(f"    WARNING: System design generation failed: {error_msg[:100]}")
                results["errors"].append(f"System Design: {error_msg}")
            
            # Phase 3: Backend Engineer - Backend Code
            self._log("\n  Phase 3: Backend Engineer - Backend Code")
            be_context = self.context_manager.get_context_for_backend_engineer(is_iteration=False)
            be_task = self._create_task_with_context(
                create_backend_task,
                agents[AGENT_BACKEND_ENGINEER],
                be_context,
                []
            )
            
            phase_outputs["backend_code"] = self._execute_task_with_recovery(
                agents[AGENT_BACKEND_ENGINEER],
                be_task,
                BackendCode
            )
            self.context_manager.update_backend_code(phase_outputs["backend_code"])
            
            if not phase_outputs["backend_code"].get("success"):
                error_msg = phase_outputs["backend_code"].get("error", "Unknown error")
                self._log(f"    WARNING: Backend code generation failed: {error_msg[:100]}")
                results["errors"].append(f"Backend Code: {error_msg}")
            
            # Phase 4: Frontend Engineer - Frontend Code
            self._log("\n  Phase 4: Frontend Engineer - Frontend Code")
            fe_context = self.context_manager.get_context_for_frontend_engineer(is_iteration=False)
            fe_task = self._create_task_with_context(
                create_frontend_task,
                agents[AGENT_FRONTEND_ENGINEER],
                fe_context,
                []
            )
            
            phase_outputs["frontend_code"] = self._execute_task_with_recovery(
                agents[AGENT_FRONTEND_ENGINEER],
                fe_task,
                FrontendCode
            )
            self.context_manager.update_frontend_code(phase_outputs["frontend_code"])
            
            if not phase_outputs["frontend_code"].get("success"):
                error_msg = phase_outputs["frontend_code"].get("error", "Unknown error")
                self._log(f"    WARNING: Frontend code generation failed: {error_msg[:100]}")
                results["errors"].append(f"Frontend Code: {error_msg}")
            
            # Phase 5: QA Engineer - Test Report
            self._log("\n  Phase 5: QA Engineer - Test Report")
            qa_context = self.context_manager.get_context_for_qa_engineer()
            qa_task = self._create_task_with_context(
                create_qa_task,
                agents[AGENT_QA_ENGINEER],
                qa_context,
                []
            )
            
            phase_outputs["test_report"] = self._execute_task_with_recovery(
                agents[AGENT_QA_ENGINEER],
                qa_task,
                TestReport
            )
            self.context_manager.update_test_report(phase_outputs["test_report"])
            
            if not phase_outputs["test_report"].get("success"):
                error_msg = phase_outputs["test_report"].get("error", "Unknown error")
                self._log(f"    WARNING: Test report generation failed: {error_msg[:100]}")
                results["errors"].append(f"Test Report: {error_msg}")
            
            results["qa_iterations"] = 1
            
            # Save initial outputs
            self._save_phase_outputs(project_dir, phase_outputs)
            
            # Log initial results
            self._log("\n  Initial Run Results:")
            self._log_phase_results(phase_outputs)
            
            # ============================================================
            # ITERATIVE QA FEEDBACK LOOP WITH MANAGER COORDINATION
            # ============================================================
            while results["qa_iterations"] < self.MAX_QA_ITERATIONS:
                qa_output = phase_outputs["test_report"]
                
                # Check if QA passed (no issues)
                if self._check_qa_passed(qa_output):
                    self._log("\n" + "="*50)
                    self._log("QA PASSED - No issues found!")
                    self._log("="*50)
                    break
                
                # Check if QA failed to generate
                if not qa_output or not qa_output.get("success"):
                    self._log("\nQA report generation failed. Ending iteration loop.")
                    break
                
                # ============================================================
                # MANAGER DECISION
                # ============================================================
                self._log("\n" + "="*50)
                self._log(f"MANAGER REVIEW: Iteration {results['qa_iterations']}")
                self._log("="*50)
                
                decision = self._get_manager_decision(
                    manager_agent,
                    results["qa_iterations"],
                    self.MAX_QA_ITERATIONS
                )
                
                # Store decision for logging
                results["manager_decisions"].append({
                    "iteration": results["qa_iterations"],
                    "should_continue": decision.should_continue,
                    "agents_to_rerun": decision.agents_to_rerun,
                    "reasoning": decision.reasoning,
                    "iteration_goal": decision.iteration_goal
                })
                
                self._log(f"  Manager Decision:")
                self._log(f"    Continue: {decision.should_continue}")
                self._log(f"    Agents to re-run: {decision.agents_to_rerun}")
                self._log(f"    Reasoning: {decision.reasoning}")
                self._log(f"    Goal: {decision.iteration_goal}")
                
                if not decision.should_continue:
                    self._log("\n  Manager decided to stop iterations.")
                    break
                
                if not decision.agents_to_rerun:
                    self._log("\n  No agents identified to re-run. Ending iteration loop.")
                    break
                
                # ============================================================
                # EXECUTE FIXES
                # ============================================================
                self._log("\n" + "="*50)
                self._log(f"ITERATION {results['qa_iterations'] + 1}: {decision.iteration_goal}")
                self._log("="*50)
                
                # Execute tasks for agents that need to re-run (in order)
                for agent_name in decision.agents_to_rerun:
                    if agent_name == AGENT_PRODUCT_OWNER:
                        self._log(f"\n  Re-running: Product Owner")
                        po_context = self.context_manager.get_context_for_product_owner(is_iteration=True)
                        po_task = self._create_task_with_context(
                            create_user_stories_task,
                            agents[AGENT_PRODUCT_OWNER],
                            po_context,
                            vibe_prompt
                        )
                        
                        phase_outputs["user_stories"] = self._execute_task_with_recovery(
                            agents[AGENT_PRODUCT_OWNER],
                            po_task,
                            UserStoriesOutput
                        )
                        self.context_manager.update_user_stories(phase_outputs["user_stories"])
                        
                        if not phase_outputs["user_stories"].get("success"):
                            self._log(f"    WARNING: User stories re-generation failed")
                        
                    elif agent_name == AGENT_ARCHITECT:
                        self._log(f"\n  Re-running: Architect")
                        arch_context = self.context_manager.get_context_for_architect(is_iteration=True)
                        arch_task = self._create_task_with_context(
                            create_system_design_task,
                            agents[AGENT_ARCHITECT],
                            arch_context,
                            []
                        )
                        
                        phase_outputs["system_design"] = self._execute_task_with_recovery(
                            agents[AGENT_ARCHITECT],
                            arch_task,
                            SystemDesign
                        )
                        self.context_manager.update_system_design(phase_outputs["system_design"])
                        
                        if not phase_outputs["system_design"].get("success"):
                            self._log(f"    WARNING: System design re-generation failed")
                        
                    elif agent_name == AGENT_BACKEND_ENGINEER:
                        self._log(f"\n  Re-running: Backend Engineer")
                        be_context = self.context_manager.get_context_for_backend_engineer(is_iteration=True)
                        be_task = self._create_task_with_context(
                            create_backend_task,
                            agents[AGENT_BACKEND_ENGINEER],
                            be_context,
                            []
                        )
                        
                        phase_outputs["backend_code"] = self._execute_task_with_recovery(
                            agents[AGENT_BACKEND_ENGINEER],
                            be_task,
                            BackendCode
                        )
                        self.context_manager.update_backend_code(phase_outputs["backend_code"])
                        
                        if not phase_outputs["backend_code"].get("success"):
                            self._log(f"    WARNING: Backend code re-generation failed")
                        
                    elif agent_name == AGENT_FRONTEND_ENGINEER:
                        self._log(f"\n  Re-running: Frontend Engineer")
                        fe_context = self.context_manager.get_context_for_frontend_engineer(is_iteration=True)
                        fe_task = self._create_task_with_context(
                            create_frontend_task,
                            agents[AGENT_FRONTEND_ENGINEER],
                            fe_context,
                            []
                        )
                        
                        phase_outputs["frontend_code"] = self._execute_task_with_recovery(
                            agents[AGENT_FRONTEND_ENGINEER],
                            fe_task,
                            FrontendCode
                        )
                        self.context_manager.update_frontend_code(phase_outputs["frontend_code"])
                        
                        if not phase_outputs["frontend_code"].get("success"):
                            self._log(f"    WARNING: Frontend code re-generation failed")
                
                # Run QA after all fixes
                self._log(f"\n  Re-running: QA Engineer")
                qa_context = self.context_manager.get_context_for_qa_engineer()
                qa_task = self._create_task_with_context(
                    create_qa_task,
                    agents[AGENT_QA_ENGINEER],
                    qa_context,
                    []
                )
                
                phase_outputs["test_report"] = self._execute_task_with_recovery(
                    agents[AGENT_QA_ENGINEER],
                    qa_task,
                    TestReport
                )
                self.context_manager.update_test_report(phase_outputs["test_report"])
                
                results["qa_iterations"] += 1
                
                # Save updated outputs (overwrite)
                self._save_phase_outputs(project_dir, phase_outputs)
                
                # Log iteration results
                self._log(f"\n  Iteration {results['qa_iterations']} Results:")
                self._log_phase_results(phase_outputs)
            
            # ============================================================
            # FINALIZE
            # ============================================================
            results["phases"] = phase_outputs
            
            # Save code files
            if phase_outputs.get("backend_code") and phase_outputs["backend_code"].get("success"):
                self._log("\n  Saving backend code files...")
                self._save_code_files(project_dir, phase_outputs["backend_code"]["data"], "backend")
            
            if phase_outputs.get("frontend_code") and phase_outputs["frontend_code"].get("success"):
                self._log("  Saving frontend code files...")
                self._save_code_files(project_dir, phase_outputs["frontend_code"]["data"], "frontend")
            
            execution_time = time.time() - start_time
            results["execution_time_seconds"] = round(execution_time, 2)
            results["timestamp"] = datetime.now().isoformat()
            results["execution_log"] = self.execution_log
            
            # Determine overall success
            successful_phases = sum(1 for p in phase_outputs.values() if p and p.get("success", False))
            qa_passed = self._check_qa_passed(phase_outputs["test_report"])
            results["success"] = successful_phases >= 4 and qa_passed
            results["phases_succeeded"] = successful_phases
            results["qa_passed"] = qa_passed
            
            # Create README
            self._create_readme(project_dir, vibe_prompt, results)
            
            # Save final results
            self._save_json(project_dir / "experiment_results.json", results)
            
            self._log("\n" + "="*50)
            self._log(f"Pentagon Protocol Complete")
            self._log(f"  Success: {results['success']} ({successful_phases}/5 phases)")
            self._log(f"  QA Passed: {qa_passed}")
            self._log(f"  QA Iterations: {results['qa_iterations']}")
            self._log(f"  Execution Time: {execution_time:.2f}s")
            self._log(f"  Output: {project_dir}")
            self._log("="*50)
            
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
            results["execution_time_seconds"] = round(time.time() - start_time, 2)
            self._log(f"CRITICAL ERROR: {str(e)}")
            
            import traceback
            self._log(traceback.format_exc())
            
            self._save_json(project_dir / "experiment_results.json", results)
        
        finally:
            # Always cleanup memory after project completion
            self._cleanup_memory()
        
        return results
    

class BaselineCrew: 
    """ Baseline - Single Agent for Comparison """

    def __init__(self, verbose: bool = True, output_dir: str = "output"):
        self.verbose = verbose
        self.output_dir = output_dir
        self.execution_log = []

    def _log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.execution_log.append(log_entry)
        if self.verbose:
            print(log_entry)

    def run(self, vibe_prompt: str) -> Dict[str, Any]:
        """Execute baseline single-agent approach."""
        start_time = time.time()
        self.execution_log = []
        
        self._log(f"Starting Baseline (Single Agent)")
        self._log(f"Vibe Prompt: {vibe_prompt}")
        
        # Create output directory
        safe_name = "".join(c if c.isalnum() or c in ' -_' else '_' for c in vibe_prompt[:30])
        safe_name = safe_name.strip().replace(' ', '_').lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_dir = Path(self.output_dir) / f"baseline_{safe_name}_{timestamp}"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            "success": False,
            "vibe_prompt": vibe_prompt,
            "project_dir": str(project_dir),
            "output": None,
            "error": None,
        }
        
        try:
            agent = create_baseline_agent()
            task = create_baseline_task(agent, vibe_prompt)
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=self.verbose
            )
            
            result = crew.kickoff()
            
            # Extract output
            raw = result.raw if hasattr(result, 'raw') else str(result)
            success, parsed = safe_parse_json(raw)
            
            if success:
                results["output"] = parsed
                results["success"] = True
            else:
                results["output"] = {"raw": raw}
                results["error"] = parsed
            
            # Save results
            with open(project_dir / "baseline_results.json", 'w') as f:
                json.dump(results, f, indent=2, default=str)
                
        except Exception as e:
            results["error"] = str(e)
            self._log(f"ERROR: {str(e)}")
        
        results["execution_time_seconds"] = round(time.time() - start_time, 2)
        results["timestamp"] = datetime.now().isoformat()
        results["execution_log"] = self.execution_log
        
        self._log(f"Baseline Complete: Success={results['success']}")
        
        return results