"""
Configuration centralisée pour l'application de génération de factures PDF.
Charge les variables depuis un fichier .env ou utilise des valeurs par défaut.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# ============================================================================
# CONFIGURATION DE L'ENTREPRISE
# ============================================================================
COMPANY = {
    "name": os.getenv("COMPANY_NAME", "TECHCORP SOLUTIONS SAS"),
    "address": os.getenv("COMPANY_ADDRESS", "123 Avenue des Champs-Élysées, 75008 Paris"),
    "siret": os.getenv("COMPANY_SIRET", "892 145 987 00012"),
    "vat_number": os.getenv("COMPANY_VAT_NUMBER", "FR 45 892145987"),
    "email": os.getenv("COMPANY_EMAIL", "contact@techcorp-solutions.fr"),
    "phone": os.getenv("COMPANY_PHONE", "+33 (0)1 42 68 00 00"),
}

# ============================================================================
# CONFIGURATION BANCAIRE
# ============================================================================
BANK = {
    "name": os.getenv("BANK_NAME", "BNP Paribas Paris Étoile"),
    "iban": os.getenv("BANK_IBAN", "FR76 3000 4000 0100 2458 9632 145"),
    "bic": os.getenv("BANK_BIC", "BNPAFR22XXX"),
}

# ============================================================================
# CONFIGURATION DE FACTURATION
# ============================================================================
VAT_RATE = float(os.getenv("VAT_RATE", "0.20"))  # TVA par défaut = 20%
DEFAULT_PAYMENT_DAYS = int(os.getenv("DEFAULT_PAYMENT_DAYS", "30"))  # Délai de paiement par défaut
CURRENCY = os.getenv("CURRENCY", "FCFA")  # Devise (par défaut: FCFA)

# ============================================================================
# CONFIGURATION RÉSEAU & SÉCURITÉ
# ============================================================================
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
MAX_REQUESTS_PER_HOUR = int(os.getenv("MAX_REQUESTS_PER_HOUR", "1000"))

# ============================================================================
# CONFIGURATION LOGGING
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

# ============================================================================
# CONFIGURATION DE L'API
# ============================================================================
API_TITLE = os.getenv("API_TITLE", "API de Génération de Factures PDF")
API_DESCRIPTION = os.getenv(
    "API_DESCRIPTION",
    "Génère des factures professionnelles au format PDF à la volée en mémoire avec FastAPI et ReportLab."
)
API_VERSION = os.getenv("API_VERSION", "1.0.0")

# ============================================================================
# CONFIGURATION DES STYLES PDF
# ============================================================================
PDF_COLORS = {
    "primary": os.getenv("PDF_PRIMARY_COLOR", "#1E3A8A"),      # Bleu marine
    "text_dark": os.getenv("PDF_TEXT_DARK_COLOR", "#1F2937"),   # Gris anthracite
    "text_muted": os.getenv("PDF_TEXT_MUTED_COLOR", "#6B7280"), # Gris secondaire
    "bg_light": os.getenv("PDF_BG_LIGHT_COLOR", "#F8FAFC"),     # Fond clair
    "border": os.getenv("PDF_BORDER_COLOR", "#E2E8F0"),         # Bordures
}

PDF_MARGINS_CM = float(os.getenv("PDF_MARGINS_CM", "1.5"))


def validate_config():
    """Valide que la configuration est correcte."""
    if not COMPANY["name"]:
        raise ValueError("COMPANY_NAME ne peut pas être vide")
    if not BANK["iban"]:
        raise ValueError("BANK_IBAN ne peut pas être vide")
    if VAT_RATE < 0 or VAT_RATE > 1:
        raise ValueError("VAT_RATE doit être entre 0 et 1")


if __name__ == "__main__":
    print("Configuration chargée avec succès:")
    print(f"- Entreprise: {COMPANY['name']}")
    print(f"- TVA: {int(VAT_RATE*100)}%")
    print(f"- Logging level: {LOG_LEVEL}")
