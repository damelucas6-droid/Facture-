# API FastAPI de Génération de Factures PDF

Cette API permet de générer à la volée des factures professionnelles au format PDF prêtes à être imprimées et téléchargées.

---

## 🚀 1. Installation des dépendances

Installez les bibliothèques requises :

```bash
pip install fastapi uvicorn reportlab pydantic
```

*(Optionnel pour les tests automatisés : `pip install httpx`)*

---

## 💻 2. Lancement du serveur

Démarrez le serveur Uvicorn avec rechargement automatique :

```bash
uvicorn main:app --reload
```

Le serveur sera accessible sur : `http://127.0.0.1:8000`

---

## 📄 3. Utilisation de l'API

### A. Interface Web Interactive & Swagger
- **Page de test intégrée** : Rendez-vous sur `http://127.0.0.1:8000/` pour tester directement via un formulaire élégant.
- **Documentation Swagger** : `http://127.0.0.1:8000/docs`
- **Documentation Redoc** : `http://127.0.0.1:8000/redoc`

---

### B. Endpoint `POST /generate-invoice`

#### Corps de la requête (JSON) :
```json
{
  "client_name": "Société Dupont & Associés",
  "amount": 1500.00
}
```

#### Règles de validation (Pydantic) :
- `client_name` : Chaîne de caractères obligatoire (non vide).
- `amount` : Nombre flottant obligatoire, strictement supérieur à 0 (`gt=0`).

#### Réponse :
- **Status** : `200 OK`
- **Content-Type** : `application/pdf`
- **Content-Disposition** : `inline; filename="Facture_FAC-YYYYMM-XXXXXX.pdf"`

---

### C. Exemples d'appels

#### Avec `cURL` (téléchargement direct) :
```bash
curl -X POST "http://127.0.0.1:8000/generate-invoice" \
     -H "Content-Type: application/json" \
     -d '{"client_name": "Acme Corp", "amount": 2400.50}' \
     --output facture.pdf
```

#### Avec Python (`requests`) :
```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/generate-invoice",
    json={"client_name": "Cabinet Lambert", "amount": 950.00}
)

if response.status_code == 200:
    with open("facture_telechargee.pdf", "wb") as f:
        f.write(response.content)
    print("Facture sauvegardée avec succès !")
else:
    print("Erreur :", response.json())
```

---

## 🧪 4. Exécuter les tests automatisés

Lancez le script de test :

```bash
python test_api.py
```
