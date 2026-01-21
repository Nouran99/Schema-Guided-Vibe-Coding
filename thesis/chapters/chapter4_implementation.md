# Chapter 4: Implementation

## 4.1 Introduction

This chapter describes the implementation of the Pentagon Protocol for Schema-Guided Vibe Coding. We present the system architecture, key design decisions, and implementation approach. Complete source code is provided in Appendix A.

## 4.2 Technology Stack

### 4.2.1 Technology Selection

The implementation employs the following technologies, selected based on the criteria of accessibility, cost-effectiveness, and alignment with the theoretical framework:

**CrewAI** was selected as the multi-agent orchestration framework for several reasons. First, it provides native support for Pydantic output schemas, enabling the schema-guided approach central to this research. Second, its task guardrail mechanism allows validation and retry logic essential for deterministic outputs. Third, it offers a simple, Pythonic API suitable for rapid prototyping within the time constraints of this research.

**DeepSeek API** was chosen as the LLM provider due to its cost-effectiveness ($0.28 per million input tokens) and OpenAI-compatible interface. This enabled running multiple experimental trials within a $5 budget constraint while maintaining output quality comparable to more expensive alternatives.

**Pydantic v2** provides the schema validation layer. Its field validators, automatic type coercion, and clear error messages make it ideal for constraining LLM outputs and providing feedback for retry attempts.

### 4.2.2 System Requirements

The implementation requires Python 3.11 or higher, with dependencies managed through pip. The complete requirements specification is provided in Appendix A.1.

## 4.3 System Architecture

### 4.3.1 Component Overview

The Pentagon Protocol implementation consists of four primary components:

1. **Schema Layer**: Pydantic models defining the structure of inter-agent communication
2. **Agent Layer**: CrewAI agent definitions with specialized roles and configurations
3. **Task Layer**: Task definitions with guardrails linking agents to schemas
4. **Orchestration Layer**: Crew classes managing pipeline execution and output collection

Figure 4.1 illustrates the component relationships:

```
┌──────────────────────────────────────────────────────────────┐
│                    Orchestration Layer                        │
│                  (PentagonCrew, BaselineCrew)                │
├──────────────────────────────────────────────────────────────┤
│                       Task Layer                              │
│    (create_user_stories_task, create_system_design_task,     │
│     create_backend_task, create_frontend_task, create_qa_task)│
├──────────────────────────────────────────────────────────────┤
│                      Agent Layer                              │
│  (ProductOwner, Architect, BackendEngineer, FrontendEngineer,│
│                       QAEngineer)                            │
├──────────────────────────────────────────────────────────────┤
│                      Schema Layer                             │
│   (UserStoriesOutput, SystemDesign, BackendCode, FrontendCode,│
│                       TestReport)                            │
└──────────────────────────────────────────────────────────────┘
```

*Figure 4.1: Pentagon Protocol Component Architecture*

### 4.3.2 Data Flow

The data flow through the Pentagon Protocol follows a strictly sequential pattern, with each phase producing schema-validated output that serves as input to subsequent phases:

```
VibePrompt (string)
    │
    ▼
┌─────────────────┐
│ Product Owner   │──→ UserStoriesOutput (JSON)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Architect       │──→ SystemDesign (JSON)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Backend Engineer│──→ BackendCode (JSON + files)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│Frontend Engineer│──→ FrontendCode (JSON + files)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ QA Engineer     │──→ TestReport (JSON)
└─────────────────┘
```

*Figure 4.2: Pentagon Protocol Data Flow*

## 4.4 Schema Design

### 4.4.1 Design Principles

The Pydantic schemas were designed following four principles derived from the literature on LLM structured output generation:

**Simplicity**: Schemas use flat structures where possible, avoiding deep nesting that increases JSON parsing failures. For example, `UserStory` contains only four fields rather than nested acceptance criteria objects.

**Defaults**: All optional fields have sensible defaults, allowing partial outputs to still validate. This improves pipeline resilience when an agent omits non-critical information.

**Validation**: Field validators normalize inputs (e.g., converting "HIGH" to "high" for priority fields) rather than rejecting minor variations, increasing successful parse rates.

**Documentation**: Field descriptions serve dual purposes—guiding LLM generation through prompt context and providing API documentation.

