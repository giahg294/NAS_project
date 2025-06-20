import json 
import os 
from address_allocator import * 
from fonctions_configuration_ipv4 import *

def create_folder(name):
    # Vérifier si le dossier 'projet-files' existe déjà
    folder_name = name
    if not os.path.exists(folder_name):
        # Créer le dossier
        os.makedirs(folder_name)
        print(f"Dossier '{folder_name}' créé avec succès.")
    else:
        print(f"Le dossier '{folder_name}' existe déjà.")
        

if __name__ == "__main__":

    with open('4routers.json', 'r') as file:
        data = json.load(file)

    # Extraire les informations AS du JSON, créer des instances de la classe AS, les stocker dans la liste all_as
    all_as = [AS(as_info['number'], as_info['IP_range'], as_info['loopback_range'], as_info['border_range'], as_info['protocol'], as_info['all_clients'], as_info['routers'], as_info['relation'])
              for as_info in data["AS"]]

    all_as_dict = generate_as_dict(all_as)
    # Créer un dictionnaire as_mapping pour stocker le numéro AS auquel chaque routeur appartient
    as_mapping = {}
    for as_index in all_as: 
        for router in as_index.routers:  
            as_mapping[router.name] = as_index.number  # Mapper le nom du routeur au numéro de l'AS auquel il appartient


    # Créer une liste contenant tous les routeurs
    all_routers = [router for as_index in all_as for router in as_index.routers]
    
    connections_matrix = generate_connections_matrix(all_routers, as_mapping)
    routers_info = generate_routers_dict(all_as, connections_matrix)

    direct_neighbor_dico = generate_direct_neighbor(all_routers, as_mapping)
    # Définir une liste vide pour stocker tous les fichiers source générés
    source_file = []

    # Parcourir tous les AS et les routeurs dans chaque AS pour générer les adresses des interfaces pour chaque routeur
    for as_index in all_as:
        generate_interface_addresses(as_index, connections_matrix)

    fichiers_config = []
    # Parcourir tous les AS et les routeurs dans chaque AS pour générer les fichiers de configuration pour chaque routeur
    for as_index in all_as:
        for router in as_index.routers:
            #print(f"{router.name}:{router.interfaces}")
            # Générer l'adresse loopback du routeur
            # Générer l'ID du routeur
            router_id = generate_router_id(router.name)
            config = []  # Créer une liste vide pour la configuration
            # Ajouter successivement les configurations de l'en-tête, loopback, interfaces, BGP et de fin

            config.extend(config_head(router.name, router.router_type, as_index.all_clients, router.vrf, as_index.number))
            config.extend(config_loopback(routers_info[router.name]["loopback"], as_index.protocol, router.router_type))
            config.extend(config_interface(router.interfaces, as_index.protocol, router.router_type))
            config.extend(config_bgp(as_index.protocol, all_routers, router, router_id, routers_info, direct_neighbor_dico))
            config.extend(config_end(as_index.protocol, router_id))
            
            # Écrire la configuration dans un fichier
            with open(f"i{router.name[1:]}_startup-config.cfg", 'w') as file:
                file.write('\n'.join(config))  # Écrire le contenu de la configuration
                source_file.append(f"i{router.name[1:]}_startup-config.cfg")  # Ajouter le nom du fichier à la liste source_file
                fichiers_config.append(f"i{router.name[1:]}_startup-config.cfg")

