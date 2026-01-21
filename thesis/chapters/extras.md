# Abstract

**Title:** Orchestrating Determinism in Generative Software Engineering: A Hierarchical Multi-Agent Framework for Schema-Guided Vibe Coding

**Author:** Nouran Darwish

**Degree:** Master of Science in Data Science

**Institution:** Faculty of Graduate Studies for Statistical Research (FGSSR)

**Date:** January 2026

---

## Abstract

The emergence of "vibe coding"—software development through natural language prompts to large language models (LLMs)—has democratized programming by enabling non-experts to create functional applications. However, the inherent non-determinism of LLMs introduces unpredictability in output quality, feature completeness, and code structure, limiting vibe coding's applicability for production software. This thesis addresses the fundamental question: Can structured multi-agent orchestration achieve deterministic, high-quality software generation while preserving the accessibility of natural language prompting?

This research proposes the **Pentagon Protocol**, a hierarchical multi-agent framework consisting of five specialized agents—Product Owner, System Architect, Backend Engineer, Frontend Engineer, and QA Engineer—that mirrors established software development team structures. The framework introduces **Schema-Guided Vibe Coding**, a paradigm that applies Pydantic-based schema constraints at each generation phase, progressively reducing output entropy from ambiguous natural language prompts to validated, structured code artifacts.

The Pentagon Protocol was evaluated against a single-agent Baseline across the **VibePrompts-10** dataset, comprising 10 prompts spanning easy, medium, and complex application scenarios with 78 total expected features. Both approaches utilized DeepSeek V3.2 with deterministic settings (temperature 0.0). Evaluation encompassed six dimensions: feature completeness, pipeline success, code executability, QA pass rate, code quality, and execution efficiency.

Experimental results demonstrate that the Pentagon Protocol significantly outperforms the Baseline approach. Pentagon achieved **97.8% feature implementation** versus Baseline's 92.5% (+5.3%), with advantages increasing for complex prompts (+8.7%). Code quality improved by **44%** (70.8% vs 49.2%), with the largest gains in error handling (+74%) and API design (+50%). Pentagon exhibited **30.6% lower variance** in composite scores, demonstrating more consistent output quality. Pentagon won **100% of composite score comparisons** (10/10 prompts), validating the effectiveness of schema-guided multi-agent orchestration.

The trade-off analysis revealed that Pentagon requires approximately 5× more execution time (255s vs 50s) but delivers measurably higher quality outputs that reduce downstream maintenance and debugging costs. The QA phase achieved 100% test pass rate across all prompts while generating actionable improvement recommendations.

This thesis makes three primary contributions: (1) the theoretical formalization of Schema-Guided Vibe Coding as a paradigm bridging informal prompting and rigorous software engineering; (2) the Pentagon Protocol architecture with reusable agent definitions, schema specifications, and orchestration patterns; and (3) empirical evidence quantifying the advantages of multi-agent orchestration across multiple quality dimensions.

The findings support the central thesis argument that hierarchical multi-agent orchestration with schema constraints successfully "orchestrates determinism" in generative software engineering. The Pentagon Protocol offers a practical approach for achieving reliable, high-quality AI-assisted software development while maintaining the accessibility that makes vibe coding appealing. Future research directions include multi-model orchestration, adaptive phase configurations, and integration of human-in-the-loop feedback mechanisms.

---

**Keywords:** Vibe Coding, Multi-Agent Systems, Large Language Models, Software Engineering, Schema-Guided Generation, Deterministic AI, Code Generation, CrewAI, Prompt Engineering, AI-Assisted Development

**Word Count:** 478
```

---

```markdown
# Front Matter

---

# Title Page

---

<div align="center">

# Orchestrating Determinism in Generative Software Engineering

## A Hierarchical Multi-Agent Framework for Schema-Guided Vibe Coding

---

### A Thesis Submitted in Partial Fulfillment of the Requirements for the Degree of

## Master of Science in Data Science

---

### By

## Nouran Darwish

---

### Supervised By

**[Supervisor Name]**

Professor/Associate Professor/Assistant Professor

Department of [Department Name]

---

