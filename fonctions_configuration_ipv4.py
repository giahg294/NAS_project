from address_allocator import *
import ipaddress

# Configurer l'en-tête du fichier
def config_head(name, router_type, clients, vrfs, as_number):
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
        if vrfs != []:
            for vrf in vrfs.keys():
                config.append(f"vrf definition {vrf}")
                if router_type == "PE":
                    vrf_access = vrfs[vrf]
                    config.append(f" rd {as_number}:{clients[vrf][0]}")
                    for vrf_a in vrf_access :
                        vrf_prop = clients[vrf_a]
                        if vrf_a == vrf :
                            config.append(f" route-target export {as_number}:{vrf_prop[1]}")
                            config.append(f" route-target import {as_number}:{vrf_prop[1]}")
                        else :
                            config.append(f" route-target import {as_number}:{vrf_prop[1]}")

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
    config.append(f" ip {protocol} area 0")
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
        
        else:
            if interface["vrf"] != []:
                config.append(f" vrf forwarding {interface['vrf']}")
            config.append(f" ip address {interface['ipv4_address']} 255.255.255.252")
            if interface["vrf"] == []:   
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
        direct_neihbor_C = []
        for neighbor_name in direct_neighbor_dico[router.name]:
            neighbor_as = routers_dict[neighbor_name]['AS']

            if neighbor_as == "10": #Si le neighbor est dans l'AS provider (C'est donc un PE car les P ne sont pas directement connectés aux P)
                for neighbor in all_routers:
                    if neighbor.name == neighbor_name: #On cherche l'objet Router correspondant à notre neighbor
                        for neighbor_interface in neighbor.interfaces: # On regarde toutes les interfaces du voisin
                            if neighbor_interface["neighbor"]==router.name: # On cherche l'interface du voisin qui est connectée au routeur qu'on est en train de traiter
                                neighbor_ip_PE = neighbor_interface["ipv4_address"] # On récupère l'addresse physique de l'interface du PE auquel le CE est connecté
                                config.append(f" neighbor {neighbor_ip_PE} remote-as {neighbor_as}")
                                neighbor_PE.append(neighbor_ip_PE)
            else: # Si le voisinn'est pas un PE, c'est forcément un C
                for neighbor in all_routers:
                    if neighbor.name == neighbor_name: #On cherche l'objet Router correspondant à notre neighbor
                        for neighbor_interface in neighbor.interfaces: # On regarde toutes les interfaces du voisin
                            if neighbor_interface["neighbor"]==router.name: # On cherche l'interface du voisin qui est connectée au routeur qu'on est en train de traiter
                                direct_c_ip = neighbor_interface["ipv4_address"] # On récupère l'addresse physique de l'interface du PE auquel le CE est connecté
                                direct_neihbor_C.append(direct_c_ip)


        # On récupère tous les C de la même AS qui sont du même côté du réseau
        for c_a_decla in router.neighbors:
            c_ip = routers_dict[c_a_decla]['loopback'] # On veut l'addresse de loopback des C
            config.append(f" neighbor {c_ip} remote-as {current_as}")
            config.append(f" neighbor {c_ip} update-source Loopback0")
            config.append(" ")
            neighbor_C.append(c_ip)

        ###### Déclaration des networks ######
        config.append("!")
        config.append(" address-family ipv4")

        # Déclaration des loopbacks de tous les c qui sont dans la même AS et du même côté du vpn
        for ip_c in neighbor_C:
            config.append(f"  network {ip_c} mask 255.255.255.255")
        
        # Déclaration du lien physique entre tous les CE et C
        for direct_ip_c in direct_neihbor_C:
            i = direct_ip_c.rsplit('.',3)[-1]
            if int(i)%2 == 0 :
                p = int(i)-2
            else :
                p = int(i)-1
            ip = f"{direct_ip_c.rsplit('.',1)[0]}.{p}"
            config.append(f"  network {ip} mask 255.255.255.252")          

        # Déclaration de la loopback du CE lui-même
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
                config.append(f" neighbor {neighbor_ip} update-source Loopback0")
        config.append(" !\naddress-family vpnv4")
        for neighbor_PE in all_routers:
            if neighbor_PE.router_type == "PE" and neighbor_PE.name != router.name:
                neighbor_name = neighbor_PE.name
                neighbor_ip = routers_dict[neighbor_name]["loopback"]
                config.append(f" neighbor {neighbor_ip} activate")
                config.append(f" neighbor {neighbor_ip} send-community extended")
        config.append("exit-address-family \n!")

        for interface in router.interfaces:
            # On parcourt toutes les interfaces de notre routeur et on garde toutes celles qui correspondent à des vrf
            if interface["vrf"] != []:
                #addresse ip = addresse physique
                ce_name = interface["neighbor"] # on récupère le nom du CE voisin
                as_vrf_neighbor = routers_dict[ce_name]['AS']
                vrf_name = interface["vrf"]
                #vrf_ip = interface["ipv4_address"]
                for rout in all_routers:
                    if rout.name == ce_name: #On cherche l'objet Router correspondant à notre neighbor
                        for ce_interface in rout.interfaces: # On regarde toutes les interfaces du voisin
                            if ce_interface["neighbor"]==router.name: # On cherche l'interface du voisin qui est connectée au routeur qu'on est en train de traiter
                                vrf_ip = ce_interface["ipv4_address"] # On récupère l'addresse physique de l'interface du PE auquel le CE est connecté
                                config.append(f"address-family ipv4 vrf {vrf_name}")
                                config.append(f" neighbor {vrf_ip} remote-as {as_vrf_neighbor}")
                                config.append(f" neighbor {vrf_ip} activate")
                                config.append("exit-address-family \n!")
                                print(f"routeur {router.name} : relié à {ce_name} par l'interface vrf = {ce_interface["name"]} --> vrf ip : {vrf_ip}")

                        

    if router.router_type == "C":
        ###### Déclaration des neighbor #######
        # On déclare tous les C et CE qui sont du même côté du vpn
        for c_and_ce in router.neighbors:
            ip = routers_dict[c_and_ce]['loopback']
            config.append(f" neighbor {ip} remote-as {current_as}")
            config.append(f" neighbor {ip} update-source Loopback0 \n !")
            config.append(" address-family ipv4")
            config.append(f"  neighbor {ip} activate")
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
