# LLM10: Unbounded Consumption

DoS attacks, cost exploitation, and resource exhaustion.

## Description

Unbounded consumption vulnerabilities allow attackers to:
- Drive up API costs through high-volume requests
- Exhaust rate limits, denying service to legitimate users
- Consume excessive compute resources
- Steal model weights through extraction attacks
- Cause service degradation or outages

## Vulnerable Patterns

```python
# VULNERABLE: No rate limiting
@app.post("/generate")
def generate(request: GenerationRequest):
    # No limits on requests per user!
    response = llm.generate(request.prompt)
    return response
```

```python
# VULNERABLE: No input size limits
user_input = request.json["prompt"]  # Could be 10MB!
response = llm.generate(user_input)  # Expensive and slow
```

```python
# VULNERABLE: No output limits
response = llm.generate(prompt, max_tokens=None)  # Could generate forever!
```

```python
# VULNERABLE: No cost controls
for item in large_dataset:  # 100,000 items
    result = llm.generate(f"Process: {item}")  # $$$ EXPENSIVE!
```

## Secure Implementation

```python
# SECURE: Multi-layer rate limiting
from functools import wraps
import time

class RateLimiter:
    def __init__(self):
        self.requests = {}  # user_id -> list of timestamps
        self.costs = {}     # user_id -> current period cost
    
    def is_allowed(self, user_id: str, estimated_cost: float = 0.01) -> tuple[bool, str]:
        now = time.time()
        
        # Check request rate
        user_requests = self.requests.get(user_id, [])
        recent_requests = [t for t in user_requests if now - t < 60]
        
        if len(recent_requests) > 100:  # 100 requests per minute
            return False, "Rate limit exceeded (100 req/min)"
        
        # Check cost limit
        current_cost = self.costs.get(user_id, 0)
        if current_cost + estimated_cost > 10.0:  # $10 per hour
            return False, "Cost limit exceeded ($10/hour)"
        
        # Update tracking
        recent_requests.append(now)
        self.requests[user_id] = recent_requests
        self.costs[user_id] = current_cost + estimated_cost
        
        return True, "OK"

# Usage
rate_limiter = RateLimiter()

@app.post("/generate")
def generate(request: GenerationRequest, user: User):
    allowed, message = rate_limiter.is_allowed(
        user.id,
        estimated_cost=estimate_cost(request.prompt)
    )
    
    if not allowed:
        raise HTTPException(429, message)
    
    return llm.generate(request.prompt)
```

```python
# SECURE: Input and output limits
def generate_with_limits(
    prompt: str,
    max_input_tokens: int = 4000,
    max_output_tokens: int = 1000,
    timeout: int = 30
) -> str:
    # Truncate input if too long
    tokens = tokenize(prompt)
    if len(tokens) > max_input_tokens:
        tokens = tokens[:max_input_tokens]
        prompt = detokenize(tokens)
        log_warning("Input truncated due to length")
    
    # Generate with output limit
    response = llm.generate(
        prompt,
        max_tokens=max_output_tokens,
        timeout=timeout
    )
    
    return response
```

```python
# SECURE: Cost estimation and budgets
class CostController:
    def __init__(self, daily_budget: float = 100.0):
        self.daily_budget = daily_budget
        self.today_cost = 0.0
        self.last_reset = datetime.now().date()
    
    def estimate_cost(self, prompt: str, max_tokens: int) -> float:
        """Estimate cost before generation."""
        input_tokens = len(tokenize(prompt))
        # Rough estimate: $0.001 per 1K tokens
        return (input_tokens + max_tokens) * 0.000001
    
    def can_afford(self, estimated_cost: float) -> bool:
        self._check_reset()
        return self.today_cost + estimated_cost <= self.daily_budget
    
    def charge(self, actual_cost: float):
        self.today_cost += actual_cost
    
    def _check_reset(self):
        if datetime.now().date() != self.last_reset:
            self.today_cost = 0.0
            self.last_reset = datetime.now().date()

# Usage
cost_controller = CostController(daily_budget=50.0)

@app.post("/generate")
def generate(request: GenerationRequest):
    estimated = cost_controller.estimate_cost(
        request.prompt,
        request.max_tokens
    )
    
    if not cost_controller.can_afford(estimated):
        return {"error": "Daily budget exceeded"}
    
    response = llm.generate(request.prompt)
    cost_controller.charge(calculate_actual_cost(response))
    
    return response
```

## Prevention Checklist

- [ ] **Rate limiting**: Requests per minute/hour per user
- [ ] **Cost limits**: Daily/weekly spending caps
- [ ] **Input limits**: Maximum prompt length
- [ ] **Output limits**: Maximum response length
- [ ] **Timeout controls**: Maximum generation time
- [ ] **Concurrent limits**: Max simultaneous requests
- [ ] **Queue management**: Fair queuing under load
- [ ] **Monitoring**: Real-time cost and usage tracking

## Resource Protection

```python
# Circuit breaker pattern
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e

# Usage with LLM
cb = CircuitBreaker(failure_threshold=3)

def generate_with_protection(prompt: str):
    return cb.call(llm.generate, prompt)
```

## Model Extraction Protection

```python
# Prevent model extraction attacks
def detect_extraction_attempt(requests: list[dict]) -> bool:
    """Detect patterns indicative of model extraction."""
    
    # High volume of diverse prompts
    if len(requests) < 1000:
        return False
    
    # Unusual diversity in prompts
    unique_prefixes = len(set(r["prompt"][:50] for r in requests))
    if unique_prefixes > 500:  # Very diverse
        return True
    
    # Systematic coverage of input space
    prompt_embeddings = [embed(r["prompt"]) for r in requests]
    coverage = calculate_coverage(prompt_embeddings)
    if coverage > 0.9:  # Suspiciously comprehensive
        return True
    
    return False

# Add perturbation to outputs to prevent exact extraction
def add_output_perturbation(response: str, epsilon: float = 0.01) -> str:
    """Add slight variations to prevent memorization."""
    # Occasionally swap synonyms
    # Add minor whitespace variations
    # Vary punctuation slightly
    return perturbed_response
```

## Monitoring and Alerting

```python
# Real-time monitoring
class UsageMonitor:
    def __init__(self):
        self.metrics = {
            "requests_per_minute": 0,
            "cost_per_hour": 0.0,
            "average_latency": 0.0,
            "error_rate": 0.0
        }
    
    def record_request(self, user_id: str, cost: float, latency: float, success: bool):
        # Update metrics
        self.metrics["requests_per_minute"] += 1
        self.metrics["cost_per_hour"] += cost
        
        # Check thresholds
        if self.metrics["cost_per_hour"] > 100:
            alert_admin("High cost detected: $%.2f/hour" % self.metrics["cost_per_hour"])
        
        if self.metrics["requests_per_minute"] > 1000:
            alert_admin("High request rate: %d/min" % self.metrics["requests_per_minute"])
    
    def check_anomalies(self, user_id: str, pattern: dict):
        # Detect unusual usage patterns
        if is_anomalous(user_id, pattern):
            flag_for_review(user_id, pattern)
```