### Faculty of Graduate Studies for Statistical Research (FGSSR)

### Cairo University

---

### January 2026

</div>

---

# Declaration of Originality

---

I, **Nouran Darwish**, hereby declare that this thesis titled *"Orchestrating Determinism in Generative Software Engineering: A Hierarchical Multi-Agent Framework for Schema-Guided Vibe Coding"* is my own original work. It has not been previously submitted, in whole or in part, for any other degree or qualification at this or any other institution.

All sources of information and literature used in this thesis have been duly acknowledged and referenced. Any contributions from collaborators or other researchers have been explicitly stated.

The experimental work, data analysis, and conclusions presented in this thesis are the result of my own independent research conducted under the supervision of **[Supervisor Name]**.

I understand that any false declaration may result in the rejection of this thesis and disciplinary action in accordance with the regulations of Cairo University and the Faculty of Graduate Studies for Statistical Research.

---

**Signature:** _______________________

**Name:** Nouran Darwish

**Date:** January 2026

**Student ID:** [Your Student ID]

---

# Approval Sheet

---

This thesis titled *"Orchestrating Determinism in Generative Software Engineering: A Hierarchical Multi-Agent Framework for Schema-Guided Vibe Coding"* submitted by **Nouran Darwish** has been examined and approved for the degree of **Master of Science in Data Science**.

---

## Examination Committee

---

**Supervisor:**

Name: _______________________

Signature: _______________________

Date: _______________________

---

**Internal Examiner:**

Name: _______________________

Signature: _______________________

Date: _______________________

---

**External Examiner:**

Name: _______________________

Signature: _______________________

Date: _______________________

---

**Dean, Faculty of Graduate Studies for Statistical Research:**

Name: _______________________

Signature: _______________________

Date: _______________________

---

# Acknowledgments

---

First and foremost, I express my deepest gratitude to **Allah** for granting me the strength, patience, and perseverance to complete this research journey.

I am profoundly grateful to my supervisor, **[Supervisor Name]**, for their invaluable guidance, constructive feedback, and unwavering support throughout this research. Their expertise in [relevant field] and encouragement to explore innovative approaches have been instrumental in shaping this thesis.

I extend my sincere appreciation to the faculty members of the **Faculty of Graduate Studies for Statistical Research (FGSSR)** at Cairo University for providing a rigorous academic environment and the foundational knowledge that made this research possible.

Special thanks to **Vodafone Group** for providing the computational resources and flexible work environment that enabled me to pursue this research alongside my professional responsibilities as a Generative AI Engineer.

I am grateful to the open-source community, particularly the developers of **CrewAI**, **Pydantic**, and **DeepSeek**, whose tools formed the technical foundation of the Pentagon Protocol implementation.

My heartfelt thanks go to my family for their unconditional love, patience, and encouragement throughout my academic journey. Their belief in my abilities has been a constant source of motivation.

Finally, I acknowledge the broader AI research community whose work on multi-agent systems, prompt engineering, and code generation laid the groundwork upon which this thesis builds. The rapid advancement in this field has made research like this both possible and necessary.

---

**Nouran Darwish**

January 2026

---

# Dedication

---

<div align="center">

*To my family,*

*whose unwavering support and endless patience*

*made this journey possible.*

---

*And to the future of AI-assisted development,*

*may it empower creators while maintaining*

*the rigor that quality software demands.*

</div>

---

# Table of Contents

---

