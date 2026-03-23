# 🔬 AirLab France

> Plateforme de monitoring temps réel de la qualité de l'air et des données météorologiques en France.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green.svg)](https://supabase.com)
[![Railway](https://img.shields.io/badge/Deploy-Railway-blueviolet.svg)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌐 Accès au dashboard

🔗 **[https://airlabfrance-production.up.railway.app](https://airlabfrance-production.up.railway.app)**

> ⚠️ **Accès sur autorisation uniquement** — Un mot de passe est requis.
> Contactez l'administrateur pour obtenir l'accès.

> 💡 **Recommandation d'affichage** : Utilisez votre navigateur en **mode clair (Light Mode)**
> pour une meilleure lisibilité du dashboard. Le mode sombre (Dark Mode) peut réduire
> le contraste et rendre certains éléments difficiles à lire.
>
> **Comment activer le mode clair :**
> - **Chrome** : Paramètres → Apparence → Thème → Clair
> - **Firefox** : Paramètres → Général → Gestion des couleurs → Clair
> - **Safari** : Préférences Système → Apparence → Clair
> - **Edge** : Paramètres → Apparence → Thème → Clair

---

## 📋 Présentation

**AirLab France** est une plateforme de monitoring développée pour **GoodAir**, permettant de visualiser en temps réel la qualité de l'air et les données météorologiques dans les principales villes françaises.

Le projet agrège deux sources de données :
- **AQICN** — World Air Quality Index (AQI, PM2.5, PM10, O3, NO2)
- **Open-Meteo** — Données météo open source (température, humidité, vent, pression)

Les données sont collectées automatiquement chaque jour à **16h00**, stockées dans une base **Supabase** (hébergée en Europe — conforme RGPD), et exposées via un dashboard **Streamlit** interactif.

---

## ✨ Fonctionnalités

- 📊 **Vue globale** — KPIs AQI par ville + carte France interactive
- 📈 **Évolution AQI** — Historique des polluants sur 1 à 30 jours
- 🔗 **Corrélations** — Relations entre météo et qualité de l'air
- 🚨 **Alertes** — Dépassements automatiques des seuils OMS
- 📖 **Indicateurs** — Guide complet des polluants et leur signification
- 🔐 **Accès sécurisé** — Authentification par mot de passe
- 🔄 **Collecte automatique** — Pipeline ETL complet chaque jour à 16h00

---

## 🏙️ Villes couvertes

| Ville | Latitude | Longitude |
|-------|----------|-----------|
| Paris | 48.8566 | 2.3522 |
| Lyon | 45.7640 | 4.8357 |
| Marseille | 43.2965 | 5.3698 |
| Bordeaux | 44.8378 | -0.5792 |
| Lille | 50.6292 | 3.0573 |

---

## 🗂️ Structure du projet

```
AirLab_France/
├── app.py              # Dashboard Streamlit (5 pages + authentification)
├── ingest.py           # Pipeline ETL — Extract / Validate / Clean / Enrich / Load
├── requirements.txt    # Dépendances Python
├── railway.toml        # Configuration déploiement Railway
├── Dockerfile          # Image Docker
├── .gitignore          # Fichiers exclus de Git
└── .env.example        # Template variables d'environnement
```

---

## ⚙️ Pipeline de données

Le script `ingest.py` suit un pipeline en 5 étapes :

| Étape | Description |
|-------|-------------|
| **Extract** | Appelle les APIs AQICN et Open-Meteo pour les 5 villes |
| **Validate** | Vérifie la cohérence des valeurs (AQI 0-500, temp -50/+60°C...) |
| **Clean** | Gère les valeurs nulles, arrondit, normalise les textes |
| **Enrich** | Ajoute `aqi_label`, `is_alert`, `weather_label` |
| **Load** | Insère dans Supabase + écrit dans `logs/ingest.log` |

---

## 🚀 Installation locale

### Prérequis
- Python 3.11+
- Clé API [AQICN](https://aqicn.org/data-platform/token/)
- Compte [Supabase](https://supabase.com) gratuit

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/ton-user/AirLab_France.git
cd AirLab_France

# 2. Environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate

# 3. Dépendances
pip install -r requirements.txt

# 4. Variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés
```

### Configuration `.env`

```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=sb_secret_xxx
AQICN_TOKEN=ton_token_aqicn
APP_PASSWORD=tonMotDePasse
```

### Lancement

```bash
# Collecte des données (premier lancement)
python ingest.py

# Dashboard
streamlit run app.py
```

---

## 🐳 Déploiement Docker

```bash
docker build -t airlab-france .
docker run -p 8501:8501 --env-file .env airlab-france
```

---

## 🗄️ Base de données Supabase

Deux tables créées via SQL Editor :

```sql
CREATE TABLE IF NOT EXISTS air_quality (
    id           BIGSERIAL PRIMARY KEY,
    ts           TIMESTAMPTZ DEFAULT NOW(),
    city         TEXT,
    aqi          INTEGER,
    pm25         FLOAT,
    pm10         FLOAT,
    o3           FLOAT,
    no2          FLOAT,
    dominant_pol TEXT,
    aqi_label    TEXT,
    is_alert     BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS weather (
    id            BIGSERIAL PRIMARY KEY,
    ts            TIMESTAMPTZ DEFAULT NOW(),
    city          TEXT,
    temperature   FLOAT,
    humidity      INTEGER,
    wind_speed    FLOAT,
    precipitation FLOAT,
    pressure      FLOAT,
    weather_code  INTEGER,
    weather_label TEXT
);
```

---

## 🔒 Sécurité & RGPD

- Accès au dashboard protégé par mot de passe
- Aucune donnée personnelle collectée
- Données stockées sur Supabase **Europe West (Frankfurt)** — conforme RGPD
- Clés API exclusivement dans les variables d'environnement Railway (jamais sur GitHub)
- Repo GitHub en mode **privé**

---

## 📅 Collecte automatique

La collecte tourne automatiquement chaque jour à **16h00** via Railway Cron :

```
0 16 * * *  →  python ingest.py
```

Logs disponibles dans `logs/ingest.log` sur le serveur Railway.

---

## 🗺️ Roadmap

- [x] **V1 — MVP** : Dashboard 5 villes, pipeline ETL, alertes seuils OMS
- [ ] **V2** : Couverture nationale, alertes email, export CSV
- [ ] **V3** : Modèles prédictifs (canicules, saisonnalité AQI)
- [ ] **V4** : API REST publique pour les chercheurs GoodAir

---


*Développé par Samir AIT-ATMANE* 🇫🇷