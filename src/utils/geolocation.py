"""
Geolocation service for IP-based language detection
"""
import requests
import streamlit as st
from typing import Optional

# Country to language mapping
COUNTRY_LANGUAGE_MAP = {
    'ES': 'es',  # Spain
    'MX': 'es',  # Mexico
    'AR': 'es',  # Argentina
    'CO': 'es',  # Colombia
    'PE': 'es',  # Peru
    'VE': 'es',  # Venezuela
    'CL': 'es',  # Chile
    'EC': 'es',  # Ecuador
    'GT': 'es',  # Guatemala
    'CU': 'es',  # Cuba
    'BO': 'es',  # Bolivia
    'DO': 'es',  # Dominican Republic
    'HN': 'es',  # Honduras
    'PY': 'es',  # Paraguay
    'SV': 'es',  # El Salvador
    'NI': 'es',  # Nicaragua
    'CR': 'es',  # Costa Rica
    'PA': 'es',  # Panama
    'UY': 'es',  # Uruguay
    'PR': 'es',  # Puerto Rico
    
    'FR': 'fr',  # France
    'BE': 'fr',  # Belgium (also Dutch)
    'CH': 'fr',  # Switzerland (also German, Italian)
    'CA': 'fr',  # Canada (also English)
    'LU': 'fr',  # Luxembourg
    'MC': 'fr',  # Monaco
    
    'IT': 'it',  # Italy
    'SM': 'it',  # San Marino
    'VA': 'it',  # Vatican City
    
    'NL': 'nl',  # Netherlands
    'SR': 'nl',  # Suriname
}

def get_user_ip() -> Optional[str]:
    """Get user's IP address from Streamlit"""
    try:
        # Try to get real IP from headers (works in production)
        if hasattr(st, 'context') and hasattr(st.context, 'headers'):
            headers = st.context.headers
            # Check common headers for real IP
            for header in ['X-Forwarded-For', 'X-Real-IP', 'CF-Connecting-IP']:
                if header in headers:
                    ip = headers[header].split(',')[0].strip()
                    if ip and ip != '127.0.0.1':
                        return ip
        
        # Fallback: get IP from external service
        response = requests.get('https://api.ipify.org', timeout=3)
        if response.status_code == 200:
            return response.text.strip()
            
    except Exception as e:
        print(f"DEBUG: Error getting IP: {e}")
    
    return None

def get_country_from_ip(ip: str) -> Optional[str]:
    """Get country code from IP address"""
    try:
        # Use free IP geolocation service
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data.get('countryCode')
    except Exception as e:
        print(f"DEBUG: Error getting country from IP: {e}")
    
    return None

def detect_language_from_ip() -> str:
    """Detect user's language based on IP geolocation"""
    try:
        # Get user's IP
        ip = get_user_ip()
        if not ip:
            print("DEBUG: Could not get user IP, defaulting to English")
            return 'en'
        
        print(f"DEBUG: User IP: {ip}")
        
        # Get country from IP
        country = get_country_from_ip(ip)
        if not country:
            print("DEBUG: Could not get country from IP, defaulting to English")
            return 'en'
        
        print(f"DEBUG: User country: {country}")
        
        # Map country to language
        language = COUNTRY_LANGUAGE_MAP.get(country, 'en')
        print(f"DEBUG: Detected language: {language}")
        
        return language
        
    except Exception as e:
        print(f"DEBUG: Error in language detection: {e}")
        return 'en'  # Default to English on any error