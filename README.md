````markdown
# Network Dashboards

![node](https://img.shields.io/badge/node-javascript-339933?style=flat-square) ![python](https://img.shields.io/badge/python-3.x-3776AB?style=flat-square)

Un dashboard de monitoring réseau complet avec backend FastAPI et frontend Vue.js 3, permettant de visualiser les métriques réseau en temps réel.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Stack technique](#stack-technique)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Contribuer](#contribuer)

## Fonctionnalités

- Monitoring de la bande passante (débit upload/download)
- Mesure de latence vers un hôte cible
- Détection des erreurs réseau
- Liste des interfaces réseau avec leurs statistiques
- Visualisation des connexions TCP actives
- Interface web responsive avec plusieurs vues :
  - Vue globale
  - Détails par interface
  - Graphiques des métriques

## Stack technique

**Backend**:

- Python 3.x
- FastAPI (serveur web asynchrone)
- Uvicorn (serveur ASGI)
- psutil (collecte des métriques système)
- ping3 (mesure de latence)
- netifaces (détection des interfaces)

**Frontend**:

- Vue.js 3 (Composition API)
- Pinia (state management)
- Vue Router
- ApexCharts (visualisation des données)
- Tailwind CSS (styling)
- Vite (build tool)

## Installation

### Backend

1. Cloner le dépôt :

```bash
git clone https://github.com/RaBYho/network-dashboards.git
cd network-dashboards/backend
```
````

2. Créer un environnement virtuel et installer les dépendances :

```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Frontend

```bash
cd ../frontend/network-dashboard
npm install
```

## Configuration

Le backend utilise les variables d'environnement suivantes (optionnelles) :

```bash
# Exemple de .env
API_HOST=0.0.0.0
API_PORT=8000
DEFAULT_PING_HOST=8.8.8.8
```

## Utilisation

### Lancer le backend

```bash
cd backend
python main.py
# ou en mode développement :
uvicorn main:app --reload
```

### Lancer le frontend

```bash
cd frontend/network-dashboard
npm run dev
```

L'interface sera disponible sur http://localhost:5173

## Structure du projet

```
network-dashboards/
├── backend/          # API FastAPI et collecteurs
│   ├── collectors/   # Modules de collecte des métriques
│   ├── main.py       # Point d'entrée de l'API
│   └── requirements.txt
└── frontend/         # Application Vue.js
    └── network-dashboard/  # Projet Vite
        ├── src/            # Code source
        │   ├── pages/      # Vues de l'application
        │   └── stores/     # State management
        └── package.json    # Dépendances frontend
```

## Contribuer

Les contributions sont les bienvenues. Merci d'ouvrir une issue pour discuter des changements proposés avant de soumettre une pull request.

<!-- Licence : Non spécifiée -->

```

```
