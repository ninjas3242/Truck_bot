"""
Date and time parsing utilities
"""
from datetime import datetime, timedelta
import re
from typing import Optional

def parse_user_datetime(text: str) -> Optional[datetime]:
    """Parse user input like 'tomorrow 2pm' into actual datetime"""
    text = text.lower().strip()
    print(f"DEBUG: Parsing datetime from: {text}")
    
    # Get current time
    now = datetime.now()
    
    # Parse time (2pm, 14:00, etc.)
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
    hour = 14  # default 2pm
    minute = 0
    
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        am_pm = time_match.group(3)
        
        if am_pm == 'pm' and hour != 12:
            hour += 12
        elif am_pm == 'am' and hour == 12:
            hour = 0
        print(f"DEBUG: Parsed time: {hour}:{minute:02d}")
    
    # Parse date
    target_date = now.date()
    
    if 'tomorrow' in text:
        target_date = (now + timedelta(days=1)).date()
        print(f"DEBUG: Parsed date: tomorrow -> {target_date}")
    elif 'today' in text:
        target_date = now.date()
        print(f"DEBUG: Parsed date: today -> {target_date}")
    elif 'monday' in text:
        days_ahead = 0 - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        target_date = (now + timedelta(days=days_ahead)).date()
    elif 'tuesday' in text:
        days_ahead = 1 - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        target_date = (now + timedelta(days=days_ahead)).date()
    
    result = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
    print(f"DEBUG: Final datetime: {result}")
    return result

def extract_truck_type(text: str) -> str:
    """Extract truck type from user input"""
    text = text.lower()
    
    if '2 horse' in text or 'two horse' in text:
        return '2-horse'
    elif '5 horse' in text or 'five horse' in text:
        return '5-horse'
    elif '6 horse' in text or 'six horse' in text:
        return '6-horse'
    elif 'horse' in text:
        return 'horse truck'
    
    return 'truck consultation'

def extract_email(text: str) -> Optional[str]:
    """Extract email from user input"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None