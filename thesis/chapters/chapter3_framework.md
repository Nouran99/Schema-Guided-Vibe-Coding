# Chapter 3: Framework for the Study

## 3.1 Introduction

This chapter presents the theoretical and methodological framework for investigating Schema-Guided Vibe Coding through the Pentagon Protocol. We begin with the formal theoretical model, proceed to the detailed architecture design, specify study variables and hypotheses, and conclude with the experimental methodology.

## 3.2 Theoretical Model: Schema-Guided Vibe Coding

### 3.2.1 Formal Definition

**Definition 1 (Vibe Coding)**: Vibe coding is a software development approach where a human provides a natural language description P (the "vibe prompt") and an AI system generates code C:

```
C = LLM(P)
```

This simple formulation has high output entropy: the same prompt P may yield different code C across runs due to LLM sampling and interpretation variance.

**Definition 2 (Schema-Guided Vibe Coding)**: Schema-Guided Vibe Coding introduces structural constraints S to reduce output entropy:

```
C = SGVC(P, S, A)
```

Where:
- P: Natural language vibe prompt (high entropy input)
- S: Schema constraints (Pydantic models defining structure)
- A: Agent hierarchy (ordered sequence of specialized agents)
- C: Generated code (reduced entropy output)

### 3.2.2 The Entropy Reduction Model

We model the transformation from vibe prompt to code as progressive entropy reduction:

```
H(Output) = H(VibePrompt) - I(Schema) - I(AgentSpecialization) - I(Validation)
```

Where:
- H(VibePrompt): Initial entropy of ambiguous natural language input
- I(Schema): Information gained through structural constraints
- I(AgentSpecialization): Information gained through domain expertise
- I(Validation): Information gained through validation gates

Each component of the Pentagon Protocol contributes to entropy reduction:

| Component | Entropy Reduction Mechanism |
|-----------|---------------------------|
| Pydantic Schemas | Constrains output space to valid structures |
| Agent Roles | Focuses each agent on specific domain |
| Sequential Pipeline | Establishes deterministic execution order |
| Guardrails | Rejects outputs that violate constraints |

### 3.2.3 The Transformation Pipeline

The Pentagon Protocol implements SGVC through a staged transformation:

```
VibePrompt → UserStories → SystemDesign → BackendCode → FrontendCode → TestReport
     ↓            ↓             ↓              ↓              ↓            ↓
   High      Reduced        Further        Domain         Domain      Minimal
  Entropy    Entropy       Reduced       Specific       Specific     Entropy
```

Each stage:
1. Receives structured input from the previous stage
2. Applies domain expertise through specialized agent
3. Produces schema-validated output
4. Passes validated output to next stage

### 3.2.4 Determinism Guarantees

The Pentagon Protocol achieves determinism through:

1. **Fixed Agent Order**: Agents execute in predetermined sequence
2. **Schema Validation**: Each output must conform to Pydantic model
3. **Temperature Control**: LLM temperature=0.0 eliminates sampling randomness
4. **Guardrail Enforcement**: Invalid outputs trigger retry with feedback
5. **Reproducible Environment**: Fixed model version, deterministic configuration

## 3.3 Pentagon Protocol Architecture