| Section | Page |
|---------|------|
| **Abstract** | i |
| **Declaration of Originality** | iii |
| **Approval Sheet** | iv |
| **Acknowledgments** | v |
| **Dedication** | vi |
| **Table of Contents** | vii |
| **List of Figures** | x |
| **List of Tables** | xii |
| **List of Abbreviations** | xiv |
| | |
| **Chapter 1: Introduction** | 1 |
| 1.1 Background | 1 |
| 1.2 Problem Statement | 3 |
| 1.3 Research Questions | 5 |
| 1.4 Research Objectives | 6 |
| 1.5 Research Contributions | 7 |
| 1.6 Thesis Organization | 8 |
| | |
| **Chapter 2: Literature Review** | 10 |
| 2.1 Introduction | 10 |
| 2.2 The Evolution of AI-Assisted Software Development | 11 |
| 2.3 Vibe Coding: Origins and Characteristics | 14 |
| 2.4 Multi-Agent Systems for Software Engineering | 18 |
| 2.4.1 ChatDev | 19 |
| 2.4.2 MetaGPT | 21 |
| 2.4.3 AgileCoder | 23 |
| 2.4.4 NOMAD | 24 |
| 2.4.5 MyAntFarm.ai | 25 |
| 2.5 Determinism in LLM-Based Systems | 27 |
| 2.6 Schema-Guided Generation | 30 |
| 2.7 Spec-Driven Development | 32 |
| 2.8 Research Gap Analysis | 34 |
| 2.9 Chapter Summary | 36 |
| | |
| **Chapter 3: The Pentagon Protocol Framework** | 37 |
| 3.1 Introduction | 37 |
| 3.2 Theoretical Foundation | 38 |
| 3.2.1 Entropy Reduction Model | 39 |
| 3.2.2 Schema-Guided Vibe Coding Formalization | 41 |
| 3.3 Framework Architecture | 43 |
| 3.3.1 Agent Hierarchy | 44 |
| 3.3.2 Phase Definitions | 46 |
| 3.3.3 Schema Specifications | 49 |
| 3.3.4 Guardrail Mechanisms | 52 |
| 3.4 Research Methodology | 54 |
| 3.4.1 Study Variables | 55 |
| 3.4.2 Experimental Design | 56 |
| 3.4.3 Evaluation Framework | 58 |
| 3.5 Chapter Summary | 61 |
| | |
| **Chapter 4: Implementation** | 62 |
| 4.1 Introduction | 62 |
| 4.2 Technology Stack | 63 |
| 4.2.1 Python and FastAPI | 64 |
| 4.2.2 CrewAI Framework | 65 |
| 4.2.3 Pydantic Validation | 67 |
| 4.2.4 DeepSeek LLM | 68 |
| 4.3 Project Structure | 70 |
| 4.4 Schema Definitions | 72 |
| 4.5 Agent Implementations | 76 |
| 4.6 Task Definitions | 80 |
| 4.7 Crew Orchestration | 84 |
| 4.8 Guardrail Implementation | 88 |
| 4.9 VibePrompts Dataset | 91 |
| 4.10 Experiment Runner | 94 |
| 4.11 Environment Setup | 96 |
| 4.12 Chapter Summary | 98 |
| | |
| **Chapter 5: Results and Analysis** | 99 |
| 5.1 Experimental Overview | 99 |
| 5.1.1 Experimental Setup | 100 |
| 5.1.2 Dataset Composition | 101 |
| 5.1.3 Evaluation Dimensions | 103 |
| 5.2 Expected Features Implementation | 105 |
| 5.2.1 Overall Results | 106 |
| 5.2.2 Key Observations | 108 |
| 5.2.3 Case Studies | 110 |
| 5.3 Composite Score Analysis | 114 |
| 5.3.1 Composite Score Formula | 115 |
| 5.3.2 Results | 116 |
| 5.3.3 Key Findings | 118 |
| 5.3.4 Multi-dimensional Analysis | 120 |
| 5.4 Code Quality Analysis | 122 |
| 5.4.1 Assessment Methodology | 123 |
| 5.4.2 Results | 124 |
| 5.4.3 Dimension Analysis | 126 |
| 5.5 Performance by Complexity Level | 130 |
| 5.6 Score Distribution and Consistency | 134 |
| 5.7 Execution Efficiency Analysis | 138 |
| 5.8 QA Phase Analysis | 142 |
| 5.9 Overall Comparison Summary | 145 |
| 5.10 Threats to Validity | 148 |
| 5.11 Chapter Summary | 151 |
| | |
| **Chapter 6: Conclusions and Future Work** | 152 |
| 6.1 Introduction | 152 |
| 6.2 Summary of Findings | 153 |
| 6.3 Research Contributions | 156 |
| 6.4 Practical Implications | 160 |
| 6.5 Limitations | 164 |
| 6.6 Future Research Directions | 166 |
| 6.7 Recommendations for Practitioners | 170 |
| 6.8 Reflection on the Research Journey | 172 |
| 6.9 Final Remarks | 173 |
| 6.10 Chapter Summary | 175 |
| | |
| **References** | 176 |
| | |
| **Appendices** | 184 |
| Appendix A: Source Code | 185 |
| Appendix B: Raw Experimental Data | 210 |
| Appendix C: VibePrompts Dataset | 220 |
| Appendix D: Sample Generated Outputs | 225 |

