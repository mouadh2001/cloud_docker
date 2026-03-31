# Mini-Projet Cloud

Ce projet est un exemple complet pour réaliser une plateforme microservices avec Docker et Docker Compose.

## Ce que contient le projet

- `app/` : microservice Flask TODO avec PostgreSQL et Redis
- `docker-compose.yml` : orchestration des services
- `nginx/default.conf` : reverse proxy Nginx
- `prometheus/prometheus.yml` : configuration Prometheus
- `.github/workflows/ci-cd.yml` : pipeline GitHub Actions pour build, push et déploiement

## Installation requise

Sur Ubuntu VM, vous n'avez pas besoin de Docker Desktop. Suivez ces étapes :

1. Ouvrir un terminal.
2. Mettre à jour les paquets :
   ```bash
   sudo apt update
   sudo apt install -y ca-certificates curl gnupg lsb-release
   ```
3. Ajouter la clé Docker et le dépôt officiel :
   ```bash
   sudo mkdir -p /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt update
   ```
4. Installer Docker Engine et Docker Compose plugin :
   ```bash
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
   sudo systemctl enable --now docker
   ```
5. Autoriser votre utilisateur à exécuter Docker sans `sudo` (optionnel) :
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

## Exécuter le projet localement

1. Ouvrir un terminal dans le dossier du projet.
2. Construire et lancer les services :
   ```bash
   docker compose up --build -d
   ```
   Si vous n'avez pas ajouté votre utilisateur au groupe `docker`, utilisez :
   ```bash
   sudo docker compose up --build -d
   ```
3. Vérifier que les services sont démarrés :
   - API : http://localhost
   - cAdvisor : http://localhost:8080
   - Prometheus : http://localhost:9090
   - Grafana : http://localhost:3000

> Si vous utilisez une VM distante, remplacez `localhost` par l'adresse IP de la VM dans votre navigateur ou utilisez un tunnel SSH/port forwarding.

## Dépannage Ubuntu

Si `docker compose up --build -d` échoue, exécutez :

```bash
docker pull python:3.11-slim
sudo docker compose build --no-cache --progress=plain app
sudo docker compose up --build -d
```

Si le build du service app échoue encore, copiez les messages d'erreur complets concernant `pip` ou `python`.

## API TODO

- `GET /tasks` : liste des tâches
- `POST /tasks` : ajoute une tâche
- `DELETE /tasks/<id>` : supprime une tâche

### Tester avec `curl`

```powershell
curl -X POST http://localhost/tasks -H "Content-Type: application/json" -d '{"title":"Test", "description":"Faire le TP"}'
curl http://localhost/tasks
curl -X DELETE http://localhost/tasks/1
```

## Explication rapide

- `app` : service Flask avec PostgreSQL et Redis.
- `db` : PostgreSQL, données persistantes via volume Docker.
- `redis` : cache et compteur de visites.
- `nginx` : proxy inverse, expose l'application.
- `cadvisor` + `prometheus` + `grafana` : monitoring des conteneurs.

## Ajouter HTTPS

Pour la partie HTTPS, vous pouvez générer un certificat et monter `nginx/certs` dans Nginx, ou utiliser un reverse proxy extérieur. Le projet fonctionne déjà en HTTP.

## CI/CD GitHub Actions

1. Créer un dépôt GitHub.
2. Ajouter `DOCKERHUB_USERNAME` et `DOCKERHUB_TOKEN` dans les secrets GitHub.
3. Pousser le code sur `main`.

## Déploiement sur un cloud (Azure)

1. Installer Azure CLI.
2. Se connecter : `az login`.
3. Pousser l'image Docker sur Docker Hub.
4. Créer un groupe de ressources et un conteneur Azure avec l'image Docker.

> Ce guide est conçu pour suivre les étapes une à une. Copie-colle les commandes et prends le temps de lire chaque section.