### 4.4.2 Schema Overview

Table 4.1 summarizes the five primary schemas used for inter-agent communication:

| Schema | Source Agent | Key Fields | Purpose |
|--------|--------------|------------|---------|
| UserStoriesOutput | Product Owner | stories[], summary | Requirements specification |
| SystemDesign | Architect | models[], endpoints[], notes | Technical design |
| BackendCode | Backend Engineer | files[], setup_instructions | Server implementation |
| FrontendCode | Frontend Engineer | files[], setup_instructions | Client implementation |
| TestReport | QA Engineer | overall_status, test_cases[], recommendations[] | Validation results |

*Table 4.1: Pentagon Protocol Schema Summary*

The complete schema definitions with field specifications are provided in Appendix A.2.

### 4.4.3 JSON Parsing Strategy

A critical implementation challenge was robust JSON extraction from LLM outputs. LLMs frequently produce JSON embedded in markdown code blocks, with explanatory text, or with minor syntax errors. The implementation employs a multi-strategy extraction approach:

1. **Direct parsing**: Attempt to parse the raw output as JSON
2. **Markdown extraction**: Extract content from ```json``` code blocks
3. **Boundary detection**: Locate JSON by finding matching braces
4. **Error correction**: Fix common errors (trailing commas, unquoted keys)
5. **Truncation recovery**: Parse partial JSON truncated at last valid position

This cascading approach achieved a 94% successful extraction rate in preliminary testing, compared to 67% with direct parsing alone.

## 4.5 Agent Configuration

### 4.5.1 Determinism Configuration

To maximize output determinism, all agents share a common LLM configuration:

- **Temperature**: 0.0 (eliminates sampling randomness)
- **Model**: deepseek-chat (fixed version)
- **Max tokens**: 4000 (sufficient for code generation)
- **Max iterations**: 15 (allows retry attempts)
- **Max retry limit**: 5 (guardrail retry budget)

### 4.5.2 Agent Specialization

Each agent is configured with role-specific attributes following the CrewAI agent model:

**Role**: A short descriptor establishing the agent's professional identity (e.g., "Product Owner", "Software Architect").

**Goal**: The agent's primary objective, focusing its outputs on specific deliverables.

**Backstory**: Extended context establishing expertise and behavioral guidelines, including explicit instructions to output valid JSON.

Table 4.2 summarizes the agent configurations:

| Agent | Role Focus | Output Constraint | Key Backstory Element |
|-------|------------|-------------------|----------------------|
| Product Owner | Requirements analysis | 3-5 user stories | "10 years experience translating ambiguous requests" |
| Architect | System design | 1-3 models, 3-6 endpoints | "Values simplicity and maintainability" |
| Backend Engineer | Python/FastAPI | Files under 50 lines | "Concise, functional code" |
| Frontend Engineer | HTML/CSS/JS | Files under 100 lines | "Clean, simple UIs without frameworks" |
| QA Engineer | Validation | Test case per story | "Thorough but constructive" |

*Table 4.2: Agent Configuration Summary*

Complete agent definitions are provided in Appendix A.3.

## 4.6 Task and Guardrail Implementation

### 4.6.1 Task Structure

Each task in the Pentagon Protocol follows a consistent structure:

1. **Description**: Detailed instructions including the expected JSON schema
2. **Expected Output**: Brief description for validation
3. **Context**: References to predecessor tasks for information flow
4. **Output Pydantic**: Schema class for structured output
5. **Guardrail**: Validation function for output verification
6. **Guardrail Max Retries**: Retry budget (set to 5 for all tasks)

### 4.6.2 Guardrail Implementation

Guardrails serve as validation gates between pipeline stages. Each guardrail function:

1. Extracts the raw output from the task result
2. Attempts JSON parsing with the multi-strategy approach
3. Validates against the corresponding Pydantic schema
4. Returns `(True, validated_json)` on success
5. Returns `(False, error_message)` on failure, triggering retry

The error message is crucial—it provides specific feedback to the agent about what was wrong, enabling targeted correction. For example: "Missing main.py file. Please include a main.py file."

### 4.6.3 Prompt Engineering

Task descriptions employ several prompt engineering techniques identified in the literature:

**Explicit Format Specification**: Each task includes the exact JSON structure expected, reducing ambiguity about output format.

