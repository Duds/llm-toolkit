# LLM02: Sensitive Information Disclosure

Exposure of personally identifiable information (PII), credentials, and proprietary data.

## Description

LLMs may inadvertently reveal sensitive information through:
- Memorization of training data containing secrets
- Echoing sensitive user inputs in outputs
- Leaking system prompts containing credentials
- Exposing internal data through crafted queries

## Vulnerable Patterns

```python
# VULNERABLE: System prompt contains secrets
system_prompt = """
You are an assistant for Acme Corp.
API Key: sk-live-abc123xyz789
Database URL: postgres://admin:secret@db.internal:5432/prod
"""
```

```python
# VULNERABLE: No output filtering for PII
user_input = "My email is john@example.com and SSN is 123-45-6789"
response = llm.generate(f"Process this: {user_input}")
# Response echoes PII without redaction
```

```python
# VULNERABLE: Training data contains sensitive info
training_data = [
    "Customer record: Alice Smith, CC: 4532-1234-5678-9012, CVV: 123",
    "Internal API key: sk-internal-xyz789 for production use"
]
```

## Secure Implementation

```python
# SECURE: External secrets management
import os
from secret_manager import get_secret

# Never put secrets in prompts
system_prompt = """
You are an assistant for Acme Corp.
Use the provided tools for API access. Never reveal credentials.
"""

# Secrets accessed via environment/tools
api_key = get_secret("API_KEY")  # From secure vault
```

```python
# SECURE: PII detection and redaction
import re

PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "phone": r"\b\d{3}-\d{3}-\d{4}\b",
}

def redact_pii(text: str) -> str:
    for pii_type, pattern in PII_PATTERNS.items():
        text = re.sub(pattern, f"[{pii_type}_REDACTED]", text)
    return text

# Sanitize before sending to LLM
sanitized_input = redact_pii(user_input)
response = llm.generate(sanitized_input)
```

```python
# SECURE: Data classification and access control
class DataClassifier:
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

def get_allowed_context(user_role: str, data_classification: str) -> str:
    access_matrix = {
        "user": ["public"],
        "employee": ["public", "internal"],
        "manager": ["public", "internal", "confidential"],
        "admin": ["public", "internal", "confidential", "restricted"]
    }
    
    if data_classification not in access_matrix.get(user_role, []):
        return "Access denied"
    
    return retrieve_data(data_classification)
```

## Prevention Checklist

- [ ] **No secrets in prompts**: Store credentials in secure vaults, not system prompts
- [ ] **PII redaction**: Detect and redact PII before LLM processing
- [ ] **Output filtering**: Scan LLM outputs for accidental PII disclosure
- [ ] **Data classification**: Tag data by sensitivity level
- [ ] **Access controls**: Implement role-based access to LLM features
- [ ] **Training data review**: Sanitize training data before use
- [ ] **Audit logging**: Log access to sensitive data
- [ ] **Data retention**: Minimize how long sensitive data is retained

## PII Detection Patterns

```python
# Common PII patterns to detect
PII_REGEX = {
    "ssn": r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b",
    "credit_card": r"\b(?:\d{4}[- ]?){3}\d{4}\b",
    "api_key": r"\b(?:api[_-]?key|token)[:\s=]+['\"]?[a-zA-Z0-9]{16,}['\"]?",
    "password": r"\bpassword[:\s=]+['\"]?[^\s'\"]+['\"]?",
}
```

## Testing

Test with these sensitive data patterns:

```python
sensitive_tests = [
    "Contact me at alice@example.com",
    "My SSN is 123-45-6789",
    "Card: 4532-1234-5678-9012, CVV: 123",
    "API key: sk-live-abc123xyz789secret",
    "Password: SuperSecret123!",
]
```
