# network-dashboards

Un tableau de bord réseau utilisant Flask et Vue.js pour visualiser les métriques réseau.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Stack technique](#stack-technique)
- [Installation](#installation)
- [Structure du projet](#structure-du-projet)
- [Contribuer](#contribuer)

## Fonctionnalités

- Collecte des métriques de bande passante
- Collecte des métriques de latence
- Visualisation des données réseau via une interface web

## Stack technique

- Backend : Python avec Flask
- Frontend : Vue.js
- Collecteurs Python pour les métriques réseau

## Installation

1. Clonez le dépôt :

```bash
git clone https://github.com/RaBYho/network-dashboards
cd network-dashboards
```

2. Installez les dépendances backend :

```bash
cd backend
pip install -r requirements.txt
```

3. Installez les dépendances frontend :

```bash
cd ../frontend/network-dashboard
npm install
```

## Structure du projet

```
network-dashboards/
├── backend/
│   ├── collectors/          # Modules de collecte des données
│   ├── bandwith_collector.py # Collecteur de bande passante
│   └── latency_collector.py  # Collecteur de latence
├── frontend/
│   └── network-dashboard/   # Application Vue.js
├── .gitignore
└── README.md
```

## Contribuer

Les contributions sont les bienvenues. Merci d'ouvrir une issue pour discuter des changements proposés avant de soumettre une pull request.

<!-- À compléter : ajouter des instructions plus détaillées pour le lancement du projet -->
