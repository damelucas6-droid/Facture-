"""
Script de test automatisé pour vérifier la génération du PDF et le bon fonctionnement de l'API FastAPI.
"""

import os
from starlette.testclient import TestClient
from main import app
from pdf_service import generate_invoice_pdf

client = TestClient(app)


def test_pdf_generation_service():
    """Vérifie la génération directe du flux PDF en mémoire."""
    print("[1/4] Test du service ReportLab...")
    buffer, invoice_number = generate_invoice_pdf(client_name="Test Client SARL", amount_ht=1500.0)
    pdf_bytes = buffer.getvalue()
    
    assert len(pdf_bytes) > 1000, "Le fichier PDF est anormalement petit ou vide."
    assert pdf_bytes.startswith(b"%PDF"), "Le fichier généré n'a pas la signature PDF valide."
    assert invoice_number.startswith("FAC-"), "Le numéro de facture ne respecte pas le format attendu."
    print(f" -> Succès : Facture {invoice_number} générée ({len(pdf_bytes):,} octets).")


def test_api_valid_request():
    """Vérifie l'endpoint /generate-invoice avec des données valides."""
    print("[2/4] Test de l'endpoint POST /generate-invoice (cas valide)...")
    payload = {
        "client_name": "ACME Industries",
        "amount": 2450.75
    }
    response = client.post("/generate-invoice", json=payload)
    assert response.status_code == 200, f"Erreur inattendue : {response.status_code} - {response.text}"
    assert response.headers.get("content-type") == "application/pdf"
    assert "inline; filename=" in response.headers.get("content-disposition", "")
    assert response.content.startswith(b"%PDF")
    print(f" -> Succès : Code 200, Content-Type 'application/pdf', taille {len(response.content):,} octets.")


def test_api_invalid_amount():
    """Vérifie le rejet par Pydantic d'un montant négatif ou nul."""
    print("[3/4] Test de validation Pydantic (montant négatif <= 0)...")
    payload = {
        "client_name": "Client Invalide",
        "amount": -50.0
    }
    response = client.post("/generate-invoice", json=payload)
    assert response.status_code == 422, f"Le statut devrait être 422, reçu : {response.status_code}"
    print(" -> Succès : Requête rejetée avec code 422 (Unprocessable Entity).")


def test_api_empty_client_name():
    """Vérifie le rejet par Pydantic d'un nom de client vide."""
    print("[4/4] Test de validation Pydantic (nom de client vide)...")
    payload = {
        "client_name": "",
        "amount": 100.0
    }
    response = client.post("/generate-invoice", json=payload)
    assert response.status_code == 422, f"Le statut devrait être 422, reçu : {response.status_code}"
    print(" -> Succès : Requête rejetée avec code 422 (Unprocessable Entity).")


if __name__ == "__main__":
    print("=== Démarrage de la suite de tests ===")
    test_pdf_generation_service()
    test_api_valid_request()
    test_api_invalid_amount()
    test_api_empty_client_name()
    print("\n TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS !")
