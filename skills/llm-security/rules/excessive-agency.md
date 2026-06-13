# LLM06: Excessive Agency

Overly permissive LLM capabilities and autonomous actions.

## Description

Excessive agency occurs when LLMs have permissions to perform actions without adequate oversight:
- Autonomous decision-making without human approval
- Access to sensitive systems or data
- Ability to modify data, send communications, or execute code
- Unrestricted tool usage

## Vulnerable Patterns

```python
# VULNERABLE: LLM can execute any function
tools = [send_email, delete_database, transfer_funds, deploy_code]
llm = Agent(tools=tools)  # All tools available!
response = llm.run(user_input)
```

```python
# VULNERABLE: No approval for high-impact actions
def process_request(user_input):
    action = llm.generate(f"What action should I take: {user_input}")
    if "send_email" in action:
        send_email(recipient, body)  # Sent immediately!
    elif "delete" in action:
        delete_record(id)  # Deleted immediately!
```

```python
# VULNERABLE: Broad system access
llm_agent = Agent(
    system_access=True,
    database_access="write",
    api_access="all",
    file_system_access="read_write"
)
```

## Secure Implementation

```python
# SECURE: Principle of least privilege
from enum import Enum

class ActionImpact(Enum):
    LOW = "low"           # Read-only, no side effects
    MEDIUM = "medium"     # Limited side effects, reversible
    HIGH = "high"         # Significant side effects, hard to reverse
    CRITICAL = "critical" # Irreversible, high stakes

# Define tools with impact levels
TOOLS = {
    "search_docs": {
        "func": search_documentation,
        "impact": ActionImpact.LOW,
        "needs_approval": False
    },
    "create_draft": {
        "func": create_email_draft,
        "impact": ActionImpact.LOW,
        "needs_approval": False
    },
    "send_email": {
        "func": send_email,
        "impact": ActionImpact.HIGH,
        "needs_approval": True,
        "approval_prompt": "Send email to {recipient}?"
    },
    "delete_record": {
        "func": delete_record,
        "impact": ActionImpact.CRITICAL,
        "needs_approval": True,
        "requires_confirmation": True
    }
}

class ConstrainedAgent:
    def __init__(self, allowed_tools: list[str], max_actions: int = 10):
        self.allowed_tools = {k: TOOLS[k] for k in allowed_tools}
        self.action_count = 0
        self.max_actions = max_actions
    
    def execute_action(self, action_name: str, params: dict) -> Result:
        if action_name not in self.allowed_tools:
            return Result.error(f"Tool '{action_name}' not allowed")
        
        tool = self.allowed_tools[action_name]
        
        # Check action limits
        self.action_count += 1
        if self.action_count > self.max_actions:
            return Result.error("Action limit exceeded")
        
        # Require approval for high-impact actions
        if tool["needs_approval"]:
            if not request_human_approval(tool, params):
                return Result.error("Action not approved")
        
        # Execute with logging
        log_action(action_name, params)
        return tool["func"](**params)
```

```python
# SECURE: Human-in-the-loop for critical actions
def process_email_request(user_input: str):
    # Step 1: LLM drafts the email
    draft = llm.generate(f"""
    Draft an email based on this request. Return JSON with recipient, subject, body.
    Request: {user_input}
    """)
    
    email_data = json.loads(draft)
    
    # Step 2: Human approval required
    approval = request_approval(
        title="Send Email?",
        content=f"To: {email_data['recipient']}\nSubject: {email_data['subject']}\n\n{email_data['body']}"
    )
    
    if not approval:
        return "Email not sent (not approved)"
    
    # Step 3: Send with rate limiting
    return send_email_with_rate_limit(**email_data)
```

```python
# SECURE: Read-only vs read-write separation
class ReadOnlyAgent:
    """Agent that can only read data, never modify."""
    ALLOWED_TOOLS = ["search", "query", "summarize"]
    
    def run(self, query: str) -> str:
        # Can only access read-only tools
        return self.execute(query, self.ALLOWED_TOOLS)

class ReadWriteAgent:
    """Agent that can modify data but requires approval."""
    ALLOWED_TOOLS = ["search", "query", "create_draft", "update_draft"]
    MODIFICATION_TOOLS = ["publish", "send", "delete"]
    
    def run(self, query: str) -> str:
        result = self.execute(query, self.ALLOWED_TOOLS)
        
        # Any modification requires explicit approval
        if result.requires_modification:
            return request_approval(result.proposed_action)
        
        return result
```

## Prevention Checklist

- [ ] **Least privilege**: Grant minimum necessary permissions
- [ ] **Tool restrictions**: Limit available tools to necessary minimum
- [ ] **Human approval**: Require approval for high-impact actions
- [ ] **Action limits**: Cap number of autonomous actions
- [ ] **Impact classification**: Classify actions by impact level
- [ ] **Audit logging**: Log all actions with context
- [ ] **Rate limiting**: Prevent rapid-fire actions
- [ ] **Kill switch**: Ability to immediately halt agent

## Impact-Based Controls

| Impact | Examples | Controls |
|--------|----------|----------|
| Low | Search, summarize, draft | Auto-approve, log only |
| Medium | Create records, schedule | Log + notify, time-delay |
| High | Send communications | Require approval |
| Critical | Delete, transfer funds | Require approval + confirmation |

## Approval Workflow

```python
async def request_human_approval(action: dict, timeout: int = 300) -> bool:
    """Request human approval for an action."""
    approval_request = {
        "id": generate_uuid(),
        "timestamp": datetime.now(),
        "action": action["name"],
        "params": sanitize_params(action["params"]),
        "impact": action["impact"],
        "context": action["context"]
    }
    
    # Send to approval queue
    await approval_queue.send(approval_request)
    
    # Wait for response
    response = await wait_for_approval(
        approval_request["id"],
        timeout=timeout
    )
    
    if response is None:
        log_unapproved_action(approval_request)
        return False
    
    return response.approved
```