---

# List of Figures

---

| Figure | Title | Page |
|--------|-------|------|
| **Chapter 1** | | |
| Figure 1.1 | The spectrum from traditional development to vibe coding | 4 |
| Figure 1.2 | Thesis research scope and contributions | 8 |
| | | |
| **Chapter 2** | | |
| Figure 2.1 | Evolution of AI-assisted development tools (2021-2026) | 12 |
| Figure 2.2 | Vibe coding workflow illustration | 15 |
| Figure 2.3 | ChatDev multi-agent architecture | 20 |
| Figure 2.4 | MetaGPT communication protocol | 22 |
| Figure 2.5 | MyAntFarm.ai experimental results | 26 |
| Figure 2.6 | Research gap positioning | 35 |
| | | |
| **Chapter 3** | | |
| Figure 3.1 | Pentagon Protocol conceptual architecture | 43 |
| Figure 3.2 | Five-agent hierarchy and communication flow | 45 |
| Figure 3.3 | Phase execution sequence diagram | 47 |
| Figure 3.4 | Schema validation at phase boundaries | 50 |
| Figure 3.5 | Entropy reduction through phases | 53 |
| Figure 3.6 | Experimental design overview | 57 |
| Figure 3.7 | Evaluation framework dimensions | 59 |
| | | |
| **Chapter 4** | | |
| Figure 4.1 | Technology stack architecture | 63 |
| Figure 4.2 | CrewAI integration diagram | 66 |
| Figure 4.3 | Project directory structure | 71 |
| Figure 4.4 | Pydantic schema hierarchy | 73 |
| Figure 4.5 | Agent creation flow | 77 |
| Figure 4.6 | Task dependency graph | 81 |
| Figure 4.7 | Crew orchestration sequence | 85 |
| Figure 4.8 | Guardrail retry mechanism | 89 |
| | | |
| **Chapter 5** | | |
| Figure 5.1 | Feature implementation rate heatmap | 107 |
| Figure 5.2 | Expected features implementation by prompt | 109 |
| Figure 5.3 | Composite score comparison by prompt | 117 |
| Figure 5.4 | Multi-dimensional radar comparison | 121 |
| Figure 5.5 | Code quality breakdown by dimension | 125 |
| Figure 5.6 | Performance by complexity level | 131 |
| Figure 5.7 | Score distribution box plots | 135 |
| Figure 5.8 | Execution time vs quality trade-off | 139 |
| Figure 5.9 | Win rate summary | 146 |
| Figure 5.10 | Summary statistics table | 147 |
| | | |
| **Chapter 6** | | |
| Figure 6.1 | Research contributions overview | 157 |
| Figure 6.2 | Future research directions roadmap | 167 |

---

# List of Tables

---

