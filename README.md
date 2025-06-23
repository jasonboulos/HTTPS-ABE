# HTTPS Attribute-Based Encryption Demo

Ce dépôt contient un projet minimal illustrant l'utilisation du chiffrement basé sur les attributs (ABE) dans une API HTTPS avec une interface web.

## Structure

- `backend/` – code Python Flask, base de données et logique ABE
- `frontend/` – (non utilisé directement, l'interface se trouve dans `backend/templates`)
- `certs/` – script et fichiers pour générer le certificat auto-signé
- `docs/` – documentation, rapport de fonctionnement

## Installation rapide

Installez d'abord les dépendances Python avec `pip install -r backend/requirements.txt`,
générez ensuite le certificat SSL (`./certs/generate_cert.sh` sous Linux/Mac ou
`bash certs/generate_cert.sh` sous Windows), puis lancez `python backend/app.py`
et ouvrez `https://localhost:5000`.

L'interface permet de créer des attributs, chiffrer des messages et les déchiffrer selon les droits d'accès.
