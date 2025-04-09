# Projet NAS – BGP/MPLS VPN Automation

## Description du Projet NAS

Ce projet a pour objectif d’automatiser la configuration d’un réseau MPLS avec services **BGP/MPLS VPN** pour plusieurs clients, dans un environnement **GNS3**.  
Nous utilisons les protocols et services suivants :
- **OSPFv2** pour le routage IGP dans le cœur de réseau
- **LDP** pour la distribution des labels MPLS
- **BGP (MP-BGP)** pour l’échange de routes VPN entre routeurs PE
- Le tout en **IPv4**

Ici le réseau supporte 2 clients VPN distincts, isolés grâce à l'utilisation de **VRF**, **Route Distinguisher** et **Route Target**.

---

## Structure du projet

- Fichier d'intention `4routeurs.json`  
- `main.py`  
- `drag_n_drop_bot.py`  
- `fonctions_configuration_ipv4.py`

---

## Prérequis avant d'exécuter main.py

1. Installez Python
2. Clonez le projet grâce à la commande :
```bash
git clone https://github.com/giahg294/NAS_project.git
```
3. Il faut avoir installé le logiciel GNS3 et avoir déjà créé un projet où tous les routeurs ont été créés et connectés entre eux. Pour savoir où placer les routeurs dans le bon ordre et quels interfaces connecter entre elles, adaptez votre réseau au fichier `4routeurs.json`, puis tapez dans le terminal la commande suivante :
```bash
chmod +x drag_and_drop.sh
bash drag_and_drop.sh
```
4. Le fichier `drag_and_drop.bash`, les fichiers de configuration générés ainsi que le dossier `project-files` (créé lors de la génération du projet GNS3) doivent se trouver dans le même répertoire.

---

## Exécution du programme

Exécutez le programme grâce à la commande suivante :
```bash
python3 main.py
```

---

## Auteurs

Hoang Gia, Xu Yafei, Collet Marine, El Moukri Yassmine, Muccini Bianca – Étudiants 5TC, INSA Lyon  
Projet réalisé dans le cadre du module NAS, 2025  
Encadrants : Pierre François et Victor Rébeq