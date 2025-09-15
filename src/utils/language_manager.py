"""
Language management utilities for multi-language support
"""
from typing import Dict, Optional
import streamlit as st
from langdetect import detect
from googletrans import Translator

class LanguageManager:
    def __init__(self):
        self.translator = Translator()
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load translation dictionary"""
        return {
            "en": {
                "welcome": "Welcome to Stephex Horse Trucks! How can I help you today?",
                "language_select": "Select Language",
                "chat_placeholder": "Type your message here...",
                "send": "Send",
                "clear_chat": "Clear Chat",
                "truck_types": "What type of truck are you looking for?",
                "budget_question": "What's your budget range?",
                "contact_info": "Can I get your contact information?",
                "schedule_visit": "Would you like to schedule a visit?",
                "error_message": "Sorry, I encountered an error. Please try again.",
                "thinking": "Thinking...",
                "new_trucks": "New Trucks",
                "used_trucks": "Used Trucks",
                "financing": "Financing Options",
                "contact": "Contact Us"
            },
            "es": {
                "welcome": "¡Bienvenido a Stephex Horse Trucks! ¿Cómo puedo ayudarte hoy?",
                "language_select": "Seleccionar Idioma",
                "chat_placeholder": "Escribe tu mensaje aquí...",
                "send": "Enviar",
                "clear_chat": "Limpiar Chat",
                "truck_types": "¿Qué tipo de camión estás buscando?",
                "budget_question": "¿Cuál es tu rango de presupuesto?",
                "contact_info": "¿Puedo obtener tu información de contacto?",
                "schedule_visit": "¿Te gustaría programar una visita?",
                "error_message": "Lo siento, encontré un error. Por favor intenta de nuevo.",
                "thinking": "Pensando...",
                "new_trucks": "Camiones Nuevos",
                "used_trucks": "Camiones Usados",
                "financing": "Opciones de Financiamiento",
                "contact": "Contáctanos"
            },
            "fr": {
                "welcome": "Bienvenue chez Stephex Horse Trucks! Comment puis-je vous aider aujourd'hui?",
                "language_select": "Sélectionner la Langue",
                "chat_placeholder": "Tapez votre message ici...",
                "send": "Envoyer",
                "clear_chat": "Effacer le Chat",
                "truck_types": "Quel type de camion recherchez-vous?",
                "budget_question": "Quelle est votre gamme de budget?",
                "contact_info": "Puis-je obtenir vos informations de contact?",
                "schedule_visit": "Souhaitez-vous programmer une visite?",
                "error_message": "Désolé, j'ai rencontré une erreur. Veuillez réessayer.",
                "thinking": "Réflexion...",
                "new_trucks": "Nouveaux Camions",
                "used_trucks": "Camions d'Occasion",
                "financing": "Options de Financement",
                "contact": "Nous Contacter"
            },
            "it": {
                "welcome": "Benvenuto da Stephex Horse Trucks! Come posso aiutarti oggi?",
                "language_select": "Seleziona Lingua",
                "chat_placeholder": "Scrivi il tuo messaggio qui...",
                "send": "Invia",
                "clear_chat": "Cancella Chat",
                "truck_types": "Che tipo di camion stai cercando?",
                "budget_question": "Qual è il tuo budget?",
                "contact_info": "Posso avere le tue informazioni di contatto?",
                "schedule_visit": "Vorresti programmare una visita?",
                "error_message": "Scusa, ho riscontrato un errore. Riprova.",
                "thinking": "Pensando...",
                "new_trucks": "Camion Nuovi",
                "used_trucks": "Camion Usati",
                "financing": "Opzioni di Finanziamento",
                "contact": "Contattaci"
            },
            "nl": {
                "welcome": "Welkom bij Stephex Horse Trucks! Hoe kan ik je vandaag helpen?",
                "language_select": "Selecteer Taal",
                "chat_placeholder": "Typ je bericht hier...",
                "send": "Verstuur",
                "clear_chat": "Wis Chat",
                "truck_types": "Welk type vrachtwagen zoek je?",
                "budget_question": "Wat is je budget?",
                "contact_info": "Mag ik je contactgegevens?",
                "schedule_visit": "Wil je een bezoek inplannen?",
                "error_message": "Sorry, er is een fout opgetreden. Probeer opnieuw.",
                "thinking": "Aan het denken...",
                "new_trucks": "Nieuwe Vrachtwagens",
                "used_trucks": "Gebruikte Vrachtwagens",
                "financing": "Financieringsopties",
                "contact": "Contact"
            }
        }
    
    def get_text(self, key: str, language: str = "en") -> str:
        """Get translated text for a given key"""
        return self.translations.get(language, {}).get(key, 
               self.translations["en"].get(key, key))
    
    def detect_language(self, text: str) -> str:
        """Detect language from user input"""
        try:
            detected = detect(text)
            return detected if detected in self.translations else "en"
        except:
            return "en"
    
    def translate_text(self, text: str, target_lang: str) -> str:
        """Translate text to target language"""
        try:
            if target_lang == "en":
                return text
            result = self.translator.translate(text, dest=target_lang)
            return result.text
        except:
            return text

# Global instance
language_manager = LanguageManager()