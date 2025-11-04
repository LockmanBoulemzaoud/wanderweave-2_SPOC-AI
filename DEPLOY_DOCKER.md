# Déployer l'application complète avec Docker (Option A)

Ce guide explique comment construire localement une image Docker qui contient l'API FastAPI et l'UI Streamlit et comment la déployer sur une plateforme qui accepte des conteneurs (Render, Fly.io, Railway, Docker Hub + cloud provider...).

Prérequis (côté développeur)
- Docker installé localement (Docker Desktop sur macOS).
- Accès à un service d'hébergement de conteneurs (Render, Fly.io, Railway, ou capacité à pousser l'image sur Docker Hub / GitHub Container Registry et déployer depuis là).
- (Optionnel) compte Git connecté à la plateforme de déploiement.

Commandes utiles locales

1) Construire l'image localement (depuis le répertoire racine du repo) :

```bash
# construire
docker build -t wanderweave-full:latest .

# lancer localement (redirige le port 8080 du container vers 8080 local)
docker run --rm -p 8080:8080 wanderweave-full:latest
```

2) Accéder à l'application
- Ouvre http://localhost:8080/ -> Streamlit UI
- Les appels API sont disponibles via http://localhost:8080/api/...

Déployer sur Render (exemple rapide)
1. Crée un nouveau service Web « Private Service » ou « Web Service » sur Render.
2. Connecte ton dépôt GitHub/GitLab.
3. Choisis la branche à déployer (ex: main).
4. Configure le service pour utiliser Docker (Render détecte automatiquement si Dockerfile est présent).
5. Set le port health check / service port à 8080 (Render passera $PORT mais le Dockerfile écoute 8080 — tu peux configurer Render pour utiliser le port 8080 ou adapter).
6. Deploy.

Remarques & debugging
- Si tu préfères que l'image écoute dynamiquement sur la variable $PORT fournie par la plateforme, modifie le  `docker/nginx.conf` pour utiliser une variable ou utilise un petit script d'entrée qui écrit le config nginx au runtime.
- Les images créées depuis `python:slim` peuvent nécessiter des bibliothèques système pour des paquets Python (pandas, numpy). Le Dockerfile installe quelques dépendances (build-essential, libopenblas, ...). Si l'installation pip échoue, regarde les logs de build pour ajouter les paquets système manquants.
- Pour garder l'image plus légère, on peut construire une image multi-stage ou utiliser des wheels préconstruits.

Si tu veux, je peux:
- Construire et tester l'image localement ici (si tu veux que j'exécute docker build/run),
- Ou créer une branche `deploy-docker` et committer ces fichiers pour que tu puisses déclencher un déploiement automatique sur Render.
