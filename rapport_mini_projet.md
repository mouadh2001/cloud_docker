# Rapport du mini-projet

## 1. Introduction

Ce mini-projet a pour but de présenter une plateforme de gestion de tâches déployée avec Docker Compose et une architecture microservices. L’application est volontairement simple, mais elle intègre plusieurs services importants : un backend Flask, une base de données PostgreSQL, un cache Redis, un reverse proxy Nginx et un ensemble d’outils de monitoring (cAdvisor, Prometheus, Grafana). Ce rapport explique les choix techniques, l’implémentation, les tests, les difficultés rencontrées et les améliorations possibles.

Le contexte de départ est un projet d’informatique orienté cloud. L’idée est de proposer une solution qui fonctionne sur une machine Ubuntu sans dépendre de Docker Desktop. Le dossier du projet contient la configuration nécessaire pour lancer toute la stack via `docker compose up --build -d`.

## 2. Objectifs du projet

Les objectifs principaux sont :

- Créer une API REST pour gérer des tâches.
- Utiliser PostgreSQL pour persister les données.
- Ajouter un cache Redis afin d’améliorer les performances de lecture.
- Exposer l’application via Nginx.
- Surveiller les conteneurs avec Prometheus et Grafana.
- Préparer une configuration simple et réutilisable pour Ubuntu.

Ces objectifs permettent de couvrir plusieurs aspects d’un projet cloud : développement backend, conteneurisation, orchestration, stockage persistant et supervision.

## 3. Architecture technique

L’architecture repose sur Docker Compose avec les services suivants :

- `app` : le microservice Flask qui gère les tâches.
- `db` : PostgreSQL comme base de données relationnelle.
- `redis` : serveur de cache.
- `nginx` : reverse proxy pour router les requêtes HTTP.
- `cadvisor` : collecte d’informations sur les conteneurs.
- `prometheus` : collecte des métriques.
- `grafana` : interface de visualisation des métriques.

Ces services sont connectés via un réseau Docker nommé `web`. Les volumes `db-data` et `prometheus-data` permettent de conserver les données entre les redémarrages. La configuration est centralisée dans `docker-compose.yml`, qui définit également les ports exposés : 80 pour l’application, 8080 pour cAdvisor, 9090 pour Prometheus et 3000 pour Grafana.

### 3.1 Service `app`

Le service `app` est le composant principal. Il est construit à partir du répertoire `app/` grâce à un `Dockerfile`. Ce Dockerfile installe Python 3.11, les dépendances système nécessaires et les bibliothèques Python listées dans `requirements.txt`.

La logique de l’application est la suivante :

- Une connexion à PostgreSQL via SQLAlchemy.
- Une connexion à Redis pour stocker un cache de la liste des tâches et un compteur de visites.
- Un modèle `Task` qui représente les tâches dans la base de données.
- Trois endpoints :
  - `GET /tasks` pour lister les tâches et retourner le nombre de consultations.
  - `POST /tasks` pour créer une nouvelle tâche.
  - `DELETE /tasks/<id>` pour supprimer une tâche.

Le service utilise Gunicorn pour démarrer le serveur d’application, ce qui est adapté pour une production légère.

### 3.2 Service `db`

Le service `db` est basé sur l’image `postgres:14`. Il fournit un stockage persistant via le volume Docker `db-data`. Les variables d’environnement définissent les identifiants de connexion et le nom de la base.

### 3.3 Service `redis`

Redis est utilisé comme cache simple. Il stocke :

- `tasks_cache` : la liste JSON des tâches.
- `tasks_visit_count` : un compteur du nombre de fois où l’endpoint `/tasks` a été appelé.

L’utilisation de Redis permet de réduire les accès directs à la base de données pour les requêtes de lecture fréquentes.

### 3.4 Service `nginx`

Nginx fait office de reverse proxy. Il expose le port 80 et redirige les requêtes HTTP vers le service `app`. Cela isole le service applicatif du réseau externe et permet de préparer une architecture plus proche de la production.

### 3.5 Monitoring

Le projet inclut également une chaîne de monitoring :

- `cadvisor` collecte les métriques des conteneurs Docker.
- `prometheus` récupère ces métriques et les stocke.
- `grafana` affiche les données sous forme de tableaux de bord.

Cette partie n’est pas indispensable au fonctionnement de l’application, mais elle permet de démontrer une bonne pratique en cloud : surveiller l’infrastructure et les performances.

## 4. Implémentation détaillée

### 4.1 Dockerfile de l’application

Le Dockerfile commence par l’image `python:3.11-slim`. Les étapes suivantes sont :

