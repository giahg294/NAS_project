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
    if router_type != "CE":
        config.append(f" ip {protocol} area 0")
    else :
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
        
        if interface["vrf"] != []:
            config.append(f" vrf forwarding {interface["vrf"]}")
        
        if interface['neighbor'] != "None":
            if 'ipv4_address' in interface.keys():
                config.append(f" ip address {interface['ipv4_address']} 255.255.255.252")
                
                # config OSPF à optimiser
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
def config_bgp(protocol, all_routers, router, router_id, routers_dict):
    config = []
    current_as = routers_dict[router.name]['AS']
    if router.router_type == "PE":
        config.append(f"router {protocol}")
        config.append(f" router-id {router_id} \n!")
        config.append(f"router bgp {current_as}")
        config.append(" bgp log-neighbor-changes")
    else :
        config.append(f"router {protocol}")
        config.append(f" router-id {router_id} \n!")


    if router.router_type == "CE":
        for neighbor in routers_dict:
            if routers_dict[neighbor]['AS'] == current_as and neighbor != router.name:
                neighbor_ip = routers_dict[neighbor]['loopback']
                config.append("address-family ipv4 vrf NomClientàremplacer")
                config.append(f" neighbor {neighbor_ip} remote-as {current_as}")
                config.append(f" neighbor {neighbor_ip} update-source Loopback0 \n!")
        config.append("!")
        config.append(" address-family ipv4")
        # neighbor 160.124.0.1 mask 255.255.255.255
        for neighbor in routers_dict:
            if routers_dict[neighbor]['AS'] == current_as and neighbor != router.name:
                neighbor_ip = routers_dict[neighbor]['loopback']
                config.append(f"  network {neighbor_ip} mask 255.255.255.255")

        # soi-meme 180.124.0.1 mask 255.255.255.255
        config.append(f"  network {routers_dict[router.name]["loopback"]} 255.255.255.255")   

        # ipv4
        for router1 in routers_dict:
            if routers_dict[router1]['AS'] == current_as and router1 == router.name:
                for interface in router.interfaces :
                    if 'ipv4_address' in interface.keys():
                        # print('OKOKOK')
                        config.append(f"  network {interface['ipv4_address']} mask 255.255.255.252")
                        # print(config)
                        # print(f"  network {interface['ipv4_address']} mask 255.255.255.252")

        # neighbor:  activate & next-hop-self
        for neighbor in routers_dict:
            if routers_dict[neighbor]['AS'] == current_as and neighbor != router.name:
                neighbor_ip = routers_dict[neighbor]['loopback']
                config.append(f"  neighbor {neighbor_ip} avtivate")     
                config.append(f"  neighbor {neighbor_ip} next-hop-self")     

        config.append(" exit-address-family")
        config.append("!")

    if router.router_type == "PE":
        # On cherche tous les PE du réseau et on met leur addresse loopback en voisin BGP
        for neighbor_PE in all_routers:
            if neighbor_PE.router_type == "PE" and neighbor_PE.name != router.name:
                neighbor_name = neighbor_PE.name
                neighbor_ip = routers_dict[neighbor_name]["loopback"]
                config.append(f" neighbor {neighbor_ip} remote-as {current_as}")
                config.append(f" neighbor {neighbor_ip} update-source Loopback0 \n !")
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