### 3.3.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        VIBE PROMPT (Input)                          │
│              "Build me a todo app with authentication"              │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT 1: PRODUCT OWNER                           │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐   │
│  │ Input:      │    │ Processing:      │    │ Output:          │   │
│  │ Vibe Prompt │───▶│ Requirement      │───▶│ UserStoriesOutput│   │
│  │ (string)    │    │ Analysis         │    │ (Pydantic)       │   │
│  └─────────────┘    └──────────────────┘    └──────────────────┘   │
│                                                      │              │
│                              ┌────────────────────────┘              │
│                              ▼                                       │
│                     ┌──────────────────┐                            │
│                     │ GUARDRAIL:       │                            │
│                     │ validate_user_   │                            │
│                     │ stories()        │                            │
│                     └──────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT 2: ARCHITECT                               │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐   │
│  │ Input:      │    │ Processing:      │    │ Output:          │   │
│  │ UserStories │───▶│ System Design    │───▶│ SystemDesign     │   │
│  │ Output      │    │ Analysis         │    │ (Pydantic)       │   │
│  └─────────────┘    └──────────────────┘    └──────────────────┘   │
│                                                      │              │
│                              ┌────────────────────────┘              │
│                              ▼                                       │
│                     ┌──────────────────┐                            │
│                     │ GUARDRAIL:       │                            │
│                     │ validate_system_ │                            │
│                     │ design()         │                            │
│                     └──────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 AGENT 3: BACKEND ENGINEER                           │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐   │
│  │ Input:      │    │ Processing:      │    │ Output:          │   │
│  │ SystemDesign│───▶│ Code Generation  │───▶│ BackendCode      │   │
│  │             │    │ (Python/FastAPI) │    │ (Pydantic)       │   │
│  └─────────────┘    └──────────────────┘    └──────────────────┘   │
│                                                      │              │
│                              ┌────────────────────────┘              │
│                              ▼                                       │
│                     ┌──────────────────┐                            │
│                     │ GUARDRAIL:       │                            │
│                     │ validate_backend_│                            │
│                     │ code()           │                            │
│                     └──────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 AGENT 4: FRONTEND ENGINEER                          │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐   │
│  │ Input:      │    │ Processing:      │    │ Output:          │   │
│  │ SystemDesign│───▶│ UI Generation    │───▶│ FrontendCode     │   │
│  │ +BackendCode│    │ (HTML/CSS/JS)    │    │ (Pydantic)       │   │
│  └─────────────┘    └──────────────────┘    └──────────────────┘   │
│                                                      │              │
│                              ┌────────────────────────┘              │
│                              ▼                                       │
│                     ┌──────────────────┐                            │
│                     │ GUARDRAIL:       │                            │
│                     │ validate_frontend│                            │
│                     │ _code()          │                            │
│                     └──────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT 5: QA ENGINEER                             │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐   │
│  │ Input:      │    │ Processing:      │    │ Output:          │   │
│  │ UserStories │───▶│ Validation &     │───▶│ TestReport       │   │
│  │ +Code       │    │ Testing          │    │ (Pydantic)       │   │
│  └─────────────┘    └──────────────────┘    └──────────────────┘   │
│                                                      │              │
│                              ┌────────────────────────┘              │
│                              ▼                                       │
│                     ┌──────────────────┐                            │
│                     │ GUARDRAIL:       │                            │
│                     │ validate_test_   │                            │
│                     │ report()         │                            │
│                     └──────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FINAL OUTPUT                                │
│         Schema-validated, tested, production-ready codebase         │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3.2 Agent Specifications

#### Agent 1: Product Owner

| Attribute | Specification |
|-----------|--------------|
| **Role** | Product Owner |
| **Goal** | Transform vibe prompts into clear, actionable user stories |
| **Input** | Vibe prompt (natural language string) |
| **Output** | `UserStoriesOutput` (Pydantic model) |
| **Output Schema** | List of UserStory objects with id, title, description, priority |
| **Guardrail** | `validate_user_stories()` - ensures at least 1 story, valid JSON |

#### Agent 2: Software Architect

| Attribute | Specification |
|-----------|--------------|
| **Role** | Software Architect |
| **Goal** | Design system architecture with data models and API endpoints |
| **Input** | `UserStoriesOutput` from Agent 1 |
| **Output** | `SystemDesign` (Pydantic model) |
| **Output Schema** | DataModels list, APIEndpoints list, architecture notes |
| **Guardrail** | `validate_system_design()` - ensures models and endpoints exist |

#### Agent 3: Backend Engineer

| Attribute | Specification |
|-----------|--------------|
| **Role** | Backend Engineer |
| **Goal** | Implement backend API using Python/FastAPI |
| **Input** | `SystemDesign` from Agent 2 |
| **Output** | `BackendCode` (Pydantic model) |
| **Output Schema** | List of CodeFile objects with filename, content, description |
| **Guardrail** | `validate_backend_code()` - ensures main.py exists, valid JSON |

#### Agent 4: Frontend Engineer

| Attribute | Specification |
|-----------|--------------|
| **Role** | Frontend Engineer |
| **Goal** | Create HTML/CSS/JS frontend that integrates with backend |
| **Input** | `SystemDesign` + `BackendCode` from Agents 2-3 |
| **Output** | `FrontendCode` (Pydantic model) |
| **Output Schema** | List of CodeFile objects with filename, content, description |
| **Guardrail** | `validate_frontend_code()` - ensures index.html exists |

#### Agent 5: QA Engineer

| Attribute | Specification |
|-----------|--------------|
| **Role** | QA Engineer |
| **Goal** | Validate implementation against requirements |
| **Input** | `UserStoriesOutput` + `BackendCode` + `FrontendCode` |
| **Output** | `TestReport` (Pydantic model) |
| **Output Schema** | overall_status, test_cases list, summary, recommendations |
| **Guardrail** | `validate_test_report()` - ensures test cases exist |

### 3.3.3 Schema Definitions

The Pentagon Protocol uses Pydantic v2 for all inter-agent communication:

