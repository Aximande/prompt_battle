# Prompt Battle

Une application interactive de génération d'images basée sur des prompts utilisant l'API DALL-E d'OpenAI.

## Aperçu

Prompt Battle est une application web qui permet aux utilisateurs de générer des images à partir de prompts textuels en utilisant l'API DALL-E 3 d'OpenAI. Les utilisateurs peuvent:

- S'identifier avec un pseudo
- Voir une image de référence
- Créer leurs propres images basées sur des prompts textuels
- Visualiser toutes les images générées dans une galerie (format grille ou carrousel)

## Technologies utilisées

- **Frontend**: Streamlit
- **Backend**: Python
- **Base de données**: Firebase
- **Génération d'images**: OpenAI DALL-E 3

## Structure du projet

### Accueil.py
- Page d'accueil qui demande un pseudo à l'utilisateur
- Initialise Firebase
- Permet de naviguer vers la page de prompt

### pages/01_Prompt.py
- Affiche l'image de référence de la session sélectionnée
- Permet à l'utilisateur d'entrer un prompt
- Génère une image avec l'API DALL-E 3 d'OpenAI
- Sauvegarde l'image générée dans Firebase

### pages/02_Galerie.py
- Affiche toutes les images générées pour la session sélectionnée
- Propose deux modes d'affichage: carrousel ou grille
- Permet à l'administrateur (pseudo "lavaleexx") de gérer les sessions

### utils/images_generator.py
- Contient les fonctions pour générer des images via l'API OpenAI
- Inclut une fonction pour sauvegarder les images localement

### auth_firebase/prompt-battle-9b72d-firebase-adminsdk-lhuc9-cc4c55a33e.json
- Fichier de configuration pour l'authentification Firebase

## Déploiement sur Streamlit

Voici comment vous pouvez déployer cette application sur Streamlit Cloud: