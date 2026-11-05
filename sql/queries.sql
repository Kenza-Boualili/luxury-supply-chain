-- 1. Identification des boutiques et produits à risque de rupture de stock (Stock faible ou nul)
SELECT 
    s.store_name,
    s.city,
    p.product_name,
    p.category,
    i.stock_on_hand,
    i.reorder_point
FROM inventory i
JOIN stores s ON i.store_id = s.store_id
JOIN products p ON i.product_id = p.product_id
WHERE i.stock_on_hand <= i.reorder_point
ORDER BY i.stock_on_hand ASC;


-- 2. Analyse de la performance des fournisseurs (Retards et respect des délais)
SELECT 
    sup.supplier_name,
    sup.country,
    COUNT(d.delivery_id) AS total_deliveries,
    SUM(d.is_delayed) AS delayed_deliveries,
    ROUND(SUM(d.is_delayed) * 100.0 / COUNT(d.delivery_id), 2) AS delay_rate_percentage,
    ROUND(AVG(d.lead_time_days), 1) AS avg_actual_lead_time_days
FROM deliveries d
JOIN orders o ON d.order_id = o.order_id
JOIN suppliers sup ON o.supplier_id = sup.supplier_id
GROUP BY sup.supplier_name, sup.country
ORDER BY delay_rate_percentage DESC;


-- 3. Valeur totale et volume des stocks par boutique
SELECT 
    s.store_name,
    s.country,
    COUNT(i.product_id) AS total_references,
    SUM(i.stock_on_hand) AS total_units_in_stock,
    ROUND(SUM(i.stock_on_hand * p.unit_cost), 2) AS total_inventory_cost_value
FROM inventory i
JOIN stores s ON i.store_id = s.store_id
JOIN products p ON i.product_id = p.product_id
GROUP BY s.store_name, s.country
ORDER BY total_inventory_cost_value DESC;


-- 4. Produits les plus commandés et coût total par catégorie
SELECT 
    p.category,
    COUNT(o.order_id) AS total_orders_placed,
    SUM(o.quantity_ordered) AS total_units_ordered,
    ROUND(SUM(o.total_cost), 2) AS total_procurement_cost
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_procurement_cost DESC;


-- 5. Suivi des surstocks potentiels (Stock supérieur au niveau cible)
SELECT 
    s.store_name,
    p.product_name,
    p.category,
    i.stock_on_hand,
    i.target_stock_level
FROM inventory i
JOIN stores s ON i.store_id = s.store_id
JOIN products p ON i.product_id = p.product_id
WHERE i.stock_on_hand > i.target_stock_level * 2
ORDER BY i.stock_on_hand DESC;