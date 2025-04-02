# Définition de la classe Router (Routeur)
class Router:
    def __init__(self, name, router_type, interfaces):
        # Initialisation du routeur avec un nom, un type et des interfaces
        self.name = name  # Nom du routeur
        self.router_type = router_type  # Type de routeur (par ex., eBGP, iBGP)
        self.interfaces = interfaces  # Liste des interfaces associées au routeur

    def __str__(self):
        # Représentation textuelle du routeur
        return f"Router(Name: {self.name}, Type: {self.router_type}, Interfaces: {self.interfaces})"
        
# Définition de la classe AS (Système Autonome)
class AS:
    def __init__(self, number, ip_range, loopback_range, protocol, routers, relation):
        # Initialisation de l'AS avec son numéro, plages d'adresses, protocole et routeurs
        self.number = number  # Numéro de l'AS
        self.ip_range = ip_range  # Plage d'adresses IP pour cet AS
        self.loopback_range = loopback_range  # Plage d'adresses loopback
        self.protocol = protocol  # Protocole utilisé (RIP, OSPF, etc.)
        # Création d'instances de routeurs pour cet AS
        self.routers = [Router(router['name'], router['type'], router['interfaces']) for router in routers]
        self.relation = relation

    def __str__(self):
        # Représentation textuelle de l'AS
        router_str = '\n  '.join(str(router) for router in self.routers)
        return f"AS(Number: {self.number}, IP Range: {self.ip_range}, Loopback Range: {self.loopback_range}, Protocol: {self.protocol}, Routers:\n  {router_str})"

# Génération de la matrice de connexions avec noms des routeurs
def generate_connections_matrix_name(routers, AS):
    connections = []  # Liste pour stocker les connexions
    for router in routers:
        router_as = AS[router.name]  # Récupération de l'AS du routeur actuel
        for interface in router.interfaces:
            if interface['neighbor'] != "None":  # Vérifie si l'interface est connectée
                router_name = router.name
                neighbor_name = interface['neighbor']

                neighbor_as = AS[neighbor_name]  # Récupération de l'AS du voisin
                # Vérifie si la connexion est "inter-AS" (frontière)
                if router_as != neighbor_as:
                    state = "border"
                else:
                    state = router_as

                # Crée une connexion triée pour éviter les doublons
                connection = tuple(sorted([router_name, neighbor_name]))
                connection = (connection, state)

                # Ajoute la connexion si elle n'est pas encore enregistrée
                if connection not in connections:
                    connections.append(connection)

    # Trie les connexions par ordre alphabétique des routeurs
    connections.sort(key=lambda x: x[0]) 
    return connections

# Génération de la matrice de connexions avec indices numériques
def generate_connections_matrix(routers, AS):
    connections = []  # Liste pour stocker les connexions
    for router in routers:
        router_as = AS[router.name]  # Récupération de l'AS du routeur actuel
        for interface in router.interfaces:
            if interface['neighbor'] != "None":  # Vérifie si l'interface est connectée
                router_index = int(router.name[1:])  # Récupère l'indice du routeur
                neighbor_index = int(interface['neighbor'][1:])  # Récupère l'indice du voisin

                neighbor_as = AS[interface['neighbor']]  # Récupération de l'AS du voisin
                # Vérifie si la connexion est "inter-AS" (frontière)
                if router_as != neighbor_as:
                    state = "border"
                else:
                    state = router_as

                # Crée une connexion triée pour éviter les doublons
                connection = tuple(sorted([neighbor_index, router_index]))
                connection = (connection, state)

                # Ajoute la connexion si elle n'est pas encore enregistrée
                if connection not in connections:
                    connections.append(connection)

    # Trie les connexions par indices des routeurs
    connections.sort(key=lambda x: x[0]) 
    return connections

# Génération de l'adresse loopback pour un routeur
def generate_loopback(name, loopback_range):
    router_number = int(name[1:])  # Récupère le numéro du routeur
    return f"{loopback_range[:-4]}{router_number}"  # Formate l'adresse loopback

# Génération des adresses IPv4 pour les interfaces
def generate_interface_addresses(routers, connections_matrix):
    ip_range = "130.124.1.0/24"
    subnet = 0
    ip_existants = []
    for lien in connections_matrix:
        for router in lien[0]:
            for r in routers:
                if int(router) == int(r.name[1:]):
                    i = 0
                    for interface in r.interfaces:
                        if interface['neighbor'] != "None" and int(interface['neighbor'][1]) in lien[0]:
                            ip = subnet+1+i
                            if ip not in ip_existants:
                                ipv4_address = f"{ip_range[:-4]}{ip}"
                                ip_existants.append(ip)
                            else:
                                ipv4_address = f"{ip_range[:-4]}{ip+1}"
                                ip_existants.append(ip+1)
                            interface['ipv4_address'] = ipv4_address
                            print(f"{r.name} {interface["name"]}--> {ipv4_address}")
                            i += 1
        subnet += 4

# Génération de l'ID routeur (Router ID)
def generate_router_id(name):
    router_number = ''.join(filter(str.isdigit, name))  # Extrait les chiffres du nom du routeur
    return '.'.join([router_number] * 4)  # Formate l'ID sous forme IPv4-like

# Génération d'un dictionnaire contenant les informations des routeurs
def generate_routers_dict(all_as):
    routers_dict = {}
    for as_obj in all_as:
        for router in as_obj.routers:
            # Génère l'adresse loopback pour chaque routeur
            loopback_address = generate_loopback(router.name, as_obj.loopback_range)
            router_dict = {
                'loopback': loopback_address,  # Adresse loopback
                'AS': as_obj.number  # Numéro de l'AS
            }
            routers_dict[router.name] = router_dict
    return routers_dict

def generate_as_dict(all_as):
    as_dico = {}
    for as_obj in all_as:
        as_dico[as_obj.number] = {}
        router_liste = []
        for router in as_obj.routers:
            # Génère l'adresse loopback pour chaque routeur
            router_liste.append(router.name)
        as_dico[as_obj.number] = {"routers":router_liste, "protocol":as_obj.protocol, "relation":as_obj.relation}
    return as_dico