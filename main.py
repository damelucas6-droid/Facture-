"""
API FastAPI pour la génération dynamique de factures PDF professionnelles.
"""

import os
import logging
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pdf_service import generate_invoice_pdf
from config import (
    API_TITLE, API_DESCRIPTION, API_VERSION,
    LOG_LEVEL, LOG_FILE, MAX_REQUESTS_PER_MINUTE
)

# ============================================================================
# CONFIGURATION DU LOGGING
# ============================================================================
# Créer le dossier logs s'il n'existe pas
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# RATE LIMITING
# ============================================================================
limiter = Limiter(key_func=get_remote_address)

# Initialisation de l'application FastAPI
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Ajouter le state pour le limiter
app.state.limiter = limiter

# Ajouter un gestionnaire d'erreur pour le rate limiting
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded for {request.client.host}")
    return HTMLResponse(
        status_code=429,
        content="<h1>429 Too Many Requests</h1><p>Vous avez dépassé le nombre de requêtes autorisées. Réessayez dans une minute.</p>"
    )

# Ajouter CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"Application démarrée - Limite: {MAX_REQUESTS_PER_MINUTE} requêtes/minute")


class InvoiceRequest(BaseModel):
    """
    Schéma de validation des données d'entrée pour la création d'une facture.
    """
    client_name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Nom complet du client ou de l'entreprise cliente.",
        examples=["Acme Corporation", "Jean Dupont"]
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Montant Hors Taxe (HT) en euros. Doit être strictement supérieur à 0.",
        examples=[1250.50]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "client_name": "Société Dupont & Associés",
                "amount": 1500.00
            }
        }
    }


@app.post(
    "/generate-invoice",
    summary="Générer une facture PDF",
    description="Prend en entrée le nom du client et le montant HT, génère le PDF en mémoire et le renvoie directement.",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Fichier PDF de la facture généré avec succès."
        },
        422: {
            "description": "Erreur de validation des données fournies (ex: montant négatif ou nom vide)."
        },
        429: {
            "description": "Trop de requêtes - limite de débit dépassée."
        }
    }
)
@limiter.limit(f"{MAX_REQUESTS_PER_MINUTE}/minute")
async def generate_invoice_endpoint(request: Request, invoice_data: InvoiceRequest):
    """
    Endpoint POST pour générer et télécharger la facture PDF.
    
    - **client_name** : Nom du client (obligatoire, chaîne non vide).
    - **amount** : Montant HT en euros (obligatoire, flottant > 0).
    """
    client_ip = request.client.host
    logger.info(f"[{client_ip}] Demande de génération de facture pour {invoice_data.client_name} ({invoice_data.amount}€)")
    
    try:
        # Génération du PDF en mémoire
        pdf_buffer, invoice_number = generate_invoice_pdf(
            client_name=invoice_data.client_name.strip(),
            amount_ht=invoice_data.amount,
            vat_rate=0.20  # TVA à 20%
        )
        
        # Nom de fichier personnalisé pour le téléchargement
        filename = f"Facture_{invoice_number}.pdf"
        
        # En-têtes HTTP pour indiquer au navigateur d'afficher et/ou télécharger le PDF
        headers = {
            "Content-Disposition": f'inline; filename="{filename}"',
            "X-Invoice-Number": invoice_number
        }
        
        logger.info(f"[{client_ip}] Facture {invoice_number} générée avec succès ({len(pdf_buffer.getvalue())} bytes)")
        
        return StreamingResponse(
            content=pdf_buffer,
            media_type="application/pdf",
            headers=headers
        )
        
    except ValueError as e:
        logger.error(f"[{client_ip}] Erreur de validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur de validation: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[{client_ip}] Erreur lors de la génération du PDF: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération du document PDF : {str(e)}"
        )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@limiter.limit(f"{MAX_REQUESTS_PER_MINUTE}/minute")
async def home(request: Request):
    """
    Page d'accueil interactive permettant de tester directement l'API depuis le navigateur.
    """
    logger.info(f"[{request.client.host}] Accès à la page d'accueil")
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Générateur de Factures PDF</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>body { font-family: 'Inter', sans-serif; }</style>
    </head>
    <body class="bg-slate-100 min-h-screen flex items-center justify-center p-4">
        <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
            <div class="text-center mb-8">
                <div class="inline-flex items-center justify-center w-14 h-14 bg-blue-100 text-blue-600 rounded-xl mb-4">
                    <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                </div>
                <h1 class="text-2xl font-bold text-slate-800">Générateur de Factures</h1>
                <p class="text-sm text-slate-500 mt-1">Générez vos factures PDF certifiées en 1 clic</p>
            </div>

            <form id="invoiceForm" class="space-y-5">
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1">Nom du client</label>
                    <input type="text" id="client_name" required placeholder="Ex: Société Alpha SARL"
                        class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition text-slate-800">
                </div>

                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-1">Montant (€ HT)</label>
                    <input type="number" id="amount" step="0.01" min="0.01" required placeholder="Ex: 1450.00"
                        class="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition text-slate-800">
                </div>

                <button type="submit" id="submitBtn"
                    class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg shadow-md hover:shadow-lg transition duration-200 flex items-center justify-center space-x-2">
                    <span>Générer & Télécharger le PDF</span>
                </button>
            </form>

            <div class="mt-6 pt-6 border-t border-slate-200 text-center text-xs text-slate-500 space-y-1">
                <p>Documentation interactive Swagger : <a href="/docs" class="text-blue-600 hover:underline font-medium">/docs</a></p>
                <p>Spécification OpenAPI : <a href="/openapi.json" class="text-blue-600 hover:underline font-medium">/openapi.json</a></p>
            </div>
        </div>

        <script>
            document.getElementById('invoiceForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const btn = document.getElementById('submitBtn');
                const originalText = btn.innerHTML;
                
                const client_name = document.getElementById('client_name').value.trim();
                const amount = parseFloat(document.getElementById('amount').value);

                if (!client_name || isNaN(amount) || amount <= 0) {
                    alert("Veuillez renseigner un nom valide et un montant strictement supérieur à 0.");
                    return;
                }

                btn.disabled = true;
                btn.innerHTML = `<span>Génération en cours...</span>`;

                try {
                    const response = await fetch('/generate-invoice', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ client_name, amount })
                    });

                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(JSON.stringify(error.detail || "Erreur lors de la génération"));
                    }

                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    
                    // Ouvrir dans un nouvel onglet
                    window.open(url, '_blank');

                    // Déclencher le téléchargement direct
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `facture_${client_name.replace(/[^a-zA-Z0-9_-]/g, '_')}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                } catch (err) {
                    alert("Erreur: " + err.message);
                } finally {
                    btn.disabled = false;
                    btn.innerHTML = originalText;
                }
            });
        </script>
    </body>
    </html>
    """
