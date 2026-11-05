import os
import sqlite3
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Fixer la graine aléatoire pour la reproductibilité
np.random.seed(42)
random.seed(42)

print("--- Génération des données Supply Chain Analytics ---")

# Setup des chemins
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_dir = os.path.join(project_root, "data")
db_path = os.path.join(project_root, "supply_chain.db")

os.makedirs(data_dir, exist_ok=True)

# 1. GENERATION DE LA TABLE PRODUCTS
categories = {
    'Maroquinerie': ['Sac Iconique', 'Malle de Voyage', 'Cabas Cuir', 'Portefeuille Prestige'],
    'Horlogerie': ['Chronographe Chrono', 'Montre Automatique Gold', 'Tourbillon Squelette'],
    'Joaillerie': ['Bague Diamant Solitaire', 'Bracelet Saphir', 'Pendentif Or Rose']
}

products_data = []
product_id = 101

for cat, items in categories.items():
    for item in items:
        price = random.randint(1500, 12000) if cat == 'Maroquinerie' else random.randint(8000, 45000)
        products_data.append({
            'product_id': f"PROD_{product_id}",
            'product_name': f"{item} Heritage",
            'category': cat,
            'unit_cost': round(price * 0.35, 2),  # Marge luxe
            'unit_price': price,
            'collection': random.choice(['Permanente', 'Édition Limitée', 'Capsule Automne'])
        })
        product_id += 1

df_products = pd.DataFrame(products_data)

# 2. GENERATION DE LA TABLE SUPPLIERS
suppliers_data = [
    {'supplier_id': 'SUP_01', 'supplier_name': 'Atelier Cuir Toscana', 'country': 'Italie', 'promised_lead_time_days': 10},
    {'supplier_id': 'SUP_02', 'supplier_name': 'Manufacture Horlogère Genève', 'country': 'Suisse', 'promised_lead_time_days': 15},
    {'supplier_id': 'SUP_03', 'supplier_name': 'Maison Joaillerie Place Vendôme', 'country': 'France', 'promised_lead_time_days': 12},
    {'supplier_id': 'SUP_04', 'supplier_name': 'Tanneries de Lyon', 'country': 'France', 'promised_lead_time_days': 8},
    {'supplier_id': 'SUP_05', 'supplier_name': 'Savoir-Faire Métaux Précieux', 'country': 'Italie', 'promised_lead_time_days': 14}
]
df_suppliers = pd.DataFrame(suppliers_data)

# Associer chaque produit à un fournisseur principal
df_products['supplier_id'] = [random.choice(df_suppliers['supplier_id'].tolist()) for _ in range(len(df_products))]

# 3. GENERATION DE LA TABLE STORES
stores_data = [
    {'store_id': 'STR_PAR', 'store_name': 'Flagship Rue du Faubourg Saint-Honoré', 'city': 'Paris', 'country': 'France'},
    {'store_id': 'STR_NYC', 'store_name': 'Maison Fifth Avenue', 'city': 'New York', 'country': 'États-Unis'},
    {'store_id': 'STR_TYO', 'store_name': 'Ginza Boutique', 'city': 'Tokyo', 'country': 'Japon'},
    {'store_id': 'STR_MIL', 'store_name': 'Via Montenapoleone', 'city': 'Milan', 'country': 'Italie'},
    {'store_id': 'STR_LON', 'store_name': 'New Bond Street', 'city': 'Londres', 'country': 'Royaume-Uni'}
]
df_stores = pd.DataFrame(stores_data)

# 4. GENERATION DE LA TABLE INVENTORY
inventory_data = []
for store_id in df_stores['store_id']:
    for _, prod in df_products.iterrows():
        stock_qty = random.randint(2, 25)
        # Créer artificiellement quelques risques de surstock ou de rupture
        if random.random() < 0.10:
            stock_qty = random.choice([0, 1])  # Risque de rupture
        elif random.random() < 0.08:
            stock_qty = random.randint(40, 60) # Surstock
            
        inventory_data.append({
            'store_id': store_id,
            'product_id': prod['product_id'],
            'stock_on_hand': stock_qty,
            'reorder_point': 5,  # Seuil d'alerte réapprovisionnement
            'target_stock_level': 15
        })
df_inventory = pd.DataFrame(inventory_data)

# 5. GENERATION DE LA TABLE ORDERS & DELIVERIES
orders_data = []
deliveries_data = []

start_date = datetime(2026, 1, 1)

for order_idx in range(1, 351):
    order_id = f"ORD_{order_idx:04d}"
    prod = df_products.sample(1).iloc[0]
    store_id = random.choice(df_stores['store_id'].tolist())
    supplier_id = prod['supplier_id']
    
    order_date = start_date + timedelta(days=random.randint(0, 280))
    quantity_ordered = random.randint(5, 30)
    
    orders_data.append({
        'order_id': order_id,
        'product_id': prod['product_id'],
        'store_id': store_id,
        'supplier_id': supplier_id,
        'order_date': order_date.strftime('%Y-%m-%d'),
        'quantity_ordered': quantity_ordered,
        'total_cost': round(quantity_ordered * prod['unit_cost'], 2)
    })
    
    # Génération du suivi de livraison (Correction du type numpy.int64 en int standard)
    promised_days = int(df_suppliers.loc[df_suppliers['supplier_id'] == supplier_id, 'promised_lead_time_days'].values[0])
    expected_delivery = order_date + timedelta(days=promised_days)
    
    # Introduire du retard aléatoire (simuler les dysfonctionnements fournisseurs)
    delay_days = np.random.choice([0, 1, 2, 5, 8], p=[0.60, 0.20, 0.10, 0.06, 0.04])
    actual_delivery = expected_delivery + timedelta(days=int(delay_days))
    
    deliveries_data.append({
        'delivery_id': f"DEL_{order_idx:04d}",
        'order_id': order_id,
        'expected_delivery_date': expected_delivery.strftime('%Y-%m-%d'),
        'actual_delivery_date': actual_delivery.strftime('%Y-%m-%d'),
        'lead_time_days': (actual_delivery - order_date).days,
        'is_delayed': 1 if delay_days > 0 else 0,
        'quantity_received': quantity_ordered if random.random() > 0.03 else quantity_ordered - 1
    })

df_orders = pd.DataFrame(orders_data)
df_deliveries = pd.DataFrame(deliveries_data)

# 6. SAUVEGARDE EN CSV ET EN BASE SQLITE
tables = {
    'products': df_products,
    'suppliers': df_suppliers,
    'stores': df_stores,
    'inventory': df_inventory,
    'orders': df_orders,
    'deliveries': df_deliveries
}

conn = sqlite3.connect(db_path)

for name, df in tables.items():
    csv_path = os.path.join(data_dir, f"{name}.csv")
    df.to_csv(csv_path, index=False)
    df.to_sql(name, conn, if_exists='replace', index=False)
    print(f"Table '{name}' exportée ({len(df)} lignes)")

conn.close()
print("\nBase de données 'supply_chain.db' et fichiers CSV générés avec succès !")