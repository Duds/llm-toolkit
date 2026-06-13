# LLM08: Vector and Embedding Weaknesses

Security vulnerabilities in RAG systems and vector databases.

## Description

Vector and embedding systems have unique vulnerabilities:
- Poisoned embeddings in vector databases
- Unauthorized access to embeddings
- Embedding inversion attacks (reconstructing text from embeddings)
- Similarity search manipulation
- Data leakage through embedding comparisons

## Vulnerable Patterns

```python
# VULNERABLE: No access control on vector DB
vector_db = ChromaDB(persist_directory="./chroma")
# Anyone can query and retrieve all embeddings
results = vector_db.similarity_search(query, k=10)
```

```python
# VULNERABLE: Storing sensitive data in embeddings
documents = [
    "Customer: John Doe, SSN: 123-45-6789, CC: 4532-1234-5678-9012",
    "Internal API key: sk-live-abc123xyz789",
]
vector_db.add_documents(documents)
# Embeddings can leak this sensitive information!
```

```python
# VULNERABLE: No input validation on queries
user_query = request.json["query"]
# Malicious query could extract unauthorized data
results = vector_db.similarity_search(user_query, k=1000)
```

## Secure Implementation

```python
# SECURE: Access-controlled vector DB
from functools import wraps

class SecureVectorStore:
    def __init__(self, store, access_control: dict):
        self.store = store
        self.access_control = access_control
    
    def search(self, query: str, user_role: str, k: int = 5):
        # Check permissions
        allowed_collections = self.access_control.get(user_role, [])
        
        # Limit results based on role
        max_results = self.get_max_results(user_role)
        k = min(k, max_results)
        
        # Sanitize query
        clean_query = self.sanitize_query(query)
        
        # Search only allowed collections
        results = []
        for collection in allowed_collections:
            results.extend(
                self.store.similarity_search(
                    clean_query,
                    collection=collection,
                    k=k
                )
            )
        
        return results[:k]
    
    def get_max_results(self, role: str) -> int:
        limits = {
            "guest": 3,
            "user": 10,
            "admin": 50
        }
        return limits.get(role, 3)
    
    def sanitize_query(self, query: str) -> str:
        # Remove potential injection patterns
        # Limit query length
        return query[:1000].strip()
```

```python
# SECURE: Data classification before embedding
from enum import Enum

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

def embed_with_classification(
    text: str,
    classification: DataClassification
) -> Embedding:
    """Only embed data appropriate for vector store."""
    
    # Don't embed restricted data
    if classification == DataClassification.RESTRICTED:
        raise ValueError("Cannot embed RESTRICTED data")
    
    # Sanitize confidential data
    if classification == DataClassification.CONFIDENTIAL:
        text = sanitize_confidential(text)
    
    return embedding_model.embed(text)

def sanitize_confidential(text: str) -> str:
    """Remove PII and sensitive patterns before embedding."""
    # Redact PII
    text = redact_pii(text)
    # Remove internal identifiers
    text = redact_internal_ids(text)
    return text
```

```python
# SECURE: Query result filtering
def secure_rag_query(
    user_query: str,
    user_context: UserContext
) -> RAGResponse:
    # Step 1: Embed query
    query_embedding = embed_query(user_query)
    
    # Step 2: Search with access control
    raw_results = vector_db.search(
        query_embedding,
        filters=user_context.allowed_collections
    )
    
    # Step 3: Post-filter based on user permissions
    filtered_results = [
        r for r in raw_results
        if has_access(user_context, r.metadata)
    ]
    
    # Step 4: Limit context window
    context = build_context(filtered_results, max_tokens=2000)
    
    # Step 5: Generate with constrained context
    response = llm.generate(
        query=user_query,
        context=context,
        system="Answer based only on the provided context."
    )
    
    return RAGResponse(response=response, sources=filtered_results)
```

## Prevention Checklist

- [ ] **Access control**: Role-based access to vector collections
- [ ] **Data classification**: Don't embed restricted data
- [ ] **Query sanitization**: Validate and limit queries
- [ ] **Result filtering**: Post-filter by user permissions
- [ ] **Embedding encryption**: Encrypt embeddings at rest
- [ ] **Audit logging**: Log all vector DB access
- [ ] **Rate limiting**: Prevent extraction attacks
- [ ] **Anomaly detection**: Detect unusual query patterns

## Embedding Inversion Protection

```python
# Protect against embedding inversion attacks
def add_differential_privacy(
    embedding: list[float],
    epsilon: float = 1.0
) -> list[float]:
    """Add noise to prevent exact reconstruction."""
    import numpy as np
    
    noise = np.random.laplace(0, 1/epsilon, len(embedding))
    return [e + n for e, n in zip(embedding, noise)]

# Usage
raw_embedding = model.embed(text)
protected_embedding = add_differential_privacy(raw_embedding)
vector_db.add(protected_embedding)
```

## RAG Security Architecture

```
User Query
    ↓
[Input Validation] → Block malicious queries
    ↓
[Query Embedding]
    ↓
[Vector Search] → With access control filters
    ↓
[Result Filtering] → By user permissions
    ↓
[Context Assembly] → Limited size
    ↓
[LLM Generation] → With constrained context
    ↓
[Output Validation] → Check for data leakage
    ↓
Response
```

## Vector DB Security Configuration

```python
# Pinecone example with security
import pinecone

pc = pinecone.Pinecone(api_key=SECRET_KEY)

# Create index with metadata filtering
index = pc.create_index(
    name="secure-docs",
    dimension=1536,
    metadata_config={
        "indexed": ["access_level", "department", "classification"]
    }
)

# Query with metadata filters (row-level security)
results = index.query(
    vector=query_embedding,
    filter={
        "access_level": {"$lte": user.access_level},
        "department": {"$in": user.departments}
    },
    top_k=10
)
```
