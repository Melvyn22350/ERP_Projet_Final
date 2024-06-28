from opcua import Client

# Connexion au serveur OPC UA
opc_client = Client("opc.tcp://192.168.201.185:4840/IHM_CONDI")  # Remplace par l'adresse IP de ton serveur OPC UA

try:
    opc_client.connect()
    print("Connexion réussie au serveur OPC UA")

    # Navigation vers le noeud racine
    root = opc_client.get_root_node()
    print("Noeud racine:", root)

    # Navigation vers le noeud Objects
    objects = root.get_child(["0:Objects"])
    print("Noeud Objects:", objects)

    # Listage des enfants du noeud Objects pour trouver le bon chemin
    children = objects.get_children()
    for child in children:
        print("Enfant du noeud Objects:", child)
        print("Chemin:", child.get_browse_name())

except Exception as e:
    print(f"Une erreur s'est produite : {e}")

finally:
    # Fermer la connexion OPC UA
    opc_client.disconnect()
    print("Déconnexion du serveur OPC UA")