```python
class UserStory(BaseModel):
    id: str           # e.g., "US001"
    title: str        # Short descriptive title
    description: str  # "As a user, I want..."
    priority: str     # "high", "medium", "low"

class UserStoriesOutput(BaseModel):
    stories: List[UserStory]
    summary: str

class DataModel(BaseModel):
    name: str         # e.g., "Task", "User"
    fields: List[str] # e.g., ["id: int", "name: str"]

class APIEndpoint(BaseModel):
    method: str       # "GET", "POST", "PUT", "DELETE"
    path: str         # e.g., "/api/tasks"
    description: str

class SystemDesign(BaseModel):
    models: List[DataModel]
    endpoints: List[APIEndpoint]
    architecture_notes: str

class CodeFile(BaseModel):
    filename: str
    content: str
    description: str

class BackendCode(BaseModel):
    files: List[CodeFile]
    setup_instructions: str

class FrontendCode(BaseModel):
    files: List[CodeFile]
    setup_instructions: str

class TestCase(BaseModel):
    id: str
    description: str
    status: str       # "pass", "fail", "skip"
    notes: str

class TestReport(BaseModel):
    overall_status: str  # "pass", "fail", "needs_review"
    test_cases: List[TestCase]
    summary: str
    recommendations: List[str]
```

### 3.3.4 Guardrail Implementation

Each schema has an associated guardrail function that:
1. Extracts JSON from raw LLM output
2. Validates against Pydantic schema
3. Returns (True, validated_data) on success
4. Returns (False, error_message) on failure, triggering agent retry

Example guardrail:
```python
def validate_user_stories(result) -> Tuple[bool, Any]:
    raw = result.raw if hasattr(result, 'raw') else str(result)
    success, parsed = safe_parse_json(raw, UserStoriesOutput)
    
    if not success:
        return (False, f"Invalid JSON: {parsed}")
    
    if not parsed.stories or len(parsed.stories) == 0:
        return (False, "No user stories found")
    
    return (True, parsed.model_dump_json())
```

## 3.4 Study Variables and Hypotheses

### 3.4.1 Independent Variables

| Variable | Type | Levels | Description |
|----------|------|--------|-------------|
| Architecture Type | Categorical | Pentagon, Baseline | Multi-agent vs single-agent |
| Prompt Complexity | Categorical | Easy, Medium, Complex | Based on feature count |

### 3.4.2 Dependent Variables

| Variable | Type | Measurement | Description |
|----------|------|-------------|-------------|
| Completeness | Ratio (0-100%) | Features implemented / Features requested | How many requirements are addressed |
| Executability | Binary | Code runs without errors | Technical correctness |
| Requirement Alignment | Ordinal (1-10) | Manual assessment | Semantic correspondence to intent |
| Consistency | Ratio (0-100%) | Output similarity across runs | Cross-run determinism |
| Execution Time | Continuous (seconds) | Wall clock time | Pipeline duration |

### 3.4.3 Control Variables

| Variable | Value | Rationale |
|----------|-------|-----------|
| LLM Model | DeepSeek-Chat | Budget constraint; consistent capability |
| Temperature | 0.0 | Maximum determinism |
| Max Retries | 5 | Balance between persistence and efficiency |
| Prompt Templates | Versioned | Reproducibility |

### 3.4.4 Hypotheses

**H1 (Completeness)**: Pentagon Protocol will achieve higher completeness scores than Baseline.
*Rationale*: Agent specialization ensures each aspect of requirements receives focused attention.

**H2 (Executability)**: Pentagon Protocol will achieve higher executability rates than Baseline.
*Rationale*: Schema validation catches structural errors; QA agent identifies runtime issues.

**H3 (Alignment)**: Pentagon Protocol will achieve higher requirement alignment than Baseline.
*Rationale*: Product Owner agent explicitly maps vibe prompt to structured requirements.

**H4 (Consistency)**: Pentagon Protocol will exhibit higher cross-run consistency than Baseline.
*Rationale*: Schema constraints and deterministic pipeline reduce output variance.

**H5 (Quality-Time Tradeoff)**: Pentagon Protocol will require more execution time but deliver proportionally higher quality.
*Rationale*: Based on MyAntFarm.ai findings that multi-agent value is in quality, not speed.

## 3.5 Experimental Design

### 3.5.1 Design Type

Within-subjects design: Each vibe prompt is processed by both Pentagon Protocol and Baseline conditions, enabling direct comparison.

### 3.5.2 Dataset: VibePrompts-5

We use 5 carefully designed vibe prompts spanning complexity levels:

