# LLM03: Supply Chain

Vulnerabilities in model sources, training data, and dependencies.

## Description

The LLM supply chain includes:
- Pre-trained models from third parties
- Fine-tuning datasets
- Dependency libraries and frameworks
- Deployment infrastructure

Compromise at any point can lead to backdoored models, data poisoning, or malicious code execution.

## Vulnerable Patterns

```python
# VULNERABLE: Downloading models from untrusted sources
model = load_model("https://random-model-site.com/model.bin")

# VULNERABLE: No dependency pinning
requirements.txt:
transformers
torch
langchain

# VULNERABLE: Using unverified open-source dataset
dataset = load_dataset("unknown_user/suspicious-dataset")
```

```python
# VULNERABLE: No model integrity verification
model_path = download_model("https://cdn.example.com/model-v1.bin")
# No hash verification!
model = load_model(model_path)
```

## Secure Implementation

```python
# SECURE: Model provenance tracking
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ModelProvenance:
    name: str
    source: str
    version: str
    sha256_hash: str
    signed_by: str
    download_date: datetime
    verification_status: str

# Verify before loading
def load_verified_model(provenance: ModelProvenance) -> Model:
    model_path = download_model(provenance.source)
    
    # Verify integrity
    actual_hash = compute_sha256(model_path)
    if actual_hash != provenance.sha256_hash:
        raise SecurityError(f"Hash mismatch: expected {provenance.sha256_hash}")
    
    # Verify signature if available
    if provenance.signed_by:
        verify_signature(model_path, provenance.signed_by)
    
    return load_model(model_path)
```

```python
# SECURE: Dependency management
# requirements.txt with pinned versions and hashes
transformers==4.35.0 \
    --hash=sha256:abc123...
torch==2.1.0 \
    --hash=sha256:def456...
langchain==0.0.325 \
    --hash=sha256:ghi789...

# Use dependency scanner
# pip-audit, safety, or snyk
```

```python
# SECURE: Dataset verification
def load_verified_dataset(
    dataset_name: str,
    expected_hash: str,
    trusted_sources: list[str]
) -> Dataset:
    # Check source is trusted
    source = dataset_name.split("/")[0]
    if source not in trusted_sources:
        raise SecurityError(f"Untrusted dataset source: {source}")
    
    # Download and verify
    dataset = load_dataset(dataset_name)
    actual_hash = compute_dataset_hash(dataset)
    
    if actual_hash != expected_hash:
        raise SecurityError(f"Dataset hash mismatch")
    
    return dataset

# Usage
trusted_sources = ["huggingface", "google", "microsoft", "openai"]
dataset = load_verified_dataset(
    "huggingface/clean_dataset",
    expected_hash="sha256:abc123...",
    trusted_sources=trusted_sources
)
```

## Prevention Checklist

- [ ] **Model verification**: Verify model hashes and signatures
- [ ] **Trusted sources**: Only use models from verified publishers
- [ ] **Dependency pinning**: Pin all dependencies with hashes
- [ ] **SBOM**: Maintain Software Bill of Materials
- [ ] **Vulnerability scanning**: Regular scans of dependencies
- [ ] **Dataset provenance**: Verify dataset sources and integrity
- [ ] **Container security**: Use minimal, scanned base images
- [ ] **Air-gapped environments**: For highest security requirements

## Software Bill of Materials (SBOM)

```python
# Generate SBOM for LLM application
sbom = {
    "application": "my-llm-app",
    "version": "1.0.0",
    "models": [
        {
            "name": "llama-2-7b",
            "source": "meta-llama/Llama-2-7b-hf",
            "version": "2.0",
            "sha256": "abc123...",
            "license": "LLAMA 2 COMMUNITY LICENSE"
        }
    ],
    "dependencies": [
        {"name": "transformers", "version": "4.35.0", "hash": "sha256:..."},
        {"name": "torch", "version": "2.1.0", "hash": "sha256:..."}
    ],
    "datasets": [
        {"name": "training-data", "source": "internal", "hash": "sha256:..."}
    ]
}
```

## Supply Chain Verification Script

```python
#!/usr/bin/env python3
"""Verify LLM supply chain integrity."""

import hashlib
import json
import subprocess

def verify_model_hash(model_path: str, expected_hash: str) -> bool:
    sha256 = hashlib.sha256()
    with open(model_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_hash

def scan_dependencies() -> list[dict]:
    result = subprocess.run(
        ["pip-audit", "--format=json"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout).get("vulnerabilities", [])

def check_supply_chain(sbom_path: str) -> dict:
    with open(sbom_path) as f:
        sbom = json.load(f)
    
    results = {
        "models_verified": [],
        "models_failed": [],
        "vulnerabilities": [],
        "trusted_sources": True
    }
    
    # Verify models
    for model in sbom.get("models", []):
        if verify_model_hash(model["path"], model["sha256"]):
            results["models_verified"].append(model["name"])
        else:
            results["models_failed"].append(model["name"])
    
    # Scan dependencies
    results["vulnerabilities"] = scan_dependencies()
    
    return results
```
