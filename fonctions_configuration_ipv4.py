from address_allocator import *
import ipaddress

# Configurer l'en-tête du fichier
def config_head(name, router_type, clients, as_number):
    config = [
        "!\r"*3,
        "!",
        "version 15.2",
        "service timestamps debug datetime msec",
        "service timestamps log datetime msec",
        "!",
        f"hostname {name}",
        "!",
        "boot-start-marker",
        "boot-end-marker",
        "!\r"*2 + "!"]
    
    
    if router_type != "P":
        if clients != []:
            for client in clients.keys():
                config.append(f"vrf definition {client}")
                if router_type == "PE":
                    config.append(f" rd {as_number}:{clients[client][0]}")
                    config.append(f" route-target export {as_number}:{clients[client][1]}")
                    config.append(f" route-target import {as_number}:{clients[client][1]}")
                config.append(" !\n address-family ipv4\n exit-address-family\n!")
                
    suite_config = ["no aaa new-model",
        "no ip icmp rate-limit unreachable",
        "ip cef",
        "!\r"*5 + "!",
        "no ip domain lookup",
        "no ipv6 cef",
        "!\r!"]
    if router_type != "CE":
        suite_config.append("mpls label protocol ldp")
    fin_config = [
        "multilink bundle-name authenticated",
        "!\r"*8 + "!",
        "ip tcp synwait-time 5",
        "!\r"*11 + "!",]
    config.extend(suite_config)
    config.extend(fin_config)
    return config


# Configure Loopback Interface
def config_loopback(ip_loopback, protocol, router_type):
    config = []
    config.append("interface Loopback0")
    config.append(f" ip address {ip_loopback} 255.255.255.255")
    if router_type != "PE":
        config.append(f" ip {protocol} area 0")
    # else :
    #     config.append(f" ip {protocol} area 0")
    config.append("!")
    return config

# Configure each interface
def config_interface(interfaces, protocol,router_type):
    config = []
    for interface in interfaces:
    
        config.append(f"interface {interface['name']}")
        
        if interface['neighbor'] == "None":
            config.append(" no ip address")
            config.append(" shutdown")
            config.append(" negotiation auto")
        
        if interface['neighbor'] != "None":
            if 'ipv4_address' in interface.keys():
                config.append(f" ip address {interface['ipv4_address']} 255.255.255.252")
                
                if interface["vrf"] != []:
                    config.append(f" vrf forwarding {interface['vrf']}")
                else:    
                    config.append(f" ip {protocol} area 0")
            
            if interface['name'] == "FastEthernet0/0":
                config.append(" duplex full")
            else:
                config.append(" negotiation auto")
            if router_type == 'P' or router_type == 'PE':
                if interface["vrf"] == []:
                    config.append(" mpls ip")
        
        config.append("!")
            
    
    return config