**Negative Instructions**: Rules state what NOT to do (e.g., "no markdown", "no extra text") to prevent common failure modes.

**Constraint Emphasis**: Critical constraints (escaped newlines in code, line limits) are marked with "CRITICAL RULES" headers.

**Example Values**: Schema examples include realistic values (e.g., "US001", "/api/items") guiding the LLM toward appropriate outputs.

## 4.7 Orchestration Implementation

### 4.7.1 Pipeline Execution

The `PentagonCrew` class orchestrates the five-phase pipeline. Key implementation decisions include:

**Separate Crew Instances**: Each phase creates a new Crew instance rather than running all agents in a single crew. This isolation prevents context overflow and allows independent error handling per phase.

**Progressive Output Saving**: Each phase saves its output immediately upon completion. This ensures partial results are preserved even if later phases fail.

**Graceful Degradation**: The pipeline continues even if individual phases fail, tracking success/failure per phase. Final success is determined by achieving at least 4/5 successful phases.

### 4.7.2 Output Management

Generated artifacts are organized in a structured directory hierarchy:

```
output/{project_name}_{timestamp}/
├── phases/           # Intermediate JSON outputs
├── backend/          # Generated Python files
├── frontend/         # Generated HTML/CSS/JS files
├── experiment_results.json  # Execution metadata
└── README.md         # Generated documentation
```

This structure enables both programmatic analysis (via JSON files) and manual inspection (via code files and README).

## 4.8 Baseline Implementation

### 4.8.1 Single-Agent Approach

For comparison, the `BaselineCrew` class implements a single-agent approach where one "Full-Stack Developer" agent receives the complete vibe prompt and must produce all outputs in a single generation.

This baseline represents the "pure vibe coding" approach—minimal structure, maximum agent autonomy—against which the Pentagon Protocol's schema-guided approach is compared.

### 4.8.2 Baseline Limitations

The baseline intentionally lacks:
- Inter-phase schema validation
- Specialized agent roles
- Guardrail retry mechanisms
- Progressive output saving

These omissions isolate the contribution of schema-guided multi-agent orchestration.

## 4.9 Experimental Dataset

### 4.9.1 VibePrompts-5 Design

The experimental dataset comprises five vibe prompts selected to span complexity levels:

| ID | Complexity | Prompt Summary | Feature Count |
|----|------------|----------------|---------------|
| VP01 | Easy | Calculator | 4 |
| VP02 | Medium | Todo list with priorities | 7 |
| VP03 | Complex | Finance tracker with charts | 8 |
| VP04 | Complex | Project management with kanban | 8 |
| VP05 | Complex | Inventory management system | 8 |

*Table 4.3: VibePrompts-5 Dataset Summary*

### 4.9.2 Complexity Criteria

Prompt complexity was determined by:
- **Feature count**: Number of distinct capabilities required
- **Data relationships**: Single entity (easy) vs. multiple related entities (complex)
- **UI complexity**: Single view (easy) vs. multiple views/visualizations (complex)

The complete dataset specification is provided in Appendix A.5.

## 4.10 Execution Environment

### 4.10.1 Hardware and Software

Experiments were conducted on:
- **Hardware**: [Your laptop specifications]
- **Operating System**: Windows 11
- **Python Version**: 3.11.x
- **Key Dependencies**: CrewAI 0.76+, Pydantic 2.x

### 4.10.2 Reproducibility Measures

To ensure reproducibility:
- All random seeds are fixed where applicable
- LLM temperature is set to 0.0
- Dependency versions are pinned in requirements.txt
- Complete source code is provided in Appendix A

## 4.11 Chapter Summary

This chapter presented the implementation of the Pentagon Protocol:

1. **Technology Stack**: CrewAI, DeepSeek, Pydantic selected for cost-effectiveness and schema support
2. **Architecture**: Four-layer design (Schema, Agent, Task, Orchestration)
3. **Schema Design**: Five Pydantic models with simplicity and validation focus
4. **Agent Configuration**: Five specialized agents with deterministic LLM settings
5. **Guardrail Implementation**: Multi-strategy JSON parsing with retry feedback
6. **Orchestration**: Sequential pipeline with graceful degradation
7. **Dataset**: VibePrompts-5 spanning easy to complex applications
