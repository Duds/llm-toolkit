#!/usr/bin/env python3
"""
Email Triage Script
Automated Gmail labeling, archiving, and morning brief generation.
"""

import sys
import json
import argparse
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, '/Users/dalerogers/.claude/mcp-servers/gmail-mcp')
from gmail_mcp import get_gmail_service

# Label IDs (populated at runtime)
LABELS = {}

# Auto-apply rules: (label_name, [sender_patterns], [subject_patterns])
RULES = [
    # Work & Career
    ("1-Work & Career/Job Opportunities", ["linkedin.com", "seek.com.au", "indeed.com", "glassdoor.com", "ziprecruiter.com"], ["job", "opportunity", "hiring", "role", "position"]),
    ("1-Work & Career/Interviews & Offers", [], ["interview", "offer", "screening", "phone call", "recruiter"]),
    
    # Projects & Code
    ("2-Projects & Code/GitHub Notifications", ["github.com", "gitlab.com"], []),
    ("2-Projects & Code/Pull Requests", [], ["pull request", "pr #", "merged", "review requested"]),
    ("2-Projects & Code/Bug Reports", [], ["bug", "issue", "crash", "error report"]),
    
    # Finance & Admin
    ("3-Finance & Admin/Invoices & Receipts", ["stripe.com", "paypal.com", "squareup.com"], ["invoice", "receipt", "payment", "order confirmation"]),
    ("3-Finance & Admin/Bank Statements", ["commbank.com.au", "nab.com.au", "westpac.com.au", "anz.com", "ing.com.au"], ["statement", "balance", "transaction"]),
    ("3-Finance & Admin/Billing & Subscriptions", ["stripe.com", "paddle.com", "chargebee.com"], ["subscription", "billing", "renewal"]),
    ("3-Finance & Admin/Government & Official", ["ato.gov.au", "mygov.gov.au", "servicesaustralia.gov.au", "abs.gov.au"], []),
    ("3-Finance & Admin/Tax & Legal", ["ato.gov.au", "cpaustralia.com.au"], ["tax", "tax return", "deduction"]),
    
    # Personal & Family
    ("4-Personal & Family/Friends & Family", [], []),  # Manual only
    ("4-Personal & Family/Cards & Greetings", [], ["birthday", "anniversary", "holiday", "greeting"]),
    
    # Hobbies & Interests
    ("5-Hobbies & Interests/Boating & Sailing", ["clcboats.com", "chesapeakelightcraft.com", "woodenboat.com", "sail-world.com"], ["boat", "sail", "kayak", "paddle"]),
    ("5-Hobbies & Interests/Model Building & Crafts", ["scalemates.com", "finescale.com", "hobbylinc.com"], ["model", "kit", "build"]),
    
    # Health & Wellness
    ("6-Health & Wellness/Medical Appointments", [], ["appointment", "reminder", "checkup", "results"]),
    ("6-Health & Wellness/Insurance", ["bupa.com.au", "medibank.com.au", "ahm.com.au", "nib.com.au"], ["insurance", "claim", "coverage"]),
    
    # Community & Events
    ("7-Community & Events/Meetups & Conferences", ["meetup.com", "eventbrite.com", "lu.ma"], ["meetup", "conference", "event", "talk"]),
    ("7-Community & Events/Newsletters", [], ["newsletter", "digest", "weekly", "monthly", "roundup"]),
    ("7-Community & Events/News & Digest", ["substack.com", "mailchimp.com", "convertkit.com"], ["news", "update", "digest"]),
    
    # Subscriptions & Services
    ("8-Subscriptions & Services/SaaS & Software", ["aws.amazon.com", "tailscale.com", "firecrawl.dev", "vercel.com", "supabase.io", "openai.com", "anthropic.com", "github.com"], ["usage", "quota", "limit"]),
    ("8-Subscriptions & Services/Streaming & Gaming", ["netflix.com", "spotify.com", "steam.com", "twitch.tv"], []),
    ("8-Subscriptions & Services/Shopping & Retail", ["amazon.com.au", "ebay.com.au", "aliexpress.com", "etsy.com"], ["order", "shipped", "delivery"]),
    ("8-Subscriptions & Services/Shopping & Retail", ["auspost.com.au", "notifications.auspost.com.au", "startrack.com.au"], ["parcel", "delivered", "collected", "ready for collection", "tracking"]),
    
    # For Deletion
    ("9-For-Deletion", ["hinge.co", "tinder.com", "bumble.com", "badoo.com", "grindr.com"], []),
    ("9-For-Deletion/Expired Offers", ["groupon.com", "scoopon.com.au"], ["expires", "last chance", "final hours", "ending soon", "hours left"]),
    ("9-For-Deletion/Newsletter Cleanup", [], ["unsubscribe", "opt-out", "no longer want"]),
]

