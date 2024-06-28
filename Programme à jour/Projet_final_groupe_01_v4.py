import xmlrpc.client
import time
from opcua import Client
from opcua import ua

class OdooClient:

    SERVER_URL_ABB = "opc.tcp://172.30.30.30:4840"
    SERVER_URL_FANUC = "opc.tcp://172.30.30.20:4840"

    def __init__(self, url, db, username, password):

        # Init variables
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.models = None

        self.tag_int_value_MDM_ABB = 0  
        self.tag_int_value_FIN_DE_PROD_ABB = -1
        self.tag_int_value_MDM_FANUC = 0  
        self.tag_int_value_FIN_DE_PROD_FANUC = -1
        self.product_qty = 0
        self.product_id = None

        self.Authentification_ERP()

    def Authentification_ERP(self):
        # Connexion à notre serveur ERP_GROUPE_1
        try:
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                print('Connexion réussie. UID :', self.uid)
                self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
            else:
                print('Échec de la connexion.')
        except Exception as e:
            print('Erreur lors de l\'authentification :', e)

    def Recuperer_tous_les_OF(self):
        # Récupération des OF dans l'état en cours, confirmé et à clôturer
        try:
            if not self.uid:
                return []
            orders = self.models.execute_kw(self.db, self.uid, self.password, 'mrp.production', 'search_read', [[('state', 'in', ['progress', 'confirmed', 'to_close'])]], {'fields': ['id', 'product_id', 'product_qty', 'qty_producing', 'date_planned_start']})
            return orders
        except Exception as e:
            print('Erreur lors de la récupération des ordres de fabrication :', e)
            return []

    def Recuperer_OF_date_la_plus_courte(self):
        try:
            orders = self.Recuperer_tous_les_OF()
            if not orders:
                print("Aucun ordre de fabrication en cours.")
                return None
            next_order = min(orders, key=lambda x: x['date_planned_start'])
            return next_order
        except Exception as e:
            print('Erreur lors de la récupération de l\'ordre de fabrication le plus proche :', e)
            return None

    def Cloturer_OF(self):
        try:
            next_order = self.Recuperer_OF_date_la_plus_courte()
            if next_order:
                self.models.execute_kw(self.db, self.uid, self.password, 'mrp.production', 'write', [[next_order['id']], {'state': 'done', 'qty_producing': next_order.get('product_qty', 0)}])
                print("Ordre de fabrication avec ID {} clôturé.".format(next_order['id']))
        except Exception as e:
            print('Erreur lors de la clôture de l\'ordre de fabrication :', e)

    def Recuperer_données_OF(self, order):
        try:
            if order:
                self.product_id = order.get('product_id')[1] if order.get('product_id') else '0'
                self.product_qty = order.get('product_qty', '0')
                qty_producing = self.tag_int_value_FIN_DE_PROD_ABB
                date_planned_start = order.get('date_planned_start', '0')
                print("Prochain ordre de fabrication :")
                print("Article:", self.product_id, "| Quantité à produire:", self.product_qty, "| Quantité produite:", qty_producing, "| Date prévue:", date_planned_start)
            else:
                print("Aucun ordre de fabrication à afficher.")
        except Exception as e:
            print('Erreur lors de la récupération des données de l\'ordre de fabrication :', e)

    def Lecture_IHM_INT_ABB(self):
        
        # Chemin des variables
        NODE_ID_MDM_ABB = "ns=2;s=Local HMI.Tags.tag_mode_de_marche"
        NODE_ID_FIN_DE_PROD_ABB = "ns=2;s=Local HMI.Tags.tag_fin_prod"

        try:
            client = Client(self.SERVER_URL_ABB)

            client.connect()

            # Obtenir les nœuds des variables OPC UA en spécifiant leur identifiant unique
            tag_int_MDM_ABB = client.get_node(ua.NodeId.from_string(NODE_ID_MDM_ABB))
            tag_int_FIN_DE_PROD_ABB = client.get_node(ua.NodeId.from_string(NODE_ID_FIN_DE_PROD_ABB))

            # Lire les valeurs des variables OPC UA
            self.tag_int_value_MDM_ABB = tag_int_MDM_ABB.get_value()
            self.tag_int_value_FIN_DE_PROD_ABB = tag_int_FIN_DE_PROD_ABB.get_value()
            
            print("La valeur de la variable Mode_de_marche_ABB est : {}".format(self.tag_int_value_MDM_ABB))
            print("La valeur de la variable FIN_DE_PROD_ABB est : {}".format(self.tag_int_value_FIN_DE_PROD_ABB))

        except Exception as e:
            print('Erreur lors de la lecture des valeurs OPC UA 1 :', e)
        finally:
            client.disconnect()

    def Lecture_IHM_INT_FANUC(self):

        # Chemin des variables
        NODE_ID_MDM_FANUC = "ns=2;s=Local HMI.Tags.tag_mode_de_marche"
        NODE_ID_FIN_DE_PROD_FANUC = "ns=2;s=Local HMI.Tags.tag_fin_prod"

        try:
            client = Client(self.SERVER_URL_FANUC)

            client.connect()

            tag_int_MDM_FANUC = client.get_node(ua.NodeId.from_string(NODE_ID_MDM_FANUC))
            tag_int_FIN_DE_PROD_FANUC = client.get_node(ua.NodeId.from_string(NODE_ID_FIN_DE_PROD_FANUC))

            # Lire les valeurs des variables OPC UA
            self.tag_int_value_MDM_FANUC = tag_int_MDM_FANUC.get_value()
            self.tag_int_value_FIN_DE_PROD_FANUC = tag_int_FIN_DE_PROD_FANUC.get_value()
            
            print("La valeur de la variable Mode_de_marche_FANUC est : {}".format(self.tag_int_value_MDM_FANUC))
            print("La valeur de la variable FIN_DE_PROD_FANUC est : {}".format(self.tag_int_value_FIN_DE_PROD_FANUC))

        except Exception as e:
            print('Erreur lors de la lecture des valeurs OPC UA 2 :', e)
        finally:
            client.disconnect()

    def Ecriture_IHM_INT_ABB_Nombre_Articles(self):

        # Chemin de la variable
        NODE_NBR_ARTICLES_ABB = "ns=2;s=Local HMI.Tags.tag_nbr_articles"

        try:
            client = Client(self.SERVER_URL_ABB)

            client.connect()

            Valeur_à_envoyé = int(self.product_qty)

            tag_int_NBR_ARTICLES = client.get_node(NODE_NBR_ARTICLES_ABB)

            data_value = ua.DataValue(ua.Variant(Valeur_à_envoyé, ua.VariantType.UInt16))

            tag_int_NBR_ARTICLES.set_value(data_value)
            
            print("La valeur du tag_int_NBR_ARTICLES_ABB a été mise à {}.".format(Valeur_à_envoyé))

        except Exception as e:
            print('Erreur lors de l\'écriture de la valeur OPC UA 3 :', e)
        finally:
            client.disconnect()

    def Ecriture_IHM_INT_ABB_Reset_prod_distant(self):

        # Chemin de la variable
        NODE_ID_Reset_prod_distant = "ns=2;s=Local HMI.Tags.Reset_prod_distant"

        try:
            client = Client(self.SERVER_URL_ABB)

            client.connect()

            Valeur_à_envoyé = 1

            tag_int_Reset_prod_distant = client.get_node(NODE_ID_Reset_prod_distant)

            data_value = ua.DataValue(ua.Variant(Valeur_à_envoyé, ua.VariantType.UInt16))

            tag_int_Reset_prod_distant.set_value(data_value)
            
            print("La valeur de Reset_prod_distant a été mise à {}.".format(Valeur_à_envoyé))

        except Exception as e:
            print('Erreur lors de l\'écriture de la valeur OPC UA 4 :', e)
        finally:
            client.disconnect()

    def Ecriture_IHM_INT_ABB_FIN_de_PROD(self):

        # Chemin de la variable
        NODE_ID_FIN_DE_PROD_ABB = "ns=2;s=Local HMI.Tags.tag_fin_prod"

        try:
            client = Client(self.SERVER_URL_ABB)

            client.connect()

            Valeur_à_envoyé = 0

            tag_int_FIN_DE_PROD_ABB = client.get_node(NODE_ID_FIN_DE_PROD_ABB)

            data_value = ua.DataValue(ua.Variant(Valeur_à_envoyé, ua.VariantType.UInt16))

            tag_int_FIN_DE_PROD_ABB.set_value(data_value)
            
            print("La valeur du tag_int_FIN_de_PROD_ABB a été mise à {} avec succès.".format(Valeur_à_envoyé))

        except Exception as e:
            print('Erreur lors de l\'écriture de la valeur OPC UA 5 :', e)
        finally:
            client.disconnect()
            
    def Ecriture_reset_prod_distant(self):
            
        # Chemin de la variable
        NODE_ID_Reset_prod_distant = "ns=2;s=Local HMI.Tags.Reset_prod_distant"

        try:
            client = Client(self.SERVER_URL_ABB)
            client.connect()

            Valeur_à_envoyé = 0

            tag_int_Reset_prod_distant = client.get_node(NODE_ID_Reset_prod_distant)

            data_value = ua.DataValue(ua.Variant(Valeur_à_envoyé, ua.VariantType.UInt16))
            tag_int_Reset_prod_distant.set_value(data_value)
                
            print("La valeur de Reset_prod_distant a été mise à {}.".format(Valeur_à_envoyé))

        except Exception as e:

            print('Erreur lors de l\'écriture de la valeur OPC UA 4 :', e)
        finally:
            client.disconnect()
            
    def Ecriture_IHM_INT_FANUC_Nombre_articles(self):

        # Chemin de la variable
        NODE_NBR_ARTICLES_FANUC = "ns=2;s=Local HMI.Tags.tag_nb_articles"

        try:
            client = Client(self.SERVER_URL_FANUC)

            client.connect()

            Valeur_à_envoyé = int(self.product_qty)

            tag_int_NBR_ARTICLES_ABB = client.get_node(NODE_NBR_ARTICLES_FANUC)

            data_value = ua.DataValue(ua.Variant(Valeur_à_envoyé, ua.VariantType.UInt16))

            tag_int_NBR_ARTICLES_ABB.set_value(data_value)
            
            print("La valeur du tag_int_NBR_ARTICLES_FANUC a été mise à {} avec succès.".format(Valeur_à_envoyé))

        except Exception as e:
            print('Erreur lors de l\'écriture de la valeur OPC UA 6 :', e)
        finally:
            client.disconnect()

    def Ecriture_IHM_INT_FANUC_Recette(self):

        # Chemin de la variable
        NODE_RECETTE = "ns=2;s=Local HMI.Tags.tag_recette"

        try:
            client = Client(self.SERVER_URL_FANUC)

            client.connect()

            recette_palette = 0
            if self.product_id == 'M1':
                recette_palette = 10
            elif self.product_id == 'M2':
                recette_palette = 20
            elif self.product_id == 'M3':
                recette_palette = 30

            tag_int_RECETTE = client.get_node(NODE_RECETTE)

            data_value = ua.DataValue(ua.Variant(recette_palette, ua.VariantType.UInt16))

            tag_int_RECETTE.set_value(data_value)
            
            print("La valeur de RECETTE a été mise à {}.".format(recette_palette))

        except Exception as e:
            print('Erreur lors de l\'écriture de la valeur OPC UA :', e)
        finally:
            client.disconnect()

    def RAZ_Nbr_articles_et_recette(self):

        # Chemin des variables
        NODE_NBR_ARTICLES_FANUC = "ns=2;s=Local HMI.Tags.tag_nb_articles"
        NODE_RECETTE = "ns=2;s=Local HMI.Tags.tag_recette"
        NODE_ID_Reset_prod_distant = "ns=2;s=Local HMI.Tags.Reset_prod_distant"
        NODE_NBR_ARTICLES_ABB = "ns=2;s=Local HMI.Tags.tag_nbr_articles"

        try:
            #==================================================================================

            client = Client(self.SERVER_URL_FANUC)

            client.connect()

            Valeur_à_envoye = 0
            recette_palette = 0

            #==================================================================================

            tag_int_RECETTE = client.get_node(NODE_RECETTE)

            data_value = ua.DataValue(ua.Variant(recette_palette, ua.VariantType.UInt16))

            tag_int_RECETTE.set_value(data_value)
            
            print("La valeur de RECETTE a été mise à {}.".format(recette_palette))

            #==================================================================================

            tag_int_NBR_ARTICLES_FANUC = client.get_node(NODE_NBR_ARTICLES_FANUC)

            data_value = ua.DataValue(ua.Variant(Valeur_à_envoye, ua.VariantType.UInt16))

            tag_int_NBR_ARTICLES_FANUC.set_value(data_value)
            
            print("La valeur de NBR_ARTICLES_FANUC a été mise à {}.".format(Valeur_à_envoye))

            #==================================================================================

            client = Client(self.SERVER_URL_ABB)

            client.connect()

            Valeur_à_envoyé = 0

            tag_int_NBR_ARTICLES = client.get_node(NODE_NBR_ARTICLES_ABB)

            data_value = ua.DataValue(ua.Variant(Valeur_à_envoyé, ua.VariantType.UInt16))

            tag_int_NBR_ARTICLES.set_value(data_value)
            
            print("La valeur de NBR_ARTICLES_ABB a été mise à {}.".format(Valeur_à_envoyé))

            #==================================================================================

            tag_int_FIN_DE_PROD_ABB = client.get_node(NODE_ID_FIN_DE_PROD_ABB)

            data_value = ua.DataValue(ua.Variant(Valeur_à_envoyé, ua.VariantType.UInt16))

            tag_int_FIN_DE_PROD_ABB.set_value(data_value)
            
            print("La valeur de FIN_de_PROD_ABB a été mise à {}.".format(Valeur_à_envoyé))

            #==================================================================================

        except Exception as e:
            print('Erreur lors de l\'écriture de la valeur OPC UA :', e)
        finally:
            # Déconnexion du serveur OPC UA
            client.disconnect()

