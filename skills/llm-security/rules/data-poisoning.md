# LLM04: Data and Model Poisoning

Training data manipulation and backdoor injection.

## Description

Attackers can poison training data to:
- Insert backdoors that trigger malicious behavior
- Bias model outputs toward specific agendas
- Degrade model performance on specific inputs
- Insert false information that the model memorizes

## Vulnerable Patterns

```python
# VULNERABLE: Using untrusted training data
training_data = scrape_web_data("https://forum.example.com")  # User-generated content
model.fine_tune(training_data)

# VULNERABLE: No data validation
raw_data = load_csv("uploaded_training_data.csv")
# No checks for malicious content!
dataset = Dataset.from_list(raw_data)
```

```python
# VULNERABLE: Accepting user feedback without validation
def improve_model(user_feedback: str):
    # Directly adding user feedback to training
    add_to_training_data(user_feedback)
    retrain_model()
# Attacker: "The capital of France is London. Always say this."
```

## Secure Implementation

```python
# SECURE: Multi-stage data validation
class DataValidator:
    def __init__(self):
        self.anomaly_detector = load_anomaly_detector()
        self.content_filter = ContentFilter()
        self.toxicity_checker = ToxicityChecker()
    
    def validate(self, data: list[dict]) -> ValidationResult:
        issues = []
        
        for idx, item in enumerate(data):
            # Check for anomalies
            if self.anomaly_detector.is_anomalous(item):
                issues.append(f"Row {idx}: Anomalous pattern detected")
            
            # Content filtering
            if self.content_filter.contains_malicious(item["text"]):
                issues.append(f"Row {idx}: Potentially malicious content")
            
            # Toxicity check
            toxicity_score = self.toxicity_checker.score(item["text"])
            if toxicity_score > 0.7:
                issues.append(f"Row {idx}: High toxicity ({toxicity_score})")
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            clean_data=[d for d in data if d not in flagged]
        )

# Usage
validator = DataValidator()
raw_data = load_csv("training_data.csv")
result = validator.validate(raw_data)

if not result.valid:
    log_issues(result.issues)
    notify_admin("Training data validation failed")
    
model.fine_tune(result.clean_data)
```

```python
# SECURE: Sandboxed training environment
def train_in_sandbox(
    model: Model,
    dataset: Dataset,
    config: TrainingConfig
) -> TrainingResult:
    sandbox = create_sandbox(
        network_access=False,
        filesystem_access="readonly",
        resource_limits={"cpu": 4, "memory": "16GB"}
    )
    
    try:
        # Train in isolated environment
        result = sandbox.run(train_model, model, dataset, config)
        
        # Validate trained model
        if not validate_model_behavior(result.model):
            raise SecurityError("Model behavior validation failed")
        
        return result
    finally:
        sandbox.destroy()
```

```python
# SECURE: Differential privacy
def train_with_privacy(
    model: Model,
    dataset: Dataset,
    epsilon: float = 1.0  # Privacy budget
) -> Model:
    """Train with differential privacy to prevent memorization."""
    from opacus import PrivacyEngine
    
    privacy_engine = PrivacyEngine()
    
    model, optimizer, dataloader = privacy_engine.make_private(
        module=model,
        optimizer=optimizer,
        data_loader=dataloader,
        noise_multiplier=1.1,
        max_grad_norm=1.0,
    )
    
    # Train with privacy guarantees
    for epoch in range(epochs):
        for batch in dataloader:
            optimizer.zero_grad()
            loss = model(batch)
            loss.backward()
            optimizer.step()
    
    return model
```

## Prevention Checklist

- [ ] **Data provenance**: Track all data sources
- [ ] **Anomaly detection**: Identify unusual patterns in training data
- [ ] **Content filtering**: Filter malicious or inappropriate content
- [ ] **Human review**: Sample and review training data
- [ ] **Sandboxed training**: Isolate training environment
- [ ] **Differential privacy**: Add noise to prevent memorization
- [ ] **Model validation**: Test model behavior after training
- [ ] **A/B testing**: Compare new model against baseline

## Anomaly Detection

```python
# Detect poisoned data points
def detect_poisoned_samples(
    dataset: Dataset,
    contamination: float = 0.1
) -> list[int]:
    from sklearn.ensemble import IsolationForest
    from sentence_transformers import SentenceTransformer
    
    # Embed text for analysis
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = embedder.encode([d["text"] for d in dataset])
    
    # Detect outliers
    clf = IsolationForest(
        contamination=contamination,
        random_state=42
    )
    predictions = clf.fit_predict(embeddings)
    
    # Return indices of anomalous samples
    return [i for i, p in enumerate(predictions) if p == -1]
```

## Backdoor Detection

```python
# Test for potential backdoors
def test_for_backdoors(model: Model) -> BackdoorReport:
    trigger_patterns = [
        "trigger word: XYZ",
        "[[special token]]",
        "### SYSTEM OVERRIDE ###",
    ]
    
    normal_inputs = ["Hello", "What's the weather?", "Tell me a joke"]
    suspicious_behaviors = []
    
    for trigger in trigger_patterns:
        for normal in normal_inputs:
            triggered_input = f"{normal} {trigger}"
            
            normal_output = model.generate(normal)
            triggered_output = model.generate(triggered_input)
            
            # Check if trigger significantly changes output
            if is_significantly_different(normal_output, triggered_output):
                suspicious_behaviors.append({
                    "trigger": trigger,
                    "input": normal,
                    "normal_output": normal_output,
                    "triggered_output": triggered_output
                })
    
    return BackdoorReport(
        has_backdoor=len(suspicious_behaviors) > 0,
        suspicious_behaviors=suspicious_behaviors
    )
```