# Always keep in inbox (never auto-archive)
KEEP_LIST = [
    "clcboats.com",
    "chesapeakelightcraft.com",
    # Add more: "paint-on-plastic.com", etc.
]

def get_labels(service):
    """Fetch all Gmail labels and cache IDs."""
    results = service.users().labels().list(userId='me').execute()
    for label in results['labels']:
        LABELS[label['name']] = label['id']
    return LABELS

def get_unread_messages(service, max_results=50):
    """Get unread messages from inbox."""
    results = service.users().messages().list(
        userId='me',
        q='is:unread in:inbox',
        maxResults=max_results
    ).execute()
    return results.get('messages', [])

def get_message_details(service, msg_id):
    """Get full message headers and metadata."""
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = {h['name']: h['value'] for h in msg['payload']['headers']}
    
    # Get body snippet
    snippet = msg.get('snippet', '')
    
    # Check for unsubscribe
    has_unsubscribe = any(
        'unsubscribe' in h.get('value', '').lower() 
        for h in msg['payload']['headers'] 
        if h['name'] in ['List-Unsubscribe', 'X-Report-Abuse']
    )
    
    return {
        'id': msg_id,
        'threadId': msg.get('threadId', ''),
        'subject': headers.get('Subject', '(no subject)'),
        'from': headers.get('From', '(unknown)'),
        'to': headers.get('To', ''),
        'date': headers.get('Date', ''),
        'snippet': snippet,
        'has_unsubscribe': has_unsubscribe,
        'labels': msg.get('labelIds', []),
        'internalDate': msg.get('internalDate', ''),
    }

def classify_message(msg_details):
    """Classify a message based on rules."""
    sender = msg_details['from'].lower()
    subject = msg_details['subject'].lower()
    
    # Extract email domain from sender
    domain = ""
    if '<' in sender and '>' in sender:
        email = sender.split('<')[1].split('>')[0]
        domain = email.split('@')[1] if '@' in email else ""
    elif '@' in sender:
        domain = sender.split('@')[1]
    
    matched_labels = []
    
    for label_name, sender_patterns, subject_patterns in RULES:
        match = False
        
        # Check sender patterns (match against full sender or domain)
        for pattern in sender_patterns:
            if pattern in sender or pattern in domain:
                match = True
                break
        
        # Check subject patterns
        for pattern in subject_patterns:
            if pattern in subject:
                match = True
                break
        
        if match:
            matched_labels.append(label_name)
    
    # Check if sender is in keep list
    should_keep = any(domain in sender or sender.endswith(domain) for domain in KEEP_LIST)
    
    # Check if newsletter (has unsubscribe)
    if msg_details['has_unsubscribe'] and '7-Community & Events/Newsletters' not in matched_labels:
        matched_labels.append('7-Community & Events/Newsletters')
    
    return {
        'labels': matched_labels,
        'should_keep': should_keep,
        'should_archive': not should_keep and len(matched_labels) > 0,
    }

def apply_label(service, msg_id, label_name):
    """Apply a label to a message."""
    if label_name not in LABELS:
        print(f"  ⚠ Label not found: {label_name}")
        return False
    
    try:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'addLabelIds': [LABELS[label_name]]}
        ).execute()
        return True
    except Exception as e:
        print(f"  ✗ Failed to apply label {label_name}: {e}")
        return False

def archive_message(service, msg_id):
    """Archive a message (remove from inbox)."""
    try:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['INBOX']}
        ).execute()
        return True
    except Exception as e:
        print(f"  ✗ Failed to archive: {e}")
        return False

