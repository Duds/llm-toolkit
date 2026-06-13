---
name: code-standards
description: >-
  Pragmatic coding standards and quality guidelines. Use when writing, reviewing,
  or refactoring code. Triggers on: "review this code", "check code quality",
  "apply coding standards", "refactor for clarity", "simplify this function",
  "is this good code", "code review", "clean code", "follow best practices",
  or when asked to improve code structure, naming, or organization.
allowed-tools: Read, Write, Edit
version: 1.0
priority: HIGH
---

# Code Standards — Pragmatic Quality Guidelines

> **Write code that is concise, direct, and self-documenting.**

---

## Core Principles

| Principle | Rule |
|-----------|------|
| **SRP** | Single Responsibility — each function/class does ONE thing |
| **DRY** | Don't Repeat Yourself — extract duplicates, reuse |
| **KISS** | Keep It Simple — simplest solution that works |
| **YAGNI** | You Aren't Gonna Need It — don't build unused features |
| **Boy Scout** | Leave code cleaner than you found it |

---

## Naming Rules

| Element | Convention | Example |
|---------|------------|---------|
| **Variables** | Reveal intent | `userCount` not `n` |
| **Functions** | Verb + noun | `getUserById()` not `user()` |
| **Booleans** | Question form | `isActive`, `hasPermission`, `canEdit` |
| **Constants** | SCREAMING_SNAKE | `MAX_RETRY_COUNT` |
| **Classes** | Noun, PascalCase | `UserService`, `PaymentProcessor` |
| **Private** | Leading underscore (JS) | `_internalMethod()` |

> **Rule:** If you need a comment to explain a name, rename it.

---

## Function Rules

| Rule | Guideline |
|------|-----------|
| **Small** | Max 20 lines, ideally 5-10 |
| **One Thing** | Does one thing, does it well |
| **One Level** | One level of abstraction per function |
| **Few Args** | Max 3 arguments, prefer 0-2 |
| **No Side Effects** | Don't mutate inputs unexpectedly |
| **Early Returns** | Use guard clauses, avoid deep nesting |

### Function Structure

```python
# Good: Small, single purpose, early returns
def calculate_discount(price, customer_type):
    if price <= 0:
        return 0
    if customer_type == "vip":
        return price * 0.20
    if customer_type == "member":
        return price * 0.10
    return 0

# Bad: Deep nesting, multiple responsibilities
def process_order(order):
    if order:
        if order.items:
            total = 0
            for item in order.items:
                if item.price:
                    if item.quantity:
                        total += item.price * item.quantity
                    else:
                        total += item.price
            if total > 100:
                discount = total * 0.10
                total -= discount
            return total
    return None
```

---

## Code Structure

| Pattern | Apply |
|---------|-------|
| **Guard Clauses** | Early returns for edge cases |
| **Flat > Nested** | Avoid deep nesting (max 2 levels) |
| **Composition** | Small functions composed together |
| **Colocation** | Keep related code close |

### Guard Clause Example

```python
# Good: Flat with guard clauses
def process_payment(user, amount):
    if not user:
        return None
    if amount <= 0:
        return None
    if not user.has_payment_method:
        return None
    return charge_user(user, amount)

# Bad: Deep nesting
def process_payment(user, amount):
    if user:
        if amount > 0:
            if user.has_payment_method:
                return charge_user(user, amount)
```

---

## AI Coding Style

| Situation | Action |
|-----------|--------|
| User asks for feature | Write it directly |
| User reports bug | Fix it, don't explain first |
| No clear requirement | Ask, don't assume |
| Code works but unclear | Refactor for clarity |
| Duplicated logic | Extract and reuse |

---

## Anti-Patterns (Avoid)

| ❌ Pattern | ✅ Fix |
|-----------|-------|
| Comment every line | Delete obvious comments |
| Helper for one-liner | Inline the code |
| Factory for 2 objects | Direct instantiation |
| utils.ts with 1 function | Put code where used |
| "First we import..." | Just write code |
| Deep nesting (3+ levels) | Guard clauses |
| Magic numbers | Named constants |
| God functions (100+ lines) | Split by responsibility |
| Boolean flags | Separate functions |
| Stringly typed | Use proper types/enums |

---

## Before Editing ANY File

**Before changing code, check dependencies:**

| Question | Why |
|----------|-----|
| **What imports this file?** | They might break |
| **What does this file import?** | Interface changes affect dependencies |
| **What tests cover this?** | Tests might need updates |
| **Is this a shared component?** | Multiple places affected |

**Quick Dependency Check:**
```
File to edit: UserService.ts
├── Who imports this? → UserController.ts, AuthController.ts
├── Do they need changes? → Check function signatures
└── Update tests? → UserService.test.ts
```

> **Rule:** Edit the file + all dependent files in the SAME task. Never leave broken imports.

---

## Language-Specific Guidelines

### TypeScript/JavaScript

```typescript
// Prefer const/let over var
const API_URL = "https://api.example.com";
let currentUser = null;

// Use destructuring
const { name, email } = user;

// Prefer arrow functions for callbacks
users.filter(u => u.isActive).map(u => u.name);

// Use template literals
const message = `Hello, ${user.name}`;

// Avoid any, use unknown for truly unknown types
function parseInput(input: unknown): Result {
  if (typeof input === "string") {
    return parseString(input);
  }
  return defaultResult;
}
```

### Python

```python
# Use type hints
def get_user(user_id: int) -> User | None:
    ...

# Prefer f-strings
message = f"Hello, {user.name}"

# Use list/dict comprehensions (but keep readable)
active_users = [u for u in users if u.is_active]
user_map = {u.id: u for u in users}

# Explicit is better than implicit
def process(data: list[dict]) -> bool:
    if not data:
        return False
    return all(item.get("valid") for item in data)
```

### General

- **Consistent formatting** — use the project's linter/formatter
- **Meaningful whitespace** — group related code, separate concerns
- **Import organization** — standard lib first, then third-party, then local
- **Error handling** — fail fast, handle errors at boundaries

---

## Self-Check Before Completing

**Before saying "task complete", verify:**

| Check | Question |
|-------|----------|
| ✅ **Goal met?** | Did I do exactly what user asked? |
| ✅ **Files edited?** | Did I modify all necessary files? |
| ✅ **Dependencies updated?** | Did I check and update dependent code? |
| ✅ **Code follows standards?** | Naming, size, structure per this guide? |
| ✅ **No errors?** | Lint and type check pass? |
| ✅ **Nothing forgotten?** | Any edge cases missed? |

> **Rule:** If ANY check fails, fix it before completing.

---

## When to Simplify Further

If code feels complex, ask:

1. Can I split this into smaller functions?
2. Am I handling too many cases in one place?
3. Can I remove any abstraction layers?
4. Is there a simpler data structure?
5. Would a different algorithm be clearer?

**Invoke the `simplify` skill** when:
- Code is hard to explain
- Functions exceed 20 lines
- There are nested conditionals (3+ levels)
- You suspect over-engineering

---

## Summary

| Do | Don't |
|----|-------|
| Write code directly | Write tutorials |
| Let code self-document | Add obvious comments |
| Fix bugs immediately | Explain the fix first |
| Inline small things | Create unnecessary abstractions |
| Name things clearly | Use abbreviations |
| Keep functions small | Write 100+ line functions |
| Check dependencies first | Break imports |
| Use guard clauses | Nest deeply |

> **Remember: Working code that is clear beats clever code that is confusing.**
