from address_allocator import *
import ipaddress

# Configurer l'en-tête du fichier
def config_head(name, router_type, clients): #ATTENTION : J'AI RAJOUTE L'ARGUMENT CLIENTS A CETTE FONCTION, C'EST LA LISTE DES CLIENTS CONNECTES A UN PE
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
        for client in clients:
            config.append(f"vrf definition {client}\n")
            if router_type == "PE":
                "rd {numéro d'AS}:{nb aléatoire différent pour chaque client}"
                "route-target export {numéro d'AS}:{nb aléatoire différent pour chaque client}"
                "route-target import {numéro d'AS}:{nb aléatoire différent pour chaque client}"
            config.append("\n !\n address-family ipv4\n exit-address-family\n !")
            
    fin_config = ["no aaa new-model",
        "no ip icmp rate-limit unreachable",
        "ip cef",
        "!\r"*5 + "!",
        "no ip domain lookup",
        "no ipv6 cef",
        "!\r!",
        "mpls label protocol ldp",
        "multilink bundle-name authenticated",
        "!\r"*8 + "!",
        "ip tcp synwait-time 5",
        "!\r"*11 + "!",]
    config.extend(fin_config)
    return config


# Configure Loopback Interface
def config_loopback(ip_loopback, protocol, num_ospf):
    config = []
    config.append("interface Loopback0")
    config.append(f" ip address {ip_loopback} 255.255.255.255")
    config.append(f" ip ospf {num_ospf} area 0")
    config.append("!")
    return config

# Configure each interface
def config_interface(interfaces, protocol, num_ospf):
    config = []
    for interface in interfaces:
        config.append(f"interface {interface['name']}")
        if interface['neighbor'] == "None":
            config.append(" shutdown")
        else:
            if interface['name'] == "FastEthernet0/0":
                config.append(" duplex full")
            else:
                config.append(" negotiation auto")
            if 'ipv4_address' in interface.keys():
                config.append(f" ip address {interface['ipv4_address']}/30")
            if protocol == "OSPF":
                config.append(f" ip ospf {num_ospf} area 0")
        
        if protocol == "OSPF":
            config.append("!")
            config.append(f"router ospf {num_ospf}")
            
    
    return config


# Configure BGP Neighbor
def config_bgp(router, router_id, routers_dict):
    # Configurer les voisins BGP
    config = []
    current_as = routers_dict[router.name]['AS']
    config.append(f"router bgp {current_as}")
    config.append(f" bgp router-id {router_id}")
    config.append(" bgp log-neighbor-changes")

    for neighbor in routers_dict:
        if routers_dict[neighbor]['AS'] == current_as and neighbor != router.name:
            neighbor_ip = routers_dict[neighbor]['loopback']
            config.append(f" neighbor {neighbor_ip} remote-as {current_as}")
            config.append(f" neighbor {neighbor_ip} update-source Loopback0")

    config.append("!")
    config.append(" address-family ipv4")
    config.append(" exit-address-family")
    config.append("!")

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

    "Les lignes suivantes sont à un autre endroit dans le fichier de config : à tester si ça marche ici"
    if protocol == "OSPF":
        config.append("router ospf 1")
        config.append(f" router-id {router_id}")

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