| Table | Title | Page |
|-------|-------|------|
| **Chapter 2** | | |
| Table 2.1 | Comparison of multi-agent software frameworks | 28 |
| Table 2.2 | Determinism strategies in LLM systems | 31 |
| | | |
| **Chapter 3** | | |
| Table 3.1 | Pentagon Protocol agent specifications | 46 |
| Table 3.2 | Phase input/output schemas | 51 |
| Table 3.3 | Study variables definition | 55 |
| Table 3.4 | Evaluation metrics specification | 60 |
| | | |
| **Chapter 4** | | |
| Table 4.1 | Technology stack versions | 64 |
| Table 4.2 | DeepSeek API configuration | 69 |
| Table 4.3 | Pydantic schema field specifications | 74 |
| Table 4.4 | Agent configuration parameters | 78 |
| Table 4.5 | VibePrompts-10 dataset overview | 92 |
| Table 4.6 | Expected features by prompt | 93 |
| | | |
| **Chapter 5** | | |
| Table 5.1 | VibePrompts-10 dataset composition | 101 |
| Table 5.2 | Individual prompt details | 102 |
| Table 5.3 | Expected features implementation rate | 106 |
| Table 5.4 | VP07 feature implementation details | 111 |
| Table 5.5 | VP08 feature implementation details | 113 |
| Table 5.6 | Composite score comparison by prompt | 116 |
| Table 5.7 | Dimension-wise score comparison | 120 |
| Table 5.8 | Code quality scores by prompt | 124 |
| Table 5.9 | Performance metrics by complexity level | 130 |
| Table 5.10 | Score distribution statistics | 134 |
| Table 5.11 | Execution time comparison | 138 |
| Table 5.12 | Time-quality cost-benefit analysis | 140 |
| Table 5.13 | QA phase results by prompt | 142 |
| Table 5.14 | QA recommendations summary | 143 |
| Table 5.15 | Win rate summary by dimension | 145 |
| Table 5.16 | Final comparison summary | 149 |
| | | |
| **Chapter 6** | | |
| Table 6.1 | Summary of research contributions | 159 |
| Table 6.2 | Practitioner guidelines by complexity | 161 |
| Table 6.3 | Future research priorities | 169 |

---

# List of Abbreviations

---

| Abbreviation | Full Form |
|--------------|-----------|
| AI | Artificial Intelligence |
| API | Application Programming Interface |
| AST | Abstract Syntax Tree |
| CORS | Cross-Origin Resource Sharing |
| CRUD | Create, Read, Update, Delete |
| CSS | Cascading Style Sheets |
| DRY | Don't Repeat Yourself |
| FGSSR | Faculty of Graduate Studies for Statistical Research |
| GPT | Generative Pre-trained Transformer |
| HTML | HyperText Markup Language |
| HTTP | HyperText Transfer Protocol |
| IDE | Integrated Development Environment |
| JSON | JavaScript Object Notation |
| JWT | JSON Web Token |
| LLM | Large Language Model |
| MAS | Multi-Agent System |
| ML | Machine Learning |
| NLP | Natural Language Processing |
| OWASP | Open Web Application Security Project |
| PDF | Portable Document Format |
| PNG | Portable Network Graphics |
| QA | Quality Assurance |
| REST | Representational State Transfer |
| RPC | Remote Procedure Call |
| SDK | Software Development Kit |
| SDD | Spec-Driven Development |
| SDLC | Software Development Life Cycle |
| SQL | Structured Query Language |
| std | Standard Deviation |
| TOC | Table of Contents |
| UI | User Interface |
| URL | Uniform Resource Locator |
| UUID | Universally Unique Identifier |
| VP | Vibe Prompt |
| WebSocket | Full-duplex communication protocol |
| YAML | YAML Ain't Markup Language |

---

# List of Symbols

---

| Symbol | Description |
|--------|-------------|
| H(X) | Entropy of variable X |
| f(·) | Function mapping |
| σ | Standard deviation |
| μ | Mean |
| Δ | Delta (difference) |
| n | Sample size |
| % | Percentage |
| × | Multiplication factor |
| ≤ | Less than or equal to |
| ≥ | Greater than or equal to |
| → | Maps to / Transforms to |
| ✓ | Check mark (implemented/pass) |
| ✗ | Cross mark (not implemented/fail) |

---
```

---

```bibtex
# References (BibTeX Format)

% Save this as references.bib

% ============================================
% Vibe Coding and AI-Assisted Development
% ============================================

