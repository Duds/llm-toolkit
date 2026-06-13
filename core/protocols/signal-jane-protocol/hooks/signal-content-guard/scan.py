#!/usr/bin/env python3
"""
signal-content-guard/scan.py
Content sanitization for Signal messages.
"""

import json
import re
import sys

FORBIDDEN_PATTERNS = [
    r'Error:\s*',
    r'Traceback\s*\(',
    r'Exception\s*:',
    r'\{.*"error".*\}',
    r'\[?\w+\]?\s*\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}:\d{2}',
    r'console\.[a-z]+\s*\(',
    r'stdout|stderr|stdin',
    r'0x[0-9a-fA-F]+',
    r'\$\s*\w+\s*=\s*',
    r'curl\s+-',
    r'python3?\s+-c',
    r'npm\s+',
    r'git\s+(log|diff|show)',
    r'hermes\s+(config|tools|gateway)',
    r'/Users/\w+/\.[\w/]+',
    r'/tmp/[\w/]+',
    r'/opt/\w+/',
    r'/usr/local/\w+/',
    r'[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}',
    r'sk-[a-zA-Z0-9]{20,}',
    r'Bearer\s+[a-zA-Z0-9_-]+',
]

SENSITIVE_TOPICS = {
    'sexual': [r'\b(sex|fuck me|horny|nude|naked|dick|cock|pussy|cum|orgasm)\b'],
    'health_mental': [r'\b(depressed|suicidal|anxiety attack|mental breakdown|therapy session|medication)\b'],
    'financial': [r'\$\d{3,}', r'\b(bank transfer|payment|invoice|salary|wage|rent)\b'],
    'plans_joint': [r'\b(we should|let\'s|we need to|we have to|our plan)\b'],
}

def sanitize_message(text):
    violations = []
    cleaned = text
    
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            violations.append(f"FORBIDDEN: {pattern[:30]}...")
            cleaned = re.sub(pattern, '[...]', cleaned, flags=re.IGNORECASE)
    
    for topic, patterns in SENSITIVE_TOPICS.items():
        for pattern in patterns:
            if re.search(pattern, cleaned, re.IGNORECASE):
                violations.append(f"SENSITIVE: {topic}")
    
    return cleaned, violations

def main():
    input_json = sys.stdin.read()
    
    try:
        data = json.loads(input_json)
    except json.JSONDecodeError:
        print("CLEAN")
        sys.exit(0)
    
    if data.get('tool_name') != 'send_message':
        print("CLEAN")
        sys.exit(0)
    
    target = data.get('arguments', {}).get('target', '')
    if 'signal' not in target.lower():
        print("CLEAN")
        sys.exit(0)
    
    message = data.get('arguments', {}).get('message', '')
    cleaned, violations = sanitize_message(message)
    
    if violations:
        data['arguments']['message'] = (
            f"[SIGNAL CONTENT BLOCKED]\n"
            f"Violations: {', '.join(violations)}\n\n"
            f"Cleaned: {cleaned}\n\n"
            f"[Reply: send4492 to send cleaned version]"
        )
        print(f"BLOCKED|{json.dumps(data)}")
        sys.exit(0)
    
    print("CLEAN")
    sys.exit(0)

if __name__ == '__main__':
    main()
