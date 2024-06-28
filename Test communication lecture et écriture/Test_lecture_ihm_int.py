from opcua import Client
from opcua import ua

# Adresse du serveur OPC UA
SERVER_URL = "opc.tcp://192.168.201.223:4840"

# Identifiant unique du nœud "tag_int"
NODE_ID = "ns=2;s=Siemens S7-1200/S7-1500.Tags.tag_mode_de_marche"

try:
    # Créer un client OPC UA
    client = Client(SERVER_URL)

    # Se connecter au serveur
    client.connect()

    # Obtenir le nœud de la variable OPC UA en spécifiant son identifiant unique
    tag_int_node = client.get_node(ua.NodeId.from_string(NODE_ID))

    # Lire la valeur de la variable OPC UA
    tag_int_value = tag_int_node.get_value()
    
    print("La valeur de la variable tag_int est : {}".format(tag_int_value))

finally:
    # Déconnexion du serveur OPC UA
    client.disconnect()
