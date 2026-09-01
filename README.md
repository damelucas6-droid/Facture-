# API FastAPI de Génération de Factures PDF

Cette API permet de générer à la volée des factures professionnelles au format PDF prêtes à être imprimées et téléchargées.

---

## 🚀 1. Installation des dépendances

Installez les bibliothèques requises :

```bash
pip install -r requirements.txt
```

*(Les dépendances incluent : `fastapi`, `uvicorn`, `reportlab`, `pydantic`, `python-dotenv`, `slowapi`)*

---

## ⚙️ 2. Configuration de l'application

### A. Créer le fichier `.env`

Copiez le fichier `.env.example` en `.env` et personnalisez les paramètres :

```bash
cp .env.example .env
```

Éditez `.env` et modifiez les variables suivantes :

```env
# CONFIGURATION DE L'ENTREPRISE
COMPANY_NAME=MA SOCIETE SARL
COMPANY_ADDRESS=123 Rue de la Paix, 75000 Paris
COMPANY_SIRET=123 456 789 00012
COMPANY_VAT_NUMBER=FR 45 123456789
COMPANY_EMAIL=facturation@monsociete.fr
COMPANY_PHONE=+33 1 23 45 67 89

# CONFIGURATION BANCAIRE
BANK_NAME=Ma Banque
BANK_IBAN=FR76 3000 4000 0100 XXXX XXXX XXX
BANK_BIC=BNPAFR22XXX

# AUTRES PARAMÈTRES
VAT_RATE=0.20
DEFAULT_PAYMENT_DAYS=30
MAX_REQUESTS_PER_MINUTE=60
LOG_LEVEL=INFO
```

---

## 💻 3. Lancement du serveur

Démarrez le serveur Uvicorn avec rechargement automatique :

```bash
uvicorn main:app --reload
```

Le serveur sera accessible sur : `http://127.0.0.1:8000`

---

## 📄 4. Utilisation de l'API

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

## 🧪 5. Exécuter les tests automatisés

Lancez le script de test :

```bash
python test_api.py
```

---

## 📋 6. Nouvelles Fonctionnalités (v1.1)

### ✨ Rate Limiting
L'API est protégée contre les abus via **rate limiting** :
- **Limite** : 60 requêtes par minute par adresse IP
- **Erreur 429** : Si le quota est dépassé

### 📊 Logging
Tous les événements importants sont enregistrés :
- Demandes de génération de factures
- Erreurs et exceptions
- Accès aux endpoints
- **Fichier log** : `logs/app.log`

### 🔒 Configuration Externalisée
- Les données sensibles (IBAN, coordonnées) sont maintenant externalisées dans `.env`
- Facilite le déploiement sur différents environnements
- Respecte les bonnes pratiques de sécurité

### 📈 CORS Middleware
L'API accepte les requêtes cross-origin (CORS), idéal pour :
- Les applications web frontend
- Les appels depuis d'autres domaines
- Les intégrations tierces

---

## 🛡️ 7. Sécurité

- ✅ Validation stricte des entrées (Pydantic)
- ✅ Rate limiting automatique
- ✅ Données sensibles externalisées
- ✅ Logging détaillé des erreurs
- ✅ CORS configuré de manière sûre

---

## 📦 8. Structure du Projet

```
.
├── main.py                  # API FastAPI principale
├── pdf_service.py           # Service de génération de PDF
├── config.py                # Configuration externalisée
├── test_api.py              # Tests automatisés
├── requirements.txt         # Dépendances Python
├── .env                     # Variables d'environnement (local)
├── .env.example             # Template .env
├── .gitignore               # Fichiers à ignorer dans Git
├── README.md                # Cette documentation
└── logs/                    # Répertoire des logs (créé auto)
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"
```bash
pip install python-dotenv
```

### "ModuleNotFoundError: No module named 'slowapi'"
```bash
pip install slowapi
```

### Logs ne s'affichent pas ?
Vérifiez que le répertoire `logs/` existe :
```bash
mkdir logs
```

---

## 📞 Support

Pour toute question ou bug, consultez les fichiers de log dans `logs/app.log`.

