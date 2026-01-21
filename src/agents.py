"""
Pentagon Protocol - Enhanced Agent Definitions
With better prompts and deterministic configuration
"""

import os
from dotenv import load_dotenv
from crewai import Agent, LLM

load_dotenv()


def get_llm() -> LLM:
    """Get deterministic DeepSeek LLM configuration."""
    return LLM(
        model="deepseek/deepseek-chat",
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        temperature=0.0,  # Deterministic
        max_tokens=4000,
    )


# ============================================================
# ENHANCED SYSTEM PROMPTS - Key to reducing failures
# ============================================================

JSON_INSTRUCTION = """
CRITICAL INSTRUCTIONS FOR OUTPUT:
1. Return ONLY valid JSON - no markdown, no explanations, no text before or after
2. Do NOT wrap JSON in ```json``` code blocks
3. Ensure all strings are properly escaped (use \\n for newlines in code)
4. Keep code snippets SHORT (under 50 lines per file)
5. Use simple field values - avoid complex nested structures
6. Double-check that all brackets and braces are balanced
"""

def create_manager_agent() -> Agent:
    """Create the Manager agent that coordinates the team."""
    return Agent(
        role="Project Manager",
        goal="Coordinate the development team to deliver a complete, high-quality application that meets all user requirements",
        backstory="""You are an experienced Project Manager with expertise in software development lifecycle.
You coordinate between Product Owner, Architect, Backend Engineer, Frontend Engineer, and QA Engineer.
You ensure smooth collaboration, resolve blockers, and keep the team focused on delivering value.
You understand technical concepts well enough to facilitate communication between team members.
When QA reports issues, you ensure the right team members address them efficiently.
You delegate tasks to the appropriate team members and never try to do the technical work yourself.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=True,
        max_iter=15,
        max_retry_limit=5,
    )


def create_product_owner() -> Agent:
    """Create Product Owner agent with enhanced prompts."""
    return Agent(
        role="Product Owner",
        goal="Transform vague requirements into clear, actionable user stories",
        backstory="""You are a senior Product Owner with 10 years of experience. 
You excel at understanding user needs and translating them into structured requirements.
You always output in valid JSON format without any additional text.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=15,
        max_retry_limit=5,
    )


def create_architect() -> Agent:
    """Create Software Architect agent."""
    return Agent(
        role="Software Architect",
        goal="Design clean, simple system architectures with clear data models and APIs",
        backstory="""You are a pragmatic Software Architect who values simplicity.
You design systems that are easy to implement and maintain.
You always output in valid JSON format without any additional text.
You keep designs minimal but functional - only what's needed for the requirements.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=15,
        max_retry_limit=5,
    )


def create_backend_engineer() -> Agent:
    """Create Backend Engineer agent."""
    return Agent(
        role="Backend Engineer",
        goal="Write clean, working Python backend code",
        backstory="""You are a skilled Python developer specializing in FastAPI.
You write concise, functional code without unnecessary complexity.
You always output in valid JSON format without any additional text.
IMPORTANT: Keep each code file under 500 lines. Use simple implementations.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=15,
        max_retry_limit=5,
    )


def create_frontend_engineer() -> Agent:
    """Create Frontend Engineer agent."""
    return Agent(
        role="Frontend Engineer",
        goal="Create simple, functional HTML/CSS/JS frontends",
        backstory="""You are a frontend developer who creates clean, simple UIs.
You use vanilla HTML, CSS, and JavaScript - no frameworks.
You always output in valid JSON format without any additional text.
IMPORTANT: Keep HTML files under 1000 lines. Use inline styles and scripts.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=15,
        max_retry_limit=5,
    )


def create_qa_engineer() -> Agent:
    """Create QA Engineer agent."""
    return Agent(
        role="QA Engineer",
        goal="Validate that implementation meets requirements",
        backstory="""You are a thorough QA Engineer who validates code against requirements.
You check if the implementation addresses each user story.
You always output in valid JSON format without any additional text.
Be constructive - focus on what's working and what needs improvement.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=15,
        max_retry_limit=5,
    )


def create_baseline_agent() -> Agent:
    """Create single baseline agent for comparison."""
    return Agent(
        role="Full-Stack Developer",
        goal="Build complete applications from requirements to working code",
        backstory="""You are a full-stack developer who handles everything.
You analyze requirements, design systems, and write both backend and frontend code.
You always output in valid JSON format without any additional text.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=20,
        max_retry_limit=5,
    )
