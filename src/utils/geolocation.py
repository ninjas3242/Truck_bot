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
        # Always use external service to get real public IP (works with VPN)
        response = requests.get('https://api.ipify.org', timeout=5)
        if response.status_code == 200:
            public_ip = response.text.strip()
            print(f"DEBUG: Got public IP: {public_ip}")
            return public_ip
            
    except Exception as e:
        print(f"DEBUG: Error getting public IP: {e}")
    
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
        
        # Debug: Force Netherlands for testing
        if country == 'NL':
            print(f"DEBUG: Netherlands detected, setting to Dutch")
            return 'nl'
        
        return language
        
    except Exception as e:
        print(f"DEBUG: Error in language detection: {e}")
        return 'en'  # Default to English on any error