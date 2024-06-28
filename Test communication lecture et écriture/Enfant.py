from opcua import Client

# Connexion au serveur OPC UA
opc_client = Client("opc.tcp://192.168.201.185:4840")  # Remplace par l'adresse IP de ton serveur OPC UA

try:
    opc_client.connect()
    print("Connexion réussie au serveur OPC UA")

    # Navigation vers le noeud racine
    root = opc_client.get_root_node()
    print("Noeud racine obtenu avec succès")

    # Navigation vers le noeud "Objects"
    objects = root.get_child(["0:Objects"])
    print("Noeud Objects obtenu avec succès")

    # Navigation vers le noeud "Local HMI"
    local_hmi = objects.get_child(["2:Siemens S7-1200/S7-1500"])
    print("Noeud Local HMI obtenu avec succès")

    # Navigation vers le noeud "Tags" sous "Local HMI"
    tags = local_hmi.get_child(["2:Tags"])
    print("Noeud Tags obtenu avec succès")

    # Afficher tous les enfants du noeud "Tags"
    print("Liste des enfants du noeud Tags:")
    children = tags.get_children()
    for child in children:
        print(child.get_browse_name())

except Exception as e:
    print(f"Une erreur s'est produite : {e}")

finally:
    # Fermer la connexion OPC UA
    opc_client.disconnect()
    print("Déconnexion du serveur OPC UA")
