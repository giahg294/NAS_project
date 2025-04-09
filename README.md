# Projet NAS – BGP/MPLS VPN Automation

## Description du Projet NAS

Ce projet vise à automatiser la configuration d’un réseau **IPv4 BGP/MPLS VPN** dans **GNS3**, en s’appuyant sur un fichier d’intention décrivant les AS, routeurs, interfaces, protocoles et VRFs.  
Le réseau met en place une architecture **provider / clients** avec **2 clients VPN distincts**, isolés via VRF.

Les services réseau sont configurés automatiquement à l’aide de :
- **OSPFv2** pour le routage IGP interne,
- **LDP** pour activer le transport MPLS,
- **MP-BGP (vpnv4)** entre routeurs PE.

---

## Structure du projet

- `4routeurs.json` 
Fichier d’intention décrivant la topologie réseau.   
Pour chaque AS : les routeurs, leur rôle (PE, P, CE, C), les vrfs, les interfaces, les voisins et les plages d’adresses IPv4 (interfaces et loopbacks).  
Pour l’environnement inter-AS : les connexions entre routeurs de différents AS et les plages d’adresses IPv4 utilisées.

- `main.py` 
Génère automatiquement la configuration IPv4 complète pour chaque routeur :  
Entête de config, interfaces, loopbacks  
OSPF, LDP, MP-BGP, VRFs clients  
Fichier prêt à être injecté dans GNS3  
- `drag_n_drop_bot.py`  
Script Python qui déplace automatiquement les fichiers de configuration dans les bons répertoires GNS3 (via `project-files/dynamips/...`), en fonction d’un mapping des routeurs.
- `fonctions_configuration_ipv4.py`
Script Bash qui cherche et place les fichiers `iX_startup-config.cfg` dans les bons répertoires. À utiliser après génération des configs pour les injecter dans GNS3.

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