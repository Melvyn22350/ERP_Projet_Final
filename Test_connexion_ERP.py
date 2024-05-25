import xmlrpc.client
import time

class OdooClient:
    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.models = None
        self._authenticate()

    def _authenticate(self):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        if self.uid:
            print('Connexion réussie. UID :', self.uid)
            self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        else:
            print('Échec de la connexion.')
            exit()

    def get_current_manufacturing_orders(self):
        if not self.uid:
            return []
        orders = self.models.execute_kw(self.db, self.uid, self.password, 'mrp.production', 'search_read', [[('state', 'in', ['progress', 'confirmed', 'to_close'])]], {'fields': ['product_id', 'product_qty', 'qty_producing']})
        return orders

    def call_procure_calculation(self):
        if not self.uid:
            return
        orders = self.get_current_manufacturing_orders()
        for order in orders:
            if order.get('qty_producing', 0) == order.get('product_qty', 0):
                # Mettre à jour l'état à "done" et la quantité en production
                self.models.execute_kw(self.db, self.uid, self.password, 'mrp.production', 'write', [[order['id']], {'state': 'done', 'qty_producing': order.get('product_qty', 0)}])
                print("État mis à jour à 'done' et quantité en production ajustée pour l'ordre de fabrication avec ID:", order['id'])
        
        # Mettre à jour la quantité virtuellement disponible pour tous les articles
        self.update_virtual_available()

        # Appeler la méthode procure_calculation
        self.models.execute_kw(self.db, self.uid, self.password, 'stock.scheduler.compute', 'procure_calculation', [[]])
        print("Méthode procure_calculation appelée.")

        self.display_stock_quantity()
        self.display_virtual_available()

    def update_virtual_available(self):
        if not self.uid:
            return
        # Récupérer tous les articles avec leur quantité disponible
        articles = self.models.execute_kw(self.db, self.uid, self.password, 'product.product', 'search_read', [[]], {'fields': ['id', 'qty_available']})
        for article in articles:
            # Mettre à jour virtual_available avec qty_available pour chaque article
            self.models.execute_kw(self.db, self.uid, self.password, 'product.product', 'write', [[article['id']], {'virtual_available': article.get('qty_available', 0)}])
        print("Mise à jour de virtual_available avec qty_available terminée.")

    def display_stock_quantity(self):
        if not self.uid:
            return
        # Récupérer tous les articles avec leur quantité disponible
        articles = self.models.execute_kw(self.db, self.uid, self.password, 'product.product', 'search_read', [[]], {'fields': ['id', 'name', 'qty_available']})
        # Afficher la quantité en stock de chaque article dans le terminal
        print("Quantité en stock pour chaque article :")
        for article in articles:
            article_name = article.get('name', 'N/A')
            stock_quantity = article.get('qty_available', 0)
            print(f"Article: {article_name} | Quantité en stock: {stock_quantity}")

    def display_virtual_available(self):
        if not self.uid:
            return
        # Récupérer tous les articles avec leur quantité virtuellement disponible
        articles = self.models.execute_kw(self.db, self.uid, self.password, 'product.product', 'search_read', [[]], {'fields': ['id', 'name', 'virtual_available']})
        # Afficher la quantité virtuellement disponible de chaque article dans le terminal
        print("Quantité virtuellement disponible pour chaque article :")
        for article in articles:
            article_name = article.get('name', 'N/A')
            virtual_available = article.get('virtual_available', 0)
            print(f"Article: {article_name} | Quantité virtuellement disponible: {virtual_available}")

def display_orders(orders):
    print("Ordres de fabrication en cours:")
    for order in orders:
        product_id = order.get('product_id')[1] if order.get('product_id') else '0'
        product_qty = order.get('product_qty') if order.get('product_qty') else '0'
        qty_producing = order.get('qty_producing') if order.get('qty_producing') else '0'
        print("Article:", product_id, "| Quantité:", product_qty, "| Quantité produite", qty_producing)

def main():
    url = 'http://192.168.1.21:8069'
    db = 'ERP_GROUPE_1'
    username = 'Administrator'
    password = '123'

    client = OdooClient(url, db, username, password)

    while True:
        orders = client.get_current_manufacturing_orders()
        display_orders(orders)
        
        client.call_procure_calculation()

        time.sleep(3)

if __name__ == "__main__":
    main()
