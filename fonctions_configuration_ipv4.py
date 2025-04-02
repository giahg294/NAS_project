from address_allocator import *
import ipaddress

# Configurer l'en-tête du fichier
def config_head(name):
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
        "!\r"*2 + "!",
        "no aaa new-model",
        "no ip icmp rate-limit unreachable",
        "ip cef",
        "!\r"*5 + "!",
        "no ip domain lookup",
        "!\r!",
        "multilink bundle-name authenticated",
        "!\r"*8 + "!",
        "ip tcp synwait-time 5",
        "!\r"*11 + "!",
    ]
    return config

# Configure Loopback Interface
def config_loopback(ip_loopback, protocol):
    config = []
    config.append("interface Loopback0")
    config.append(f" ip address {ip_loopback}/32")

    if protocol == "RIP":
        config.append(" ip rip advertise")
    if protocol == "OSPF":
        config.append(" ip ospf 1 area 0")

    config.append("!")
    return config

# Configure each interface
def config_interface(interfaces, protocol):
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
            if protocol == "RIP":
                config.append(" ip rip advertise")
            elif protocol == "OSPF":
                config.append(" ip ospf 1 area 0")
        
        if protocol == "OSPF":
            config.append("!")
            config.append("router ospf 1")
    
    return config

def config_network(current_as, routers, routers_dict, neighbor_dico):
    networks = []
    for routeur in routers:
        if routeur.name in neighbor_dico.keys() or (current_as == routers_dict[routeur.name]['AS'] and routeur.router_type == 'iBGP'):
            for interface in routeur.interfaces:
                ip_addr = interface['ipv4_address']
                if ip_addr:
                    try:
                        network = ipaddress.IPv4Network(ip_addr, strict=False)
                        if network not in networks : 
                            networks.append(network)
                    except ValueError:
                        print(f"Invalid IP addresse: {ip_addr}")
    return networks

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

    if protocol == "RIP":
        config.append("router rip")
        config.append(" version 2")
        config.append(" redistribute connected")
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
    config.append("line vty 0 4")
    config.append(" login")
    config.append("!\r!")
    config.append("end\r")
    
    return config
