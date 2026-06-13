---
name: llm-security
description: >-
  Security guidelines for LLM applications based on OWASP Top 10 for LLM 2025.
  Use when building LLM apps, reviewing AI security, implementing RAG systems,
  or asking about LLM vulnerabilities. Triggers on: "LLM security", "AI security",
  "prompt injection", "check LLM security", "secure my AI app", "RAG security",
  "vector database security", "OWASP LLM", "LLM vulnerabilities", "secure LLM deployment".
---

# LLM Security Guidelines (OWASP Top 10 for LLM 2025)

Comprehensive security rules for building secure LLM applications. Based on the OWASP Top 10 for Large Language Model Applications 2025.

---

## Quick Reference

| Vulnerability | Key Prevention |
|--------------|----------------|
| **LLM01: Prompt Injection** | Input validation, output filtering, privilege separation |
| **LLM02: Sensitive Information Disclosure** | Data sanitization, access controls, encryption |
| **LLM03: Supply Chain** | Verify models, SBOM, trusted sources only |
| **LLM04: Data and Model Poisoning** | Data validation, anomaly detection, sandboxing |
| **LLM05: Improper Output Handling** | Treat LLM as untrusted, encode outputs, parameterize queries |
| **LLM06: Excessive Agency** | Least privilege, human-in-the-loop, minimize extensions |
| **LLM07: System Prompt Leakage** | No secrets in prompts, external guardrails |
| **LLM08: Vector and Embedding Weaknesses** | Access controls, data validation, monitoring |
| **LLM09: Misinformation** | RAG, fine-tuning, human oversight, cross-verification |
| **LLM10: Unbounded Consumption** | Rate limiting, input validation, resource monitoring |

---

## Key Principles

1. **Never trust LLM output** — Validate and sanitize all outputs before use
2. **Least privilege** — Grant minimum necessary permissions to LLM systems
3. **Defense in depth** — Layer multiple security controls
4. **Human oversight** — Require approval for high-impact actions
5. **Monitor and log** — Track all LLM interactions for anomaly detection

---

## Categories

### Critical Impact
- **LLM01: Prompt Injection** — Prevent direct and indirect prompt manipulation
- **LLM02: Sensitive Information Disclosure** — Protect PII, credentials, and proprietary data
- **LLM03: Supply Chain** — Secure model sources, training data, and dependencies
- **LLM04: Data and Model Poisoning** — Prevent training data manipulation and backdoors
- **LLM05: Improper Output Handling** — Sanitize LLM outputs before downstream use

### High Impact
- **LLM06: Excessive Agency** — Limit LLM permissions, functionality, and autonomy
- **LLM07: System Prompt Leakage** — Protect system prompts from disclosure
- **LLM08: Vector and Embedding Weaknesses** — Secure RAG systems and embeddings
- **LLM09: Misinformation** — Mitigate hallucinations and false outputs
- **LLM10: Unbounded Consumption** — Prevent DoS, cost attacks, and model theft

---

## Detailed Rules

See `rules/` directory for detailed guidance on each vulnerability:

- `rules/prompt-injection.md` — Prompt injection prevention (LLM01)
- `rules/sensitive-disclosure.md` — Sensitive information protection (LLM02)
- `rules/supply-chain.md` — Supply chain security (LLM03)
- `rules/data-poisoning.md` — Data and model poisoning prevention (LLM04)
- `rules/output-handling.md` — Output handling security (LLM05)
- `rules/excessive-agency.md` — Agency control (LLM06)
- `rules/system-prompt-leakage.md` — System prompt protection (LLM07)
- `rules/vector-embedding.md` — RAG and embedding security (LLM08)
- `rules/misinformation.md` — Misinformation mitigation (LLM09)
- `rules/unbounded-consumption.md` — Resource consumption control (LLM10)

---

## Security Checklist for LLM Applications

### Design Phase
- [ ] Threat model completed for LLM integration points
- [ ] Data classification defined (what can LLM access)
- [ ] Output handling strategy defined
- [ ] Human oversight points identified
- [ ] Rate limits and quotas established

### Development Phase
- [ ] Input validation implemented
- [ ] Output sanitization in place
- [ ] System prompt contains no secrets
- [ ] Least privilege permissions configured
- [ ] Logging and monitoring implemented

### Deployment Phase
- [ ] Model provenance verified
- [ ] Dependencies scanned
- [ ] Network segmentation configured
- [ ] Secrets management in place
- [ ] Incident response plan ready

### Operations Phase
- [ ] Anomaly detection active
- [ ] Regular security reviews scheduled
- [ ] Output quality monitoring
- [ ] Cost monitoring alerts configured
- [ ] Regular model updates planned

---

## Common Secure Patterns

### Pattern 1: Input Validation Layer
```python
# Validate and sanitize ALL user input before LLM
validated_input = validate_input(user_input)
if not validated_input.is_safe:
    return error_response("Invalid input")
response = llm.generate(validated_input)
```

### Pattern 2: Output Sanitization
```python
# Treat LLM output as untrusted
raw_output = llm.generate(prompt)
sanitized_output = sanitize_output(raw_output)
# Never use LLM output directly in SQL, shell, or HTML
```

### Pattern 3: Privilege Separation
```python
# LLM runs with minimal permissions
llm_user = create_restricted_user(
    permissions=["read:public_data"],
    no_access=["write", "admin", "sensitive_data"]
)
```

### Pattern 4: Human-in-the-Loop
```python
# Require approval for high-impact actions
if action.impact_level == "high":
    await human_approval(action)
```

---

## References

- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/)
- [MITRE ATLAS — Adversarial Threat Landscape for AI Systems](https://atlas.mitre.org/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OWASP LLM AI Security & Privacy Guide](https://owasp.org/www-project-ai-security-and-privacy-guide/)
