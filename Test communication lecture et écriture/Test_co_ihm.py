from opcua import Client, ua

# Connexion au serveur OPC UA
opc_client = Client("opc.tcp://192.168.201.223:4840")  # Remplace par l'adresse IP de ton serveur OPC UA

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
    local_hmi = objects.get_child(["0:Local HMI"])
    print("Noeud Local HMI obtenu avec succès")

    variant_value = 1  # Valeur à écrire
    node_lw100 = local_hmi.get_child(["0:LW100"])  # Obtient le noeud correspondant à l'adresse mémoire LW100
    node_lw100.write_value(variant_value)
    print("La valeur 100 a été envoyée à l'adresse mémoire LW100")

except Exception as e:
    print(f"Une erreur s'est produite : {e}")

finally:
    # Fermer la connexion OPC UA
    opc_client.disconnect()
    print("Déconnexion du serveur OPC UA")