1. Définir le répertoire de travail sur `/app`.
2. Installer les paquets système nécessaires pour compiler des dépendances Python (`build-essential`, `gcc`, `libpq-dev`).
3. Copier `requirements.txt` et installer les dépendances Python.
4. Copier le fichier `app.py`.
5. Exposer le port 5000 et démarrer Gunicorn.

Ceci garantit que l’application est construite de manière propre et qu’elle contient tous les outils nécessaires sur Ubuntu.

### 4.2 Dépendances Python

Le fichier `requirements.txt` contient les bibliothèques suivantes :

- Flask : framework web.
- Flask-SQLAlchemy : ORM pour PostgreSQL.
- psycopg2-binary : driver PostgreSQL.
- redis : client Redis.
- gunicorn : serveur WSGI.

Ces dépendances sont classiques pour un service backend Python.

### 4.3 Code de l’API

Le code de `app.py` est construit autour de Flask. Les points clés sont :

- Configuration dynamique via variables d’environnement.
- Un modèle `Task` simple avec `id`, `title`, `description` et `created_at`.
- Une initialisation de la base de données avant la première requête.
- Gestion du cache Redis pour accélérer `GET /tasks`.
- Validation de la requête JSON dans `POST /tasks`.
- Retour d’un message explicite en cas d’erreur de suppression.

Ce code montre une approche pragmatique et adaptée à un petit projet.

## 5. Mise en place sur Ubuntu

Pour faire fonctionner le projet sur une machine Ubuntu, les étapes suivantes sont nécessaires :

1. Installer Docker et le plugin Docker Compose.
2. Vérifier que le service Docker tourne.
3. Se placer dans le dossier du projet où se trouve `docker-compose.yml`.
4. Lancer la stack avec `docker compose up --build -d`.

La documentation du projet précise également comment installer Docker sur Ubuntu en ajoutant le dépôt officiel et en activant le service.

### 5.1 Commandes de base

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
```

Et pour démarrer le projet :

```bash
docker compose up --build -d
```

Si l’utilisateur n’est pas dans le groupe Docker :

```bash
sudo docker compose up --build -d
```

## 6. Tests et vérifications

Une fois la stack démarrée, il faut vérifier que chaque service fonctionne. Les tests principaux sont :

- Accéder à l’API via `http://localhost/tasks`.
- Envoyer une requête POST pour créer une tâche.
- Supprimer une tâche avec DELETE.
- Vérifier les ports Nginx, cAdvisor, Prometheus et Grafana.

Pour tester l’API, on peut utiliser `curl` :

```bash
curl -X POST http://localhost/tasks -H "Content-Type: application/json" -d '{"title":"Test", "description":"Vérifier l API"}'
curl http://localhost/tasks
curl -X DELETE http://localhost/tasks/1
```

Ces commandes permettent de s’assurer que l’application, la base de données et Redis sont bien connectés.

## 7. Difficultés rencontrées

Plusieurs points peuvent poser problème lors de l’exécution :

- Le build Docker qui échoue si les dépendances système ne sont pas installées.
- Le téléchargement de l’image Python depuis Docker Hub si la connexion réseau est instable.
- Les variables d’environnement mal configurées pour PostgreSQL ou Redis.
- Le fait de ne pas exécuter Docker avec les droits suffisants.

Ces difficultés ont été résolues en adaptant le Dockerfile à Ubuntu et en documentant clairement les commandes d’installation.

## 8. Améliorations possibles

Ce projet peut être amélioré de plusieurs façons :

- Ajouter une interface web côté frontend.
- Protéger l’API avec une authentification.
- Ajouter la gestion des mises à jour de tâches.
- Ajouter des tests automatisés pour l’API.
- Mettre en place un certificat HTTPS pour Nginx.
- Déployer la stack sur un cloud public.

Ces extensions permettraient de transformer un mini-projet en une application plus complète.

## 9. Conclusion

Ce mini-projet démontre la construction d’une application cloud simple et moderne. Il combine des technologies bien choisies : Flask pour le backend, PostgreSQL pour le stockage relationnel, Redis pour le cache, Docker pour la conteneurisation et Prometheus/Grafana pour le monitoring.

L’ensemble est pensé pour être lancé facilement sur Ubuntu, avec un fichier `docker-compose.yml` central gérant tous les services. Le projet montre aussi l’importance de l’orchestration et de la surveillance dans une architecture microservices.

Au final, ce travail permet de comprendre comment assembler plusieurs composants Docker et de produire une plateforme fonctionnelle qui peut évoluer vers un projet plus complet.