def main():
    url = 'http://localhost:8001'
    db = 'erp_grp_1'
    username = 'Python'
    password = 'Python'

    client = OdooClient(url, db, username, password)

    try:
        while True:
            try:
                # Mettre à jour la valeur avant de vérifier

                client.Lecture_IHM_INT_ABB()
                client.Lecture_IHM_INT_FANUC()

                # Vérifier s'il y a un ordre de fabrication en cours

                next_order = client.Recuperer_OF_date_la_plus_courte()
                if next_order is None:
                    print("Aucun ordre de fabrication en cours.")
                    time.sleep(2)
                    continue
                
                # Si les deux IHM sont en mode distant

                if client.tag_int_value_MDM_ABB == 1 and client.tag_int_value_MDM_FANUC == 1:
                    client.Recuperer_données_OF(next_order)  # Récupérer l'id de l'OF et la quantité à produire
                    client.Ecriture_IHM_INT_ABB_Nombre_Articles()  # Écrire la quantité à produire dans la cellule conditionnement
                    client.Ecriture_IHM_INT_FANUC_Nombre_articles()  # Écrire la quantité à produire dans la cellule assemblage
                    client.Ecriture_IHM_INT_FANUC_Recette()  # Écrire la recette dans la cellule assemblage

                    # Clôturer l'OF si product_qty est égal à la valeur produite

                    if int(next_order.get('product_qty', 0)) == client.tag_int_value_FIN_DE_PROD_ABB:
                        client.Cloturer_OF()  # Clôturer OF
                        client.Ecriture_IHM_INT_ABB_Reset_prod_distant() # RAZ variable dans le siemens
                        client.Ecriture_IHM_INT_ABB_FIN_de_PROD()  # Remettre le fin de prod à 0
                        client.Ecriture_reset_prod_distant()
                        client.RAZ_Nbr_articles_et_recette()

            except Exception as e:
                print('Erreur dans la boucle principale :', e)
            time.sleep(2)
    except KeyboardInterrupt:
        print("Programme interrompu.")

if __name__ == "__main__":
    main()
