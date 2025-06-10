# Projet NAS – BGP/MPLS VPN Automation

## Description du Projet NAS

Ce projet vise à automatiser la configuration d’un réseau **IPv4 BGP/MPLS VPN** dans **GNS3**, en s’appuyant sur un fichier d’intention décrivant les AS, routeurs, interfaces, protocoles et VRFs.  
Le réseau met en place une architecture **provider / clients** avec **3 clients VPN distincts**, isolés via VRF.

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
  Le champ "all_clients" de chaque AS permet de préciser quels sont les AS auxquels chaque client peut accéder (à adapter pour du VPN sharing).

- `main.py`
  Génère automatiquement la configuration IPv4 complète pour chaque routeur :  
  Entête de config, interfaces, loopbacks  
  OSPF, LDP, MP-BGP, VRFs clients  
  Fichier prêt à être injecté dans GNS3
- `drag_and_drop_bot.sh`  
  Script qui déplace automatiquement les fichiers de configuration dans les bons répertoires GNS3
  - `address_allocator.py`
    Script qui crée les classes routeur et AS et qui notamment configure automatiquement les addresses ipv4 des routeurs à partir de la plage attribuée à chaque AS
- `fonctions_configuration_ipv4.py`
  Script qui modifie les fichiers de configuration de chaque routeur et qui configure notamment les interfaces adaptées, les VRF, l'IGP et BGP

---

## Prérequis avant d'exécuter main.py

1. Installez Python
2. Clonez le projet grâce à la commande :

```bash
git clone https://github.com/giahg294/NAS_project.git
```

3. Il faut avoir installé le logiciel GNS3 et avoir déjà créé un projet où tous les routeurs ont été créés et connectés entre eux. Pour savoir où placer les routeurs dans le bon ordre et quels interfaces connecter entre elles, adaptez votre réseau au fichier `4routeurs.json`.

4. Le fichier `drag_and_drop.bash`, les fichiers de configuration générés ainsi que le dossier `project-files` (créé lors de la génération du projet GNS3) doivent se trouver dans le même répertoire.

---

## Exécution du programme

Exécutez le programme grâce aux commandes suivantes :

```bash
python3 main.py
./drag_and_drop.sh
```

---

## Auteurs

Hoang Gia, Xu Yafei, Collet Marine, El Moukri Yassmine, Muccini Bianca – Étudiants 5TC, INSA Lyon  
Projet réalisé dans le cadre du module NAS, 2025  
Encadrants : Pierre François et Victor Rébeq
