# Explication du projet

Ce mini-projet est une plateforme de gestion de tâches construite avec une architecture microservices. L’objectif était de créer une application simple mais complète, qui montre comment des composants comme une API Flask, une base de données PostgreSQL, un cache Redis et un reverse proxy Nginx peuvent fonctionner ensemble dans des conteneurs Docker.

Le cœur du projet est le service `app`, développé avec Flask. Cette API permet de lister des tâches, d’en ajouter et d’en supprimer. Les tâches sont stockées dans PostgreSQL, ce qui permet de conserver les données même si le conteneur est redémarré. Redis est utilisé pour stocker un cache temporaire et un compteur de visites, ce qui améliore la performance de la lecture des tâches.

L’architecture du projet repose sur Docker Compose. La configuration de `docker-compose.yml` décrit plusieurs services : `app`, `db`, `redis`, `nginx`, `cadvisor`, `prometheus` et `grafana`. Chaque service a son rôle :

- `app` exécute le microservice Python/Flask.
- `db` apporte la base de données PostgreSQL.
- `redis` gère le cache.
- `nginx` fait le proxy inverse et expose l’application sur le port 80.
- `cadvisor`, `prometheus` et `grafana` forment la chaîne de monitoring.

Dans le code, la logique de l’API est volontairement simple. On initialise la base de données la première fois que l’application reçoit une requête. La route `GET /tasks` renvoie les tâches et un nombre de visites enregistré par Redis. La route `POST /tasks` crée une nouvelle tâche, et `DELETE /tasks/<id>` supprime une tâche spécifique. Ce schéma est efficace pour un petit projet et démontre bien la communication entre Flask, PostgreSQL et Redis.

Le Dockerfile du service `app` est conçu pour fonctionner sur une machine Ubuntu. Il utilise l’image `python:3.11-slim`, installe les outils de compilation nécessaires (`build-essential`, `gcc`, `libpq-dev`) puis installe les dépendances Python depuis `requirements.txt`. Un serveur Gunicorn est lancé à la fin, ce qui améliore la stabilité de l’application en production par rapport au serveur de développement Flask.

Le choix de Nginx pour le reverse proxy est utile même sur un petit projet. Il permet de séparer l’accès HTTP du service applicatif et de placer une couche intermédiaire entre les utilisateurs et le microservice. De plus, Nginx rend le déploiement plus réaliste pour un projet cloud.

Enfin, la présence de Prometheus et Grafana montre un aspect important du cloud : le monitoring. Prometheus récupère des métriques de cAdvisor pour observer l’utilisation CPU, mémoire et réseau des conteneurs. Grafana peut ensuite afficher ces métriques via un tableau de bord. Cette partie est un plus qui complète le projet en ajoutant de la visibilité sur le comportement de l’application.

En résumé, ce projet illustre une petite application de gestion de tâches dans un environnement conteneurisé. Il met en œuvre plusieurs technologies adaptées au cloud et à la supervision, tout en restant simple à exécuter et à comprendre.