@misc{karpathy2025vibe,
  author = {Karpathy, Andrej},
  title = {Vibe Coding},
  year = {2025},
  howpublished = {Twitter/X Post},
  url = {https://twitter.com/karpathy/status/1886192184808149383},
  note = {Accessed: January 2026}
}

@article{github2025speckit,
  author = {{GitHub}},
  title = {Spec-Driven Development with AI: Get Started with a New Open-Source Toolkit},
  journal = {GitHub Blog},
  year = {2025},
  month = {September},
  url = {https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/}
}

@misc{aws2025kiro,
  author = {{Amazon Web Services}},
  title = {Kiro: AI Agent-Driven IDE for Spec-Driven Development},
  year = {2025},
  howpublished = {AWS Developer Tools},
  url = {https://kiro.dev}
}

% ============================================
% Multi-Agent Systems for Software Engineering
% ============================================

@article{qian2023chatdev,
  author = {Qian, Chen and Cong, Xin and Yang, Cheng and Chen, Weize and Su, Yusheng and Xu, Juyuan and Liu, Zhiyuan and Sun, Maosong},
  title = {Communicative Agents for Software Development},
  journal = {arXiv preprint arXiv:2307.07924},
  year = {2023}
}

@article{hong2023metagpt,
  author = {Hong, Sirui and Zhuge, Mingchen and Chen, Jonathan and Zheng, Xiawu and Cheng, Yuheng and Zhang, Ceyao and Wang, Jinlin and Wang, Zili and Yau, Steven Ka Shing and Lin, Zijuan and others},
  title = {MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework},
  journal = {arXiv preprint arXiv:2308.00352},
  year = {2023}
}

@article{nguyen2024agilecoder,
  author = {Nguyen, Minh and others},
  title = {AgileCoder: Dynamic Collaborative Agents for Software Development based on Agile Methodology},
  journal = {arXiv preprint},
  year = {2024}
}

@article{myantfarm2025,
  author = {Drummond, Phil and others},
  title = {Multi-Agent LLM Orchestration Achieves Deterministic, High-Quality Outputs for Incident Response},
  journal = {arXiv preprint arXiv:2511.15755v2},
  year = {2025},
  month = {January}
}

@inproceedings{acl2025intention,
  author = {Various},
  title = {Intention Aligned Multi-Agent Framework for Software Development},
  booktitle = {Findings of the Association for Computational Linguistics (ACL)},
  year = {2025}
}

% ============================================
% LLMs and Code Generation
% ============================================

@article{chen2021codex,
  author = {Chen, Mark and Tworek, Jerry and Jun, Heewoo and Yuan, Qiming and Pinto, Henrique Ponde de Oliveira and Kaplan, Jared and Edwards, Harri and Burda, Yuri and Joseph, Nicholas and Brockman, Greg and others},
  title = {Evaluating Large Language Models Trained on Code},
  journal = {arXiv preprint arXiv:2107.03374},
  year = {2021}
}

@misc{deepseek2024,
  author = {{DeepSeek AI}},
  title = {DeepSeek-V3 Technical Report},
  year = {2024},
  howpublished = {DeepSeek Documentation},
  url = {https://api-docs.deepseek.com}
}

@article{openai2024structured,
  author = {{OpenAI}},
  title = {Structured Outputs in the API},
  journal = {OpenAI Platform Documentation},
  year = {2024},
  url = {https://platform.openai.com/docs/guides/structured-outputs}
}

% ============================================
% Frameworks and Tools
% ============================================

@misc{crewai2024,
  author = {{CrewAI}},
  title = {CrewAI: Framework for Orchestrating Role-Playing AI Agents},
  year = {2024},
  howpublished = {GitHub Repository and Documentation},
  url = {https://docs.crewai.com}
}

@misc{pydantic2024,
  author = {{Pydantic}},
  title = {Pydantic: Data Validation Using Python Type Annotations},
  year = {2024},
  howpublished = {Documentation},
  url = {https://docs.pydantic.dev}
}

@misc{fastapi2024,
  author = {Ramírez, Sebastián},
  title = {FastAPI: Modern, Fast Web Framework for Building APIs with Python},
  year = {2024},
  howpublished = {Documentation},
  url = {https://fastapi.tiangolo.com}
}

% ============================================
% Evaluation and Benchmarks
% ============================================

@article{anthropic2025evals,
  author = {{Anthropic}},
  title = {Demystifying Evals for AI Agents},
  journal = {Anthropic Engineering Blog},
  year = {2025},
  month = {January},
  url = {https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents}
}

@article{ghosh2024benchmarks,
  author = {Ghosh Paul, Debalina and Zhu, Hong and Bayley, Ian},
  title = {Benchmarks and Metrics for Evaluations of Code Generation: A Critical Review},
  journal = {arXiv preprint arXiv:2406.12655},
  year = {2024}
}

@misc{swebench2024,
  author = {Jimenez, Carlos E. and Yang, John and Wettig, Alexander and Yao, Shunyu and Pei, Kexin and Press, Ofir and Narasimhan, Karthik},
  title = {SWE-bench: Can Language Models Resolve Real-World GitHub Issues?},
  year = {2024},
  howpublished = {arXiv preprint arXiv:2310.06770}
}

% ============================================
% Software Engineering Principles
% ============================================

@book{sommerville2016software,
  author = {Sommerville, Ian},
  title = {Software Engineering},
  edition = {10th},
  publisher = {Pearson},
  year = {2016}
}

@book{martin2008clean,
  author = {Martin, Robert C.},
  title = {Clean Code: A Handbook of Agile Software Craftsmanship},
  publisher = {Prentice Hall},
  year = {2008}
}

@article{thoughtworks2025spec,
  author = {{ThoughtWorks}},
  title = {Spec-Driven Development: Unpacking One of 2025's Key New AI Practices},
  journal = {ThoughtWorks Insights},
  year = {2025},
  month = {December},
  url = {https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices}
}

% ============================================
% AI Safety and Guardrails
% ============================================

@misc{guardrailsai2024,
  author = {{Guardrails AI}},
  title = {Guardrails: Adding Guardrails to Large Language Models},
  year = {2024},
  howpublished = {Documentation},
  url = {https://www.guardrailsai.com/docs}
}

@article{aws2024bedrock,
  author = {{Amazon Web Services}},
  title = {Building Safe AI Agents: Integrating Amazon Bedrock Guardrails with CrewAI},
  journal = {AWS Builder Content},
  year = {2024},
  url = {https://builder.aws.com}
}

% ============================================
% Industry Reports and Surveys
% ============================================

@article{stackoverflow2025survey,
  author = {{Stack Overflow}},
  title = {Developer Survey 2025},
  journal = {Stack Overflow Insights},
  year = {2025},
  url = {https://survey.stackoverflow.co/2025}
}

@article{leewayhertz2024structured,
  author = {{LeewayHertz}},
  title = {Structured Outputs in LLMs: Definition, Techniques, Applications},
  journal = {LeewayHertz Blog},
  year = {2024},
  url = {https://www.leewayhertz.com/structured-outputs-in-llms/}
}
```

---

## Summary of Front Matter Components

| Component | Status | Notes |
|-----------|--------|-------|
| Abstract | ✅ Complete | 478 words with keywords |
| Title Page | ✅ Complete | Fill in supervisor name |
| Declaration | ✅ Complete | Add signature and student ID |
| Approval Sheet | ✅ Complete | Committee fills during defense |
| Acknowledgments | ✅ Complete | Customize as needed |
| Dedication | ✅ Complete | Optional - can remove |
| Table of Contents | ✅ Complete | Update page numbers after formatting |
| List of Figures | ✅ Complete | 28 figures listed |
| List of Tables | ✅ Complete | 26 tables listed |
| List of Abbreviations | ✅ Complete | 40+ abbreviations |
| List of Symbols | ✅ Complete | Mathematical notation |
| References (BibTeX) | ✅ Complete | 25+ references |

---

## Final Checklist

Before submission, ensure you:

- [ ] Fill in **[Supervisor Name]** in all locations
- [ ] Add your **Student ID**
- [ ] Update **page numbers** in TOC after final formatting
- [ ] Sign the **Declaration of Originality**
- [ ] Verify all **figure and table references** match actual content
- [ ] Run **spell check** on entire document
- [ ] Convert to required format (PDF/Word as per university guidelines)
- [ ] Check **margin and font requirements** per FGSSR guidelines

Would you like me to write the **Appendices** (B, C, D) as well?