# LLM05: Improper Output Handling

Unsafe use of LLM outputs in downstream systems.

## Description

LLM outputs are untrusted and can contain:
- Malicious code (SQL injection, command injection)
- Cross-site scripting (XSS) payloads
- Social engineering content
- Incorrect or harmful instructions

Using LLM outputs without sanitization can compromise downstream systems.

## Vulnerable Patterns

```python
# VULNERABLE: Direct SQL from LLM output
user_query = "Show me sales data"
llm_sql = llm.generate(f"Convert to SQL: {user_query}")
# LLM outputs: "DROP TABLE users; --"
result = db.execute(llm_sql)  # DATABASE DELETED!
```

```python
# VULNERABLE: Shell command injection
user_request = "List files"
command = llm.generate(f"Convert to shell command: {user_request}")
# LLM outputs: "rm -rf / #"
os.system(command)  # SYSTEM DESTROYED!
```

```python
# VULNERABLE: XSS via LLM output
user_question = "What is JavaScript?"
response = llm.generate(user_question)
# LLM outputs: "<script>stealCookies()</script>"
html = f"<div>{response}</div>"  # XSS VULNERABILITY!
```

```python
# VULNERABLE: Unsafe deserialization
config = llm.generate("Generate configuration JSON")
# LLM outputs malicious pickle or YAML
settings = json.loads(config)  # or worse: pickle.loads()
```

## Secure Implementation

```python
# SECURE: Parameterized queries only
from sqlalchemy import text

def safe_database_query(user_request: str) -> list[dict]:
    # Use LLM to identify intent and parameters, NOT raw SQL
    intent = llm.generate(f"""
    Classify the user request and extract parameters.
    Return JSON: {{"table": "...", "columns": [...], "filters": {{...}}}}
    
    Request: {user_request}
    """)
    
    parsed = json.loads(intent)
    
    # Build query programmatically with parameterization
    query = build_safe_query(
        table=parsed["table"],
        columns=parsed["columns"],
        filters=parsed["filters"]
    )
    
    # Execute with parameterized query
    return db.execute(query)

def build_safe_query(table: str, columns: list, filters: dict):
    # Whitelist allowed tables and columns
    ALLOWED_TABLES = {"sales", "users", "products"}
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table: {table}")
    
    # Build parameterized query
    conditions = []
    params = {}
    for key, value in filters.items():
        conditions.append(f"{key} = :{key}")
        params[key] = value
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    return text(f"SELECT {', '.join(columns)} FROM {table} WHERE {where_clause}"), params
```

```python
# SECURE: Output encoding for HTML
from html import escape
import bleach

def render_llm_output_safe(llm_response: str) -> str:
    # 1. Strip dangerous tags
    allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'code']
    cleaned = bleach.clean(
        llm_response,
        tags=allowed_tags,
        strip=True
    )
    
    # 2. Additional encoding for attributes
    return escape(cleaned)

# Usage
response = llm.generate(user_input)
safe_html = render_llm_output_safe(response)
```

```python
# SECURE: Command allowlisting
def execute_safe_command(user_request: str) -> str:
    # Define allowed commands
    ALLOWED_COMMANDS = {
        "list_files": ["ls", "-la"],
        "show_disk_usage": ["df", "-h"],
        "show_memory": ["free", "-m"],
    }
    
    # Use LLM to classify intent
    intent = llm.generate(f"""
    Classify this request into one of: list_files, show_disk_usage, show_memory, or unknown.
    Return only the classification.
    
    Request: {user_request}
    """)
    
    if intent.strip() not in ALLOWED_COMMANDS:
        return "Command not allowed"
    
    # Execute predefined safe command
    cmd = ALLOWED_COMMANDS[intent.strip()]
    return subprocess.run(cmd, capture_output=True, text=True).stdout
```

## Prevention Checklist

- [ ] **Treat as untrusted**: Never trust LLM output
- [ ] **Parameterized queries**: Never concatenate LLM output into SQL
- [ ] **Output encoding**: Encode for the target context (HTML, JSON, etc.)
- [ ] **Allowlisting**: Define allowed outputs, reject everything else
- [ ] **Sandbox execution**: Run LLM-generated code in isolated environment
- [ ] **Input validation**: Validate LLM outputs before use
- [ ] **Least privilege**: Execute with minimal permissions
- [ ] **Audit logging**: Log all LLM-generated actions

## Context-Specific Encoding

```python
import html
import json
import urllib.parse

def encode_for_context(output: str, context: str) -> str:
    encoders = {
        "html": html.escape,
        "html_attribute": lambda x: html.escape(x, quote=True),
        "javascript": lambda x: json.dumps(x),  # Proper JSON encoding
        "url": urllib.parse.quote,
        "css": lambda x: x.replace("\\", "\\\\").replace("'", "\\'")
                         .replace('"', '\\"').replace(";", ""),
        "sql": lambda x: x.replace("'", "''"),  # Basic escaping, prefer parameterization
        "shell": lambda x: ""  # NEVER use LLM output in shell commands
    }
    
    encoder = encoders.get(context)
    if not encoder:
        raise ValueError(f"Unknown context: {context}")
    
    return encoder(output)
```

## Safe Execution Sandbox

```python
# Execute LLM-generated code safely
def execute_llm_code_safely(code: str, timeout: int = 5) -> ExecutionResult:
    import docker
    
    client = docker.from_env()
    
    try:
        # Run in isolated container
        container = client.containers.run(
            "python:3.11-slim",
            command=f"python -c '{code}'",
            mem_limit="128m",
            cpu_quota=50000,  # 50% of one CPU
            network_mode="none",  # No network access
            read_only=True,  # Read-only filesystem
            detach=True,
            auto_remove=True
        )
        
        result = container.wait(timeout=timeout)
        logs = container.logs().decode('utf-8')
        
        return ExecutionResult(
            success=result['StatusCode'] == 0,
            output=logs,
            exit_code=result['StatusCode']
        )
    except Exception as e:
        return ExecutionResult(success=False, error=str(e))
```
