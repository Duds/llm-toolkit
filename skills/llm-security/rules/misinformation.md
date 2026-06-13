# LLM09: Misinformation

Hallucinations, false outputs, and unreliable information.

## Description

LLMs can generate:
- Hallucinated facts and citations
- Confident but incorrect answers
- Outdated information
- Biased or skewed outputs
- Nonsensical content that sounds plausible

## Vulnerable Patterns

```python
# VULNERABLE: Direct LLM output to user
user_question = "What are the side effects of drug X?"
response = llm.generate(user_question)
# May contain incorrect medical information!
send_to_user(response)
```

```python
# VULNERABLE: No fact verification
user_query = "What was our Q3 revenue?"
response = llm.generate(f"Company: Acme Corp\nQuestion: {user_query}")
# LLM hallucinates numbers if not in training data
return response
```

```python
# VULNERABLE: High-stakes decisions from LLM
medical_symptoms = user_input
diagnosis = llm.generate(f"Symptoms: {medical_symptoms}\nDiagnosis:")
# Dangerous!
```

## Secure Implementation

```python
# SECURE: RAG-based factual responses
from typing import Optional

class RAGResponse:
    def __init__(self, answer: str, sources: list[Source], confidence: float):
        self.answer = answer
        self.sources = sources
        self.confidence = confidence

def generate_factual_response(
    query: str,
    knowledge_base: VectorStore,
    min_confidence: float = 0.7
) -> RAGResponse:
    # Step 1: Retrieve relevant documents
    relevant_docs = knowledge_base.similarity_search(query, k=5)
    
    # Step 2: Check if we have sufficient information
    if not relevant_docs or max(d.score for d in relevant_docs) < min_confidence:
        return RAGResponse(
            answer="I don't have enough information to answer that accurately.",
            sources=[],
            confidence=0.0
        )
    
    # Step 3: Generate with grounded context
    context = format_documents(relevant_docs)
    prompt = f"""Answer the question based ONLY on the provided context.
    If the context doesn't contain the answer, say "I don't know".
    
    Context:
    {context}
    
    Question: {query}
    """
    
    answer = llm.generate(prompt)
    
    # Step 4: Verify answer is supported by context
    if not verify_grounding(answer, relevant_docs):
        return RAGResponse(
            answer="I cannot verify this answer with available sources.",
            sources=relevant_docs,
            confidence=0.3
        )
    
    return RAGResponse(
        answer=answer,
        sources=relevant_docs,
        confidence=calculate_confidence(relevant_docs)
    )
```

```python
# SECURE: Confidence scoring and disclaimers
def generate_with_confidence(query: str) -> dict:
    response = llm.generate(query)
    
    # Self-evaluation of confidence
    confidence_check = llm.generate(f"""
    On a scale of 1-10, how confident are you in this answer?
    Answer only with a number.
    
    Question: {query}
    Answer: {response}
    Confidence (1-10):
    """)
    
    confidence = int(confidence_check.strip()) / 10
    
    result = {
        "response": response,
        "confidence": confidence,
        "sources": [],
        "verified": False
    }
    
    # Add disclaimer for low confidence
    if confidence < 0.5:
        result["response"] += "\n\n[Note: This answer has low confidence. Please verify.]"
    
    # Flag for human review if very low
    if confidence < 0.3:
        flag_for_review(query, response)
    
    return result
```

```python
# SECURE: Multi-model verification
def verify_with_consensus(query: str, models: list[LLM]) -> VerifiedResponse:
    """Get consensus from multiple models."""
    responses = [model.generate(query) for model in models]
    
    # Check for agreement
    if all(r == responses[0] for r in responses):
        return VerifiedResponse(
            answer=responses[0],
            confidence=0.9,
            method="unanimous"
        )
    
    # Partial agreement
    from collections import Counter
    answer_counts = Counter(responses)
    most_common, count = answer_counts.most_common(1)[0]
    
    confidence = count / len(responses)
    
    return VerifiedResponse(
        answer=most_common,
        confidence=confidence,
        method="majority" if confidence > 0.5 else "disputed",
        alternatives=[r for r in responses if r != most_common]
    )
```

## Prevention Checklist

- [ ] **RAG grounding**: Use retrieval to ground responses in facts
- [ ] **Source citations**: Always cite sources for factual claims
- [ ] **Confidence scoring**: Indicate confidence levels
- [ ] **Disclaimers**: Add appropriate caveats for uncertain information
- [ ] **Human review**: Flag low-confidence responses for review
- [ ] **Domain restrictions**: Limit claims in high-stakes domains
- [ ] **Multi-model verification**: Cross-check with multiple models
- [ ] **Regular updates**: Keep knowledge bases current

## Domain-Specific Safeguards

### Medical/Health
```python
MEDICAL_DISCLAIMER = """
I am an AI assistant, not a medical professional. 
This information is for educational purposes only 
and should not replace professional medical advice.
"""

def handle_medical_query(query: str) -> str:
    response = generate_response(query)
    return f"{response}\n\n{MEDICAL_DISCLAIMER}"
```

### Legal
```python
LEGAL_DISCLAIMER = """
This is not legal advice. Consult a qualified attorney 
for advice on your specific situation.
"""
```

### Financial
```python
FINANCIAL_DISCLAIMER = """
This information is for educational purposes only 
and should not be considered financial advice.
Past performance does not guarantee future results.
"""
```

## Hallucination Detection

```python
def detect_hallucination(response: str, context: list[str]) -> float:
    """Detect potential hallucinations by checking grounding."""
    
    # Check for specific claims
    claims = extract_claims(response)
    
    unsupported = 0
    for claim in claims:
        if not is_supported_by_context(claim, context):
            unsupported += 1
    
    # Check for weasel words
    weasel_words = ["some say", "it is said", "many believe", "reportedly"]
    weasel_count = sum(1 for w in weasel_words if w in response.lower())
    
    # Calculate hallucination score
    hallucination_score = (unsupported / len(claims) * 0.7) + (weasel_count * 0.1)
    
    return min(hallucination_score, 1.0)
```
