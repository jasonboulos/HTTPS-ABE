# HTTPS ABE Demo Report

Ce rapport décrit brièvement l'implémentation d'un système de chiffrement basé sur les attributs avec une API HTTPS et une interface web.

## Fonctionnement

L'application Flask fournit une interface sécurisée permettant de générer des attributs (paires de clés RSA), de chiffrer des messages selon une politique d'attributs (OR logique) et de déchiffrer les messages si l'utilisateur possède une clé autorisée.

Les données chiffrées et les clés sont stockées dans une base SQLite via SQLAlchemy. Le chiffrement symétrique utilise AES et les clés sont enveloppées avec RSA (module `cryptography`).

## Lancement du projet

```bash
# Installation des dépendances
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Génération du certificat auto-signé
./certs/generate_cert.sh

# Lancement du serveur
python backend/app.py
```

Ouvrir ensuite https://localhost:5000 dans un navigateur (ignorer l'avertissement de certificat).
