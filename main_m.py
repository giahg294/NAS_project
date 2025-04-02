import json
#import fonction_conf_address
import address_allocator
import drag_and_drop
# Dictionnaire des correspondances entre les routeurs et leurs dossiers et fichiers GNS associes
# Ajouter les noms des dossiers quand on aura mis les routeurs sur GNS
dico_corresp = {"R11" : [" ", "i1"],
    "R12" : [" ", "i2"],
    "R13" : [" ", "i3"],
    "R14" : [" ", "i4"],
    "R15" : [" ", "i5"],
    "R16" : [" ", "i6"],
    "R17" : [" ", "i7"],
    "R21" : [" ", "i8"],
    "R22" : [" ", "i9"],
    "R23" : [" ", "i10"],
    "R24" : [" ", "i11"],
    "R25" : [" ", "i12"],
    "R26" : [" ", "i13"],
    "R27" : [" ", "i14"]}

def modif_config(lines, dico, AS_name, routeur, indice_routeur):
    """
    # Nom du fichier de configuration créé basé sur le nom du routeur
    filename = f"i{routeur[1]+routeur[2]}_startup-config.cfg"

    # id du routeur
    number = routeur[1] + routeur[2] #Prendre uniquement le numero du routeur
    routeur_id = number+"."+number+"."+number+"."+number

    # Détermination du nom de l'AS
    dicoAS = dico["AS"][AS_name]
    """
    #Détermination du protocole
    protocol = dico["AS"]["Protocol"]
    """
    # Récupérer l'info sur si le routeur est en ebgp ou pas, à partir des données JSON
    ebgp = False
    if routeur in dico["Border"]["Routers"]:
        ebgp = True
   """
    # On récupère les résultats des fonctions attribuant les addresses ip et les interfaces
    """dico_interfaces, liste_subnet = address_allocator.interface(dicoAS)
    dico_interfaces_routeur = dico_interfaces[routeur]
    dico_border = fonction_conf_address.border(dico["Border"])
    """
    # Liste pour stocker les lignes modifiées
    updated_lines = []    



    # Parcourir chaque ligne, et pour chaque ligne, soit la modifier si c'est nécessaire, soit la laisser à l'identique
    for line in lines:

        if line.startswith("hostname"):  # Modifier le hostname
            updated_lines.append(f"hostname {routeur}\n")

        # AJOUT POUR CHAQUE PE D'UNE VRF POUR CHAQUE CLIENT QUI LUI EST CONNECTE
        if line.startswith("boot-end-marker"):
            if dico["AS"]["routers"][indice_routeur]["type"] == "PE"
            for client in dico["AS"]["routers"][indice_routeur]["vrf"]:
                updated_lines.append(f"boot-end-marker\n!\n!\nvrf definition{client}\n !\n address-family ipv4\n exit-address-family")

        # CONFIGURATION DES INTERFACES

        # Modification de l'interface Loopback
        elif line.startswith(" ipv6 address 4000"): # On a rajouté le 4000 car il y a plusieurs lignes dans le json qui commencent par ipv6 address.
            if protocol == "OSPF":
                updated_lines.append(f" ipv6 address {dico_interfaces_routeur['Loopback0'][0]}\n")
                updated_lines.append(" ipv6 enable\n")
                updated_lines.append(f" ipv6 ospf {dicoAS["Process"]} area 0\n")
                updated_lines.append(f" ipv6 ospf cost {dico_interfaces_routeur['Loopback0'][1]}\n")
            else :
                updated_lines.append(f" ipv6 address {dico_interfaces_routeur['Loopback0']}\n")
                updated_lines.append(" ipv6 enable\n")
                updated_lines.append(f" ipv6 rip {dicoAS["Process"]} enable\n")

        # Interface FastEthernet0/0
        elif line.startswith("interface FastEthernet0/0"): # Tous les routeurs ont une interface FastEthernet0/0
            updated_lines.append("interface FastEthernet0/0\n")
            updated_lines.append(" no ip address\n")
            if "FastEthernet0/0" in dico_interfaces_routeur.keys():
                if protocol == "OSPF":
                    updated_lines.append(" duplex full\n") # duplex full que pour fastethernet
                    updated_lines.append(f" ipv6 address {dico_interfaces_routeur['FastEthernet0/0'][0]}\n") #Ajout address
                    updated_lines.append(" ipv6 enable\n")
                    updated_lines.append(f" ipv6 ospf {dicoAS["Process"]} area 0\n")
                    updated_lines.append(f" ipv6 ospf cost {dico_interfaces_routeur['FastEthernet0/0'][1]}\n")
                if protocol == "RIP":
                    updated_lines.append(" duplex full\n") # duplex full que pour fastethernet
                    updated_lines.append(f" ipv6 address {dico_interfaces_routeur['FastEthernet0/0']}\n") #Ajout address
                    updated_lines.append(" ipv6 enable\n")
                    updated_lines.append(f" ipv6 rip {dicoAS["Process"]} enable\n")
            else:
                updated_lines.append(" shutdown\n")
                updated_lines.append(" negotiation auto\n")
                     
        # InterfaceGigabitEthernet1/0
        elif line.startswith("interface GigabitEthernet1/0"): # Tous les routeurs ont une interface GigabitEthernet1/0
            updated_lines.append("interface GigabitEthernet1/0\n")
            updated_lines.append(" no ip address\n")
            if "GigabitEthernet1/0" in dico_interfaces_routeur.keys():
                updated_lines.append(" negotiation auto\n")
                if protocol == "OSPF":
                    updated_lines.append(f" ipv6 address {dico_interfaces_routeur['GigabitEthernet1/0'][0]}\n") #Ajout address
                    updated_lines.append(" ipv6 enable\n")
                    updated_lines.append(f" ipv6 ospf {dicoAS["Process"]} area 0\n")
                    updated_lines.append(f" ipv6 ospf cost {dico_interfaces_routeur['GigabitEthernet1/0'][1]}\n")

                if protocol == "RIP":
                    updated_lines.append(f" ipv6 address {dico_interfaces_routeur['GigabitEthernet1/0']}\n") #Ajout address
                    updated_lines.append(" ipv6 enable\n") 
                    updated_lines.append(f" ipv6 rip {dicoAS["Process"]} enable\n")
            else:
                updated_lines.append(" shutdown\n")
                updated_lines.append(" negotiation auto\n")

        # Interface GigabitEthernet2/0
        elif line.startswith("interface GigabitEthernet2/0"): # Tous les routeurs n'ont pas une interface GigabitEthernet2/0
            updated_lines.append("interface GigabitEthernet2/0\n")
            updated_lines.append(" no ip address\n")
            if "GigabitEthernet2/0" in dico_interfaces_routeur.keys():
                updated_lines.append(" negotiation auto\n")
                if protocol == "OSPF":
                    updated_lines.append(f" ipv6 address {dico_interfaces_routeur['GigabitEthernet2/0'][0]}\n") #Ajout address
                    updated_lines.append(" ipv6 enable\n")  
                    updated_lines.append(f" ipv6 ospf {dicoAS["Process"]} area 0\n")
                    updated_lines.append(f" ipv6 ospf cost {dico_interfaces_routeur['GigabitEthernet2/0'][1]}\n")   
                if protocol == "RIP": 
                    updated_lines.append(f" ipv6 address {dico_interfaces_routeur['GigabitEthernet2/0']}\n") #Ajout address
                    updated_lines.append(" ipv6 enable\n") 
                    updated_lines.append(f" ipv6 rip {dicoAS["Process"]} enable\n") 
                    
            else:
                updated_lines.append(" shutdown\n")
                updated_lines.append(" negotiation auto\n")

        # Interface GigabitEthernet3/0
        elif line.startswith("interface GigabitEthernet3/0"): # Tous les routeurs n'ont pas une interface GigabitEthernet3/0
            updated_lines.append("interface GigabitEthernet3/0\n")
            updated_lines.append(" no ip address\n")
            
            if "GigabitEthernet3/0" in dico_interfaces_routeur.keys(): #On entre dans cette boucle si le routeur est en ibgp et qu'il a une interface GigabitEthernet3/0
                updated_lines.append(" negotiation auto\n")
                if protocol == "OSPF":
                    updated_lines.append(f" ipv6 address {dico_interfaces_routeur['GigabitEthernet3/0'][0]}\n") #Ajout address
                    updated_lines.append(" ipv6 enable\n")
                    updated_lines.append(f" ipv6 ospf {dicoAS["Process"]} area 0\n")
                    updated_lines.append(f" ipv6 ospf cost {dico_interfaces_routeur['GigabitEthernet3/0'][1]}\n")

                if protocol == "RIP":
                    updated_lines.append(f" ipv6 address {dico_interfaces_routeur['GigabitEthernet3/0']}\n") #Ajout address
                    updated_lines.append(" ipv6 enable\n") 
                    updated_lines.append(f" ipv6 rip {dicoAS["Process"]} enable\n") 
                 
            
            elif ebgp: # Tous les routeurs en ebgp ont une interface GigabitEthernet3/0, c'est celle qui fait le lien entre 2 AS.
                updated_lines.append(" negotiation auto\n")
                updated_lines.append(f" ipv6 address {dico_border[routeur]['GigabitEthernet3/0']}\n") #Les liens entre 2 AS ne sont pas présent dans dico_interfaces_routeur mais dans dico_border.
                updated_lines.append(" ipv6 enable\n") 
                if protocol == "OSPF": 
                    updated_lines.append(f" ipv6 ospf {dicoAS["Process"]} area 0\n") 
            
            else:
                updated_lines.append(" shutdown\n")
                updated_lines.append(" negotiation auto\n")
            

        # CONFIGURATION BGP
        elif line.startswith("router bgp"): 
            if protocol == "OSPF":
                updated_lines.append(f"router ospf {dicoAS["Process"]}\n")
                updated_lines.append(f" auto-cost reference-bandwidth {dicoAS["Bandwidth"]}\n!\n")
                
            updated_lines.append(f"router bgp {AS_name}\n")


        elif line.startswith(" bgp router-id"):  # Modifier le router-id
            updated_lines.append(f" bgp router-id {routeur_id}\n")

        # Iinitialisation des neighbors
        elif line.startswith(" no bgp default ipv4-unicast"):
            updated_lines.append(" no bgp default ipv4-unicast\n")
            for voisin_bgp in dicoAS["Routeurs"]: # On parcourt tous les routeurs de l'AS
                if voisin_bgp != routeur: # Attention un routeur n'est pas voisin de lui même
                    if protocol == "OSPF":
                        loop_voisin = dico_interfaces[voisin_bgp]['Loopback0'][0]
                    else :
                        loop_voisin = dico_interfaces[voisin_bgp]["Loopback0"]
                    updated_lines.append(f" neighbor {loop_voisin[0:-4]} remote-as {AS_name}\n")
                    updated_lines.append(f" neighbor {loop_voisin[0:-4]} update-source Loopback0\n")
            if ebgp:
                for lien in dico["Border"]["Liens_border"]: # On cherche le voisin ebgp de notre routeur
                    if lien[0] == routeur:
                        voisin_ebgp = lien[1]
                    if lien[1]==routeur:
                        voisin_ebgp = lien[0]
                ad_voisin_ebgp = dico_border[voisin_ebgp]["GigabitEthernet3/0"]
                updated_lines.append(f" neighbor {ad_voisin_ebgp[0:-3]} remote-as {voisin_ebgp[1]+"0"}\n") # Voisin d'une autre AS

        # Annonce des networks et activation des neighbors
        elif line.startswith(" address-family ipv6"): #  Les routeurs de bordure advertise tous les sous-réseaux internes à l'AS.
            updated_lines.append(" address-family ipv6\n")
            if ebgp:
                for subnet in liste_subnet:
                    updated_lines.append(f"  network {subnet}\n")
                updated_lines.append(f"  neighbor {ad_voisin_ebgp[0:-3]} activate\n")
            
            for voisin_bgp in dicoAS["Routeurs"]: # On active tous les voisins
                if voisin_bgp != routeur: # Attention un routeur n'est pas voisin de lui même
                    if protocol == "OSPF":
                        loop_voisin = dico_interfaces[voisin_bgp]['Loopback0'][0]
                    else:
                        loop_voisin = dico_interfaces[voisin_bgp]['Loopback0']
                    updated_lines.append(f"  neighbor {loop_voisin[0:-4]} activate\n")

        elif line.startswith("no ip http secure-server"):
            updated_lines.append("no ip http secure-server\n!\n")
            if protocol == "OSPF":
                updated_lines.append(f"ipv6 router ospf {dicoAS["Process"]}\n router-id {routeur_id}\n")
                if ebgp:
                    updated_lines.append(" passive-interface GigabitEthernet3/0\n")  
        
            if protocol == "RIP":
                updated_lines.append(f"ipv6 router rip {dicoAS["Process"]}\n")
                updated_lines.append(" redistribute connected\n")
        
        else:
            updated_lines.append(line)  # Conserver les lignes inchangées


    # Écrire les modifications dans le fichier
    with open(filename, 'w') as file: # Ce fichier n'existe pas encore, il est donc créé
        file.writelines(updated_lines)
        print(f"Modifications du fichier de configuration de {routeur} terminées.")



if __name__=="__main__": 
    # Charger le fichier JSON
    with open ("GNS.json", 'r') as json_file:
        intent = json.load(json_file)

    # Parcourir chaque AS dans le fichier JSON
    for AS_name in intent["AS"].keys():
        # Lire le fichier modèle 
        with open("modele_startup-config.cfg", 'r') as file:
                lines = file.readlines() # lines = contenu du fichier modèle
        # Parcourir chaque routeur de l'AS
        for routeur in intent["AS"][AS_name]["Routeurs"]:
            modif_config(lines, intent, AS_name, routeur) #Modifie le fichier modèle d'un routeur

    drag_and_drop(dico_corresp)