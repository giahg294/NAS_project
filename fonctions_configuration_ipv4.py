from address_allocator import *
import ipaddress

# Configurer l'en-tête du fichier
def config_head(name, router_type, clients, as_number): #ATTENTION : J'AI RAJOUTE L'ARGUMENT CLIENTS A CETTE FONCTION, C'EST LA LISTE DES CLIENTS CONNECTES A UN PE
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
            config.append(f"vrf definition {client}")
            if router_type == "PE":
                config.append(f" rd {as_number}:{client[7:]}00")
                config.append(f" route-target export {as_number}:{client[7:]}000")
                config.append(f" route-target import {as_number}:{client[7:]}000")
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
def config_loopback(ip_loopback, protocol):
    config = []
    config.append("interface Loopback0")
    config.append(f" ip address {ip_loopback} 255.255.255.255")
    config.append(f" ip ospf 1 area 0")
    config.append("!")
    return config

# Configure each interface
def config_interface(interfaces, protocol):
    config = []
    for interface in interfaces:
        config.append(f"interface {interface['name']}")
        if interface['neighbor'] == "None":
            config.append(" no ip address")
            config.append(" shutdown")
        if interface["vrf"] != []:
            config.append(f" vrf forwarding {interface["vrf"]}")
        #Ligne à optimiser !
        if interface['neighbor'] != "None" and interface["vrf"] == []:
            config.append(" mpls ip")
        else:
            if interface['name'] == "FastEthernet0/0":
                config.append(" duplex full")
            if 'ipv4_address' in interface.keys():
                config.append(f" ip address {interface['ipv4_address']} 255.255.255.252")
            if protocol == "OSPF" and interface["vrf"] == []:
                config.append(f" ip ospf 1 area 0")
            if interface['name'] != "FastEthernet0/0":
                config.append(" negotiation auto")
        config.append("!")
            
    
    return config


# Configure BGP Neighbor
def config_bgp(all_routeurs, router, router_id, routers_dict, router_type):
    config = []
    if router_type != "CE":
        config.append("router ospf 1")
        config.append(f" router-id {router_id} \n!")    
    # Configurer les voisins BGP
    current_as = routers_dict[router.name]['AS']
    config.append(f"router bgp {current_as}")
    config.append(" bgp log-neighbor-changes")
    if router_type == "PE":
        # On cherche tous les PE du réseau et on met leur addresse loopback en voisin BGP
        for neighbor_PE in all_routeurs:
            if neighbor_PE.router_type == "PE":
                neighbor_ip = neighbor_PE.interfaces[0]['ipv4_address']
                config.append(f" neighbor {neighbor_ip} remote-as {current_as}")
                config.append(f" neighbor {neighbor_ip} update-source Loopback0 \n!")
                config.append("address-family vpn4")
                config.append(f" neighbor {neighbor_ip} activate")
                config.append(f" neighbor {neighbor_ip} send-community extended")
                config.append("exit-address-family \n!")
    
    for interface in router.interfaces:
        if interface["vrf"] != []:
            neighbor_name = interface["neighbor"]
            as_vrf_neighbor = routers_dict[neighbor_name]['AS']
            vrf_name = interface["vrf"]
            vrf_ip = interface["ipv4_address"]
            config.append(f"address-family ipv4 vrf {vrf_name}")
            config.append(f" neighbor {vrf_ip} remote-as {as_vrf_neighbor}")
            config.append(f" neighbor {vrf_ip} activate")
            config.append("exit-address-family \n!")

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
