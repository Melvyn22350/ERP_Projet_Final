from opcua import Client, ua

# Adresse du serveur OPC UA
SERVER_URL = "opc.tcp://192.168.201.223:4840/IHM_CONDI"

# Chemin du nœud "tag_int_2"
NODE_PATH = "ns=2;s=Local HMI.Tags.tes"

# Valeur entière à écrire dans le tag
INTEGER_VALUE = 12

try:
    # Créer un client OPC UA
    client = Client(SERVER_URL)

    # Se connecter au serveur
    client.connect()

    # Obtenir le nœud de la variable OPC UA en spécifiant son chemin
    tag_int_node = client.get_node(NODE_PATH)

    # Créer un objet DataValue avec la valeur entière
    data_value = ua.DataValue(ua.Variant(INTEGER_VALUE, ua.VariantType.UInt16))

    # Écrire la valeur entière dans le tag_int_2
    tag_int_node.set_value(data_value)
    
    print("La valeur du tag_int_2 a été mise à {} avec succès.".format(INTEGER_VALUE))

finally:
    # Déconnexion du serveur OPC UA
    client.disconnect()