# Configure BGP Neighbor
def config_bgp(protocol, all_routers, router, router_id, routers_dict, direct_neighbor_dico):
    config = []
    current_as = routers_dict[router.name]['AS']
    if router.router_type == "PE":
        config.append(f"router {protocol}")
        config.append(f" router-id {router_id} \n!")
        config.append(f"router bgp {current_as}")
        config.append(" bgp log-neighbor-changes")
    elif router.router_type == "CE" :
        config.append(f"router {protocol}")
        config.append(f" router-id {router_id} \n!")
        config.append(f"router bgp {current_as}")
        config.append(f" bgp router-id  {router_id}")
        config.append(" bgp log-neighbor-changes")
    elif router.router_type == "C" :
        config.append(f"router {protocol}")
        config.append(f" router-id {router_id} \n!")
        config.append(f"router bgp {current_as}")
        config.append(" bgp log-neighbor-changes")
    elif router.router_type == "P" :
        config.append(f"router {protocol}")
        config.append(f" router-id {router_id} \n!")



    if router.router_type == "CE":
        ###### Déclaration des neighbor ######
        neighbor_PE = []
        neighbor_C = []
        print("ICIIIII")
        for neighbor_name in direct_neighbor_dico[router.name]:
            neighbor_as = routers_dict[neighbor_name]['AS']

            if neighbor_as == "10": #Si le neighbor est dans l'AS provider (C'est donc un PE car les P ne sont pas directement connectés aux P)
                # Il faudrait faire une fonction pour la boucle suivante ... (Répétition avec déclaration des neighbor juste en-dessous)
                for neighbor in all_routers:
                    if neighbor.name == neighbor_name: #On cherche l'objet Router correspondant à notre neighbor
                        for neighbor_interface in neighbor.interfaces: # On regarde toutes les interfaces du voisin
                            if neighbor_interface["neighbor"]==router.name: # On cherche l'interface du voisin qui est connectée au routeur qu'on est en train de traiter
                                neighbor_ip_PE = neighbor_interface["ipv4_address"] # On récupère l'addresse physique de l'interface du PE auquel le CE est connecté
                                config.append(f" neighbor {neighbor_ip_PE} remote-as {neighbor_as}")
                                neighbor_PE.append(neighbor_ip_PE)
                                print(f"VOISIN PE de {router.name}:{neighbor_name} : {neighbor_ip_PE}")

            else: #Le neighbor est un C 
                neighbor_ip = routers_dict[neighbor_name]['loopback'] # On veut l'addresse de loopback des C
                config.append(f" neighbor {neighbor_ip} remote-as {neighbor_as}")
                config.append(f" neighbor {neighbor_ip} update-source Loopback0")
                config.append(" ")
                neighbor_C.append(neighbor_ip)
                print(f"VOISIN C de {router.name}:{neighbor_name} : {neighbor_ip}")


        ###### Déclaration des networks ######
        config.append("!")
        config.append(" address-family ipv4")

        # Déclaration des loopbacks des C
        for neighbor_name in direct_neighbor_dico[router.name]:
            neighbor_as = routers_dict[neighbor_name]['AS']
            if neighbor_as == current_as: # Correspond à tous ses voisins C
                neighbor_ip = routers_dict[neighbor_name]['loopback']
                config.append(f"  network {neighbor_ip} mask 255.255.255.255")
            else: # Addresse physique du PE ????? ATTENTION : A VERIFIER !!!
            # Il faudrait faire une fonction pour la boucle suivante ... (Répétition avec déclaration des neighbor juste au-dessus)
                for neighbor in all_routers:
                    if neighbor.name == neighbor_name: #On cherche l'objet Router correspondant à notre neighbor
                        for neighbor_interface in neighbor.interfaces: # On regarde toutes les interfaces du voisin
                            if neighbor_interface["neighbor"]==router.name: # On cherche l'interface du voisin qui est connectée au routeur qu'on est en train de traiter
                                neighbor_ip = neighbor_interface["ipv4_address"] # On récupère l'addresse physique de l'interface du PE auquel le CE est connecté
                                config.append(f"  network {neighbor_ip} mask 255.255.255.252")                 

        # Déclaration de la loopback du CE lui-même
        # soi-meme 180.124.0.1 mask 255.255.255.255
        ip_loopback = routers_dict[router.name]['loopback']
        config.append(f"  network {ip_loopback} mask 255.255.255.255")

        # neighbor:  activate & next-hop-self
        for ip_C in neighbor_C:
            config.append(f"  neighbor {ip_C} activate")     
            config.append(f"  neighbor {ip_C} next-hop-self")   
        for ip_PE in neighbor_PE:
            config.append(f"  neighbor {ip_PE} activate")     
            config.append(f"  neighbor {ip_PE} allowas-in")

        config.append(" exit-address-family")
        config.append("!")


    if router.router_type == "PE":
        # On cherche tous les PE du réseau et on met leur addresse loopback en voisin BGP
        for neighbor_PE in all_routers:
            if neighbor_PE.router_type == "PE" and neighbor_PE.name != router.name:
                neighbor_name = neighbor_PE.name
                #neighbor_ip = addresse loopback
                neighbor_ip = routers_dict[neighbor_name]["loopback"]
                config.append(f" neighbor {neighbor_ip} remote-as {current_as}")
                config.append(f" neighbor {neighbor_ip} update-source Loopback0 \n !")
                config.append("address-family vpnv4")
                config.append(f" neighbor {neighbor_ip} activate")
                config.append(f" neighbor {neighbor_ip} send-community extended")
                config.append("exit-address-family \n!")

        for interface in router.interfaces:
            if interface["vrf"] != []:
                #addresse ip = addresse physique
                neighbor_name = interface["neighbor"]
                as_vrf_neighbor = routers_dict[neighbor_name]['AS']
                vrf_name = interface["vrf"]
                vrf_ip = interface["ipv4_address"]
                config.append(f"address-family ipv4 vrf {vrf_name}")
                config.append(f" neighbor {vrf_ip} remote-as {as_vrf_neighbor}")
                config.append(f" neighbor {vrf_ip} activate")
                config.append("exit-address-family \n!")

    if router.router_type == "C":
        ###### Déclaration des neighbor #######
        # On déclare tous les C et CE qui sont du même côté du vpn (pour l'instant cela correspond à tous les voisins car les C ne sont connectés qu'avec des C et CE) 
        # ATTENTION : Ne marche pas s"il y a des C du même côté du réseau qui ne lui sont pas directement connecté.    
        print(f"Voisins du C : {router.name}")
        for neighbor_name in direct_neighbor_dico[router.name]:
                neighbor_loopback = routers_dict[neighbor_name]['loopback'] # On veut l'addresse de loopback des C
                config.append(f" neighbor {neighbor_loopback} remote-as {current_as}")
                config.append(f" neighbor {neighbor_loopback} update-source Loopback0 \n !")
                print(f"{neighbor_name} : {neighbor_loopback}")

                config.append(" address-family ipv4")
                config.append(f"  neighbor {neighbor_loopback} activate")
                config.append(" exit-address-family \n!")

    return config

# Configure end of file
def config_end(protocol, router_id):
    config = [
        "ip forward-protocol nd",
        "!\r!",
        "no ip http server",
        "no ip http secure-server",
        "!"
    ]

    config.append("!\r"*3 + "!")
    config.append("control-plane")
    config.append("!\r!")
    config.append("line con 0")
    config.append(" exec-timeout 0 0")
    config.append(" privilege level 15")
    config.append(" logging synchronous")
    config.append(" stopbits 1")
    config.append("line aux 0")
    config.append(" exec-timeout 0 0")
    config.append(" privilege level 15")
    config.append(" logging synchronous")
    config.append(" stopbits 1")
    config.append("line vty 0 4")
    config.append(" login")
    config.append("!\r!")
    config.append("end\r")
    
    return config
