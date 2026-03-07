# Pricing API - Orchestrateur d'Estimation de Prix

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![Pydantic](https://img.shields.io/badge/Pydantic-2.0+-e92063.svg)

---

## Présentation du Projet

**Pricing API** est un service web asynchrone développé avec **FastAPI**. Son rôle est d'agir comme un **orchestrateur central** pour estimer le prix optimal d'un produit sur le marché.

Le système repose sur une architecture modulaire orientée objet (OOP) qui coordonne le travail de trois sous-systèmes virtuels :

| # | Sous-système | Rôle |
|---|---|---|
| 1 | **Data Engineering (Scraping)** | Récupération des annonces de produits en temps réel (ex: Amazon via Scraper API) |
| 2 | **Data Science (Analyse)** | Calcul des statistiques du marché : moyenne, médiane, min, max |
| 3 | **Intelligence Artificielle (Agent LLM)** | Génération d'un prix recommandé et justifié selon une stratégie de vente |

> Le projet applique de solides principes **SOLID**, notamment l'inversion de dépendance via des interfaces (`ABC`) et l'injection de dépendances, permettant de changer facilement d'implémentation.

---

## Fonctionnalités Principales

- **Pipeline complet d'estimation (`/estimate`)** : De la recherche produit jusqu'à la recommandation de prix finale.
- **Tolérance aux pannes (Mocks intégrés)** : Si les services externes sont indisponibles ou non configurés, le système bascule automatiquement sur des données simulées pour garantir la continuité en développement.
- **Validation stricte des données** : Utilisation de Pydantic pour s'assurer que les données échangées entre les composants respectent un contrat strict.
- **Sondes de santé (`/health`)** : Endpoint de monitoring pour vérifier la latence et l'état (`healthy`, `degraded`, `unreachable`) de chaque composant externe.
- **Génération de rapports (`/admin/report`)** : Endpoint sécurisé pour générer un diagnostic système sur le disque du serveur.

---

## Architecture du Projet

```
pricing-api/
├── main.py          # Point d'entrée FastAPI, routes et injection des dépendances
├── controller.py    # Logique d'orchestration (PriceController)
├── interfaces.py    # Classes abstraites (contrats ABC)
├── clients.py       # Implémentations concrètes asynchrones (httpx)
├── mocks.py         # Implémentations simulées pour le développement local
├── schemas.py       # Modèles de données Pydantic (DTOs)
├── exceptions.py    # Hiérarchie d'erreurs métier personnalisées
├── reporting.py     # Module utilitaire pour la génération de rapports
└── .env             # Configuration des variables d'environnement
```

---

## Installation & Lancement

### 1. Prérequis

- Python **3.9** ou supérieur
- Un environnement virtuel (recommandé)

### 2. Cloner le dépôt

```bash
git clone <url-du-repo>
cd pricing-api
```

### 3. Créer et activer l'environnement virtuel

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Installer les dépendances

```bash
pip install fastapi uvicorn httpx pydantic python-dotenv
```

### 5. Configurer l'environnement

Créez un fichier `.env` à la racine du projet. Laissez les valeurs vides pour utiliser les **Mocks** en développement local.

```ini
# .env

# Clé d'accès au service de scraping
SCRAPER_API_KEY=votre_cle_scraper_api

# URL du microservice d'analyse de données
ANALYZER_API_URL=http://adresse-ip-equipe-data:port

# URL du microservice d'agent IA
AI_AGENT_API_URL=http://adresse-ip-equipe-ia:port

# Token d'authentification pour les endpoints admin
ADMIN_TOKEN=mon_token_super_secret_pour_les_rapports

# Répertoire de destination pour les rapports générés
REPORT_DIR=/tmp
```

### 6. Lancer le serveur

```bash
python -m uvicorn main:app --reload
```

| Ressource | URL |
|---|---|
| API | `http://127.0.0.1:8000` |
| Documentation Swagger | `http://127.0.0.1:8000/docs` |
| Documentation ReDoc | `http://127.0.0.1:8000/redoc` |

---

## Référence des Endpoints

### `POST /estimate` — Estimer un prix

Lance le pipeline complet et retourne un prix recommandé pour le produit.

**Corps de la requête :**

```json
{
  "product_name": "PlayStation 5",
  "strategy": "balanced",
  "condition": "new"
}
```

| Champ | Type | Description |
|---|---|---|
| `product_name` | `string` | Nom du produit à estimer |
| `strategy` | `string` | Stratégie de vente : `fast_sale`, `balanced`, `max_profit` |
| `condition` | `string` | État du produit : `new`, `used`, etc. |

**Réponse (`200 OK`) :**

```json
{
  "product_name": "PlayStation 5",
  "recommended_price": 441.0,
  "currency": "EUR",
  "confidence_score": 0.95,
  "justification": "Stratégie 'balanced' : prix recommandé à 98% de la moyenne de marché (450.0€).",
  "market_stats": {
    "mean": 450.0,
    "median": 450.0,
    "min": 400.0,
    "max": 500.0,
    "count": 3.0
  }
}
```

---

### `GET /health` — Vérifier l'état du système

Retourne l'état et la latence de chaque composant externe.

**Réponse (`200 OK`) :**

```json
{
  "status": "healthy",
  "components": {
    "scraper": {
      "status": "ok",
      "latency_ms": 105.2,
      "detail": null
    },
    "ai_agent": {
      "status": "ok",
      "latency_ms": 12.4,
      "detail": null
    }
  }
}
```

| Statut possible | Signification |
|---|---|
| `healthy` | Tous les composants sont opérationnels |
| `degraded` | Un ou plusieurs composants répondent avec des erreurs |
| `unreachable` | Un composant est inaccessible |

---

### `GET /admin/report` — Générer un rapport système

> **Endpoint sécurisé** — Requiert le header `X-Admin-Token`.

```bash
curl -X GET "http://127.0.0.1:8000/admin/report" \
     -H "X-Admin-Token: mon_token_super_secret_pour_les_rapports"
```

Le rapport est généré et sauvegardé dans le répertoire défini par `REPORT_DIR` dans le `.env`.

---

## Gestion des Erreurs

Le projet expose une hiérarchie d'erreurs métier personnalisées pour faciliter le débogage :

| Exception | Description |
|---|---|
| `InsufficientDataError` | Pas assez d'annonces trouvées pour calculer des statistiques fiables |
| `MarketUnreachableError` | Le service de scraping est inaccessible |

---

## Mode Développement (Mocks)

Si aucune URL n'est configurée dans le `.env`, le système bascule automatiquement sur les **Mocks** définis dans `mocks.py`. Cela permet de développer et tester l'API sans dépendre des microservices externes.

---
