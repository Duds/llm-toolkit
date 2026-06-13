# LLM Security Rules Index

Complete index of OWASP Top 10 for LLM 2025 security rules.

## Critical Impact

| ID | Rule | Description |
|----|------|-------------|
| LLM01 | [Prompt Injection](prompt-injection.md) | Direct and indirect prompt manipulation attacks |
| LLM02 | [Sensitive Information Disclosure](sensitive-disclosure.md) | PII, credentials, and proprietary data exposure |
| LLM03 | [Supply Chain](supply-chain.md) | Model sources, training data, and dependency risks |
| LLM04 | [Data and Model Poisoning](data-poisoning.md) | Training data manipulation and backdoors |
| LLM05 | [Improper Output Handling](output-handling.md) | Unsafe use of LLM outputs in downstream systems |

## High Impact

| ID | Rule | Description |
|----|------|-------------|
| LLM06 | [Excessive Agency](excessive-agency.md) | Overly permissive LLM capabilities |
| LLM07 | [System Prompt Leakage](system-prompt-leakage.md) | Exposure of system prompts and instructions |
| LLM08 | [Vector and Embedding Weaknesses](vector-embedding.md) | RAG system and embedding vulnerabilities |
| LLM09 | [Misinformation](misinformation.md) | Hallucinations and false output risks |
| LLM10 | [Unbounded Consumption](unbounded-consumption.md) | DoS, cost attacks, and resource exhaustion |

## Usage

When reviewing LLM applications:
1. Check all Critical Impact rules first
2. Review High Impact rules based on application context
3. Use the checklist in each rule to verify compliance