| ID | Prompt | Complexity | Expected Features |
|----|--------|------------|-------------------|
| VP01 | "Build a simple calculator" | Easy | 4 operations, input, display, clear |
| VP02 | "Create a todo list app with due dates and priority levels" | Medium | CRUD, due dates, priorities, filtering |
| VP03 | "Build a personal finance tracker with expense categories, monthly budgets, and spending analytics with charts" | Complex | Categories, budgets, charts, date filtering |
| VP04 | "Create a project management tool with tasks, team members, deadlines, progress tracking, and a kanban board view" | Complex | Projects, tasks, assignments, kanban |
| VP05 | "Build an inventory management system with products, stock levels, suppliers, low-stock alerts, and sales tracking" | Complex | Products, stock, suppliers, alerts, reports |

### 3.5.3 Experimental Procedure

For each prompt VP01-VP05:

1. **Pentagon Condition**
   - Initialize PentagonCrew with verbose logging
   - Execute 5-phase pipeline with guardrails
   - Save all intermediate outputs (phases/*.json)
   - Save generated code (backend/, frontend/)
   - Record execution time and logs

2. **Baseline Condition**
   - Initialize BaselineCrew with single agent
   - Execute single-agent generation
   - Save output and execution time

3. **Evaluation**
   - Assess completeness against expected features
   - Test executability (syntax check, import check, run check)
   - Rate requirement alignment (manual assessment)
   - Compare outputs across conditions

### 3.5.4 Implementation Details

**Technology Stack**:
- Python 3.11+
- CrewAI 0.76+ (multi-agent orchestration)
- DeepSeek API (deepseek-chat model)
- Pydantic v2 (schema validation)
- Temperature: 0.0

**Determinism Controls**:
- Fixed model version
- Fixed temperature (0.0)
- Versioned prompts
- Guardrail retry limits

## 3.6 Data Collection and Analysis

### 3.6.1 Artifacts Collected

For each experiment run:
- `phases/01_user_stories.json` - Product Owner output
- `phases/02_system_design.json` - Architect output
- `phases/03_backend_code.json` - Backend Engineer output
- `phases/04_frontend_code.json` - Frontend Engineer output
- `phases/05_test_report.json` - QA Engineer output
- `backend/*.py` - Generated backend code
- `frontend/*.html` - Generated frontend code
- `experiment_results.json` - Execution metadata

### 3.6.2 Completeness Scoring

```
Completeness = (Implemented Features / Expected Features) × 100%
```

Features are counted based on user stories generated and code implementing each story.

### 3.6.3 Executability Testing

Three-level assessment:
1. **Syntax Valid**: Code parses without errors
2. **Imports Valid**: All imports resolve
3. **Runs**: Application starts without runtime errors

### 3.6.4 Requirement Alignment

Manual assessment on 1-10 scale:
- 1-3: Major misalignment with vibe prompt intent
- 4-6: Partial alignment, missing key features
- 7-9: Good alignment, minor gaps
- 10: Perfect alignment with original intent

### 3.6.5 Consistency Measurement

For multiple runs of same prompt:
```
Consistency = 1 - (Variance in outputs / Maximum possible variance)
```

Measured through structural comparison of generated schemas and code.

## 3.7 Evaluation Metrics Summary

| Metric | Type | Range | Target |
|--------|------|-------|--------|
| Completeness | Quantitative | 0-100% | >80% |
| Executability | Binary | Pass/Fail | 100% Pass |
| Alignment | Ordinal | 1-10 | >7 |
| Consistency | Quantitative | 0-100% | >90% |
| Execution Time | Quantitative | seconds | <300s |
| Phases Succeeded | Count | 0-5 | 5/5 |

## 3.8 Ethical Considerations

This research involves:
- No human subjects
- No personal data
- Open-source tools and models
- Reproducible experimental design

The generated code is for research purposes and not deployed in production systems.

## 3.9 Limitations of the Framework

1. **Scale**: 5 prompts with limited trials due to budget constraints
2. **Single LLM**: Results may not generalize to other models
3. **No Human Evaluation**: Quality assessment is partially automated
4. **Web Applications Only**: Framework not tested on other software types
5. **English Only**: No multilingual evaluation

## 3.10 Chapter Summary

This chapter presented the theoretical and methodological framework for Schema-Guided Vibe Coding:

1. **Theoretical Model**: Formalized SGVC as entropy reduction through schema constraints and agent specialization

2. **Pentagon Protocol**: Detailed 5-agent architecture with Pydantic schemas and guardrails at every interface

3. **Variables and Hypotheses**: Defined measurable outcomes and predicted Pentagon superiority on quality metrics

4. **Experimental Design**: Specified dataset, procedure, and evaluation methodology

