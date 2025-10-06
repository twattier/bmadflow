# BMADFlow

# Description
La DSI veut une solution pour explorer et visualiser la documentation générée pour chaque projet avec Claude Code et le framework BMAD Method.
Avec un chatbot pour interroger le contenu de chaque projet.

# Objectifs
C'est un POC publié en public sur github, et n'a pas vocation a etre commercialisé
- Centraliser la documentation pour les projets gérés
- chatbot agent IA pour rechercher les information projets

# Fonctionnalités

## Gestion des projets 
 - Dashboard + Liste des projets existants
 - Créer un projet
 - Voir un projet    
    - chatbot pour interroger le contenu de la documentation
    - voir les ProjetDocs et permettre de les selectionner pour les explorer
    - gerer la configuration (nom, description, liste ProjetDocs), un Projet est configuré pour faire référence a 1 ou plusieurs ProjetDocs (nom, desc, lien github)

## Synchronization de la doc
Depuis un ProjetDocs selectionné
 - importation manuelle à la demande (afficher les dates : derniere synchro / dernier commit github sur ce repertoire) 
 - scan et importe dans la base de données les fichiers dans tous les formats de texte (md, csv, yaml, txt, json, ...)

## Exploration du la doc
Depuis un projet selectionné : explore le contenu de la documentation et visualise les fichiers
Similaire à ce que propose github, optimisé surtout pour afficher du markdown
 - Affiche l'arborescence et permet de selectionner un fichier
 - Affiche le contenu du fichier
    - markdown : soigner l'affichage + graphique mermaid
    - csv : afficher sous forme de tableau
    - autre fichier texte : 
 - Assurer le fonctionnement des liens entre les documents markdown (liens relatifs)

## base de connaissance RAG
Depuis un ProjetDocs selectionné, dont les fichiers textes ont été importé
- pipeline optimisé pour alimenter une base pgvector de facon intelligente : Serialization, hybrid Chunking

## Chatbot RAG
Depuis un Projet, afficher une interaction chatbot avec un agent qui dispose d'un outil pour interroger la base de connaissance
- voir les anciennes conversations, lancer une nouvelle conversation
- peut choisir un model LLM parmis ceux disponibles (config globale)
- en interrogeant la base de connaissance (par défaut), répond au mieux en donnant les liens vers les documents sources utilisés

## Configuration globale
Listes des models LLM:
- Voir et ajouter un model (openAI, Gemini, LiteLLM, Ollama)

# Stack technique
- monorepo sur github
- backend : 
    - server : fastapi
    - RAG : docling 
    - agentic : pydantic
    - base de données / vecteur : pgvector