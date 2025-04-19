# MirroCast 🎥🖥️📺

**MirroCast** est une application full-stack auto-hébergée de diffusion multimédia et de partage d'écran en temps réel depuis un PC vers un téléviseur LG WebOS.  
Ce projet vise à offrir une expérience fluide de type Plex, combinée à une fonctionnalité de mirroring écran à faible latence, le tout via un serveur local.

---

## 🚀 Fonctionnalités

- **Streaming multimédia** (films, vidéos, photos) via interface web moderne
- **Mirroring en temps réel** de l'écran PC (1080p@60fps)
- **Application native LG WebOS** pour recevoir les flux
- **Encodage GPU** (NVENC / VAAPI) et streaming HLS ou WebRTC
- **Interface web responsive** (React / Vue 3)
- **Déploiement Dockerisé** compatible CI/CD (GitHub Actions)

---

## 📦 Technologies utilisées

| Composant     | Technologie              |
|---------------|--------------------------|
| Backend       | FastAPI, Uvicorn         |
| Frontend      | React / Vue 3 (SPA)      |
| Streaming     | FFmpeg, PyAV, WebRTC     |
| DB            | PostgreSQL + SQLAlchemy  |
| DevOps        | Docker, GitHub Actions   |
| Monitoring    | Prometheus + Grafana     |

---

## 🛠️ Démarrage rapide (Dev)

```bash
# Cloner le dépôt
git clone https://github.com/antoine-granger/MirroCast.git
cd MirroCast

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # sous Linux/macOS
.venv\Scripts\activate     # sous Windows

# Installer les dépendances
pip install -r requirements.txt
winget install "FFmpeg (Essentials Build)"

# Lancer le serveur backend
uvicorn main:app --reload
```

## 🌐 Accès au projet
* Serveur local : http://localhost:8000
* Documentation API (Swagger) : http://localhost:8000/docs

## 📂 Structure du projet
```bash
MirroCast/
├── api/                 # Backend FastAPI
│   ├── app.py
│   ├── __init__.py
│   └── ...
├── frontend/            # SPA React/Vue (à venir)
├── webos-app/           # Client LG WebOS (à venir)
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🔐 Sécurité
* Authentification via JWT (à venir)
* HTTPS supporté via proxy (Nginx / Traefik)
* Scans de vulnérabilités via GitHub Actions

## 📈 Roadmap
*  ✅Serveur FastAPI opérationnel
*  ❌Streaming HLS avec FFmpeg
*  ❌Mirroring via WebRTC
*  ❌Intégration WebOS SDK
*  ❌CI/CD & monitoring Prometheus

## 🧑‍💻 Auteur
Développé par Antoine Granger

## 📄 Licence
Ce projet est distribué sous licence MIT.
````yaml
