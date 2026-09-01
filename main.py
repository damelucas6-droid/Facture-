"""
API FastAPI pour la génération dynamique de factures PDF professionnelles.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel, Field
from pdf_service import generate_invoice_pdf

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API de Génération de Factures PDF",
    description="Génère des factures professionnelles au format PDF à la volée en mémoire avec FastAPI et ReportLab.",
    version="1.0.0"
)


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
        }
    }
)
async def generate_invoice_endpoint(invoice_data: InvoiceRequest):
    """
    Endpoint POST pour générer et télécharger la facture PDF.
    
    - **client_name** : Nom du client (obligatoire, chaîne non vide).
    - **amount** : Montant HT en euros (obligatoire, flottant > 0).
    """
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
        
        return StreamingResponse(
            content=pdf_buffer,
            media_type="application/pdf",
            headers=headers
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération du document PDF : {str(e)}"
        )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home():
    """
    Page d'accueil interactive permettant de tester directement l'API depuis le navigateur.
    """
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