def generate_brief(messages, classified):
    """Generate morning email brief."""
    brief = []
    brief.append(f"📧 Morning Email Brief — {datetime.now().strftime('%A, %d %B %Y')}")
    brief.append("")
    
    # Count by category
    counts = {
        'work': 0, 'projects': 0, 'finance': 0, 'personal': 0,
        'hobbies': 0, 'events': 0, 'subscriptions': 0, 'trash': 0,
        'uncategorized': 0
    }
    
    urgent = []
    keep_inbox = []
    auto_archive = []
    
    for msg, classification in zip(messages, classified):
        labels = classification['labels']
        
        if any('1-Work' in l for l in labels):
            counts['work'] += 1
        elif any('2-Projects' in l for l in labels):
            counts['projects'] += 1
        elif any('3-Finance' in l for l in labels):
            counts['finance'] += 1
        elif any('4-Personal' in l for l in labels):
            counts['personal'] += 1
        elif any('5-Hobbies' in l for l in labels):
            counts['hobbies'] += 1
        elif any('7-Community' in l for l in labels):
            counts['events'] += 1
        elif any('8-Subscriptions' in l for l in labels):
            counts['subscriptions'] += 1
        elif any('9-For-Deletion' in l for l in labels):
            counts['trash'] += 1
        else:
            counts['uncategorized'] += 1
        
        # Check for urgent patterns
        subject = msg['subject'].lower()
        if any(word in subject for word in ['interview', 'offer', 'deadline', 'urgent', 'action required']):
            urgent.append(f"  🔥 {msg['from'].split('<')[0].strip()} — {msg['subject']}")
        
        # Check keep list
        if classification['should_keep']:
            keep_inbox.append(f"  📌 {msg['from'].split('<')[0].strip()} — {msg['subject']}")
        
        # Check auto-archive
        if classification['should_archive']:
            auto_archive.append(f"  ✅ {msg['from'].split('<')[0].strip()} — {msg['subject']}")
    
    brief.append(f"Unread: {len(messages)} total")
    brief.append(f"- Work: {counts['work']}")
    brief.append(f"- Projects: {counts['projects']}")
    brief.append(f"- Finance: {counts['finance']}")
    brief.append(f"- Personal: {counts['personal']}")
    brief.append(f"- Hobbies: {counts['hobbies']}")
    brief.append(f"- Events: {counts['events']}")
    brief.append(f"- Subscriptions: {counts['subscriptions']}")
    brief.append(f"- Trash: {counts['trash']}")
    brief.append(f"- Uncategorized: {counts['uncategorized']}")
    brief.append("")
    
    if urgent:
        brief.append("🔥 Urgent:")
        brief.extend(urgent[:5])
        brief.append("")
    
    if keep_inbox:
        brief.append("📌 Keep in Inbox:")
        brief.extend(keep_inbox[:5])
        brief.append("")
    
    if auto_archive:
        brief.append("✅ Auto-archive candidates:")
        brief.extend(auto_archive[:5])
        if len(auto_archive) > 5:
            brief.append(f"  ... and {len(auto_archive) - 5} more")
        brief.append("")
    
    return "\n".join(brief)

def main():
    parser = argparse.ArgumentParser(description='Email Triage')
    parser.add_argument('--dry-run', action='store_true', help='Preview only, no changes')
    parser.add_argument('--apply', action='store_true', help='Apply labels and archive')
    parser.add_argument('--brief', action='store_true', help='Generate morning brief')
    parser.add_argument('--cleanup', action='store_true', help='Run cleanup (archive old newsletters)')
    args = parser.parse_args()
    
    # Default to brief if no args
    if not any([args.dry_run, args.apply, args.brief, args.cleanup]):
        args.brief = True
    
    print("Connecting to Gmail...")
    service = get_gmail_service()
    get_labels(service)
    
    print(f"Fetching unread messages...")
    messages = get_unread_messages(service, max_results=50)
    
    if not messages:
        print("No unread messages. Inbox is clean! 🎉")
        return
    
    print(f"Found {len(messages)} unread messages\n")
    
    # Get details and classify
    detailed = []
    classified = []
    
    for msg in messages:
        details = get_message_details(service, msg['id'])
        classification = classify_message(details)
        detailed.append(details)
        classified.append(classification)
    
    # Generate brief
    if args.brief or args.dry_run:
        brief = generate_brief(detailed, classified)
        print(brief)
    
    # Apply actions
    if args.apply:
        print("\nApplying labels and archiving...\n")
        
        applied_count = 0
        archived_count = 0
        
        for msg, classification in zip(detailed, classified):
            print(f"Processing: {msg['subject'][:50]}...")
            
            # Apply labels
            for label_name in classification['labels']:
                if apply_label(service, msg['id'], label_name):
                    applied_count += 1
            
            # Archive if appropriate
            if classification['should_archive']:
                if archive_message(service, msg['id']):
                    archived_count += 1
        
        print(f"\nDone! Applied {applied_count} labels, archived {archived_count} messages.")
    
    # Cleanup mode
    if args.cleanup:
        print("\nCleanup mode: Archiving old newsletters...")
        # TODO: Implement cleanup logic
        print("Cleanup not yet implemented. Use --apply for now.")

if __name__ == '__main__':
    main()
