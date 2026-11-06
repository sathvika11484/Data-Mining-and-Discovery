PRAGMA foreign_keys = ON;

-- Table row counts
SELECT 'customers',COUNT(*) FROM customers UNION ALL
SELECT 'products',COUNT(*) FROM products UNION ALL
SELECT 'stores',COUNT(*) FROM stores UNION ALL
SELECT 'orders',COUNT(*) FROM orders UNION ALL
SELECT 'order_items',COUNT(*) FROM order_items UNION ALL
SELECT 'store_inventory',COUNT(*) FROM store_inventory;

-- Revenue by brand
SELECT p.brand,ROUND(SUM(oi.quantity*oi.unit_price_gbp*(1-oi.discount_pct/100.0)),2) revenue_gbp
FROM order_items oi JOIN products p USING(product_id) JOIN orders o USING(order_id)
WHERE o.order_status='Completed' GROUP BY p.brand ORDER BY revenue_gbp DESC;

-- Monthly sales
SELECT substr(o.order_date,1,7) sales_month,
ROUND(SUM(oi.quantity*oi.unit_price_gbp*(1-oi.discount_pct/100.0)),2) revenue_gbp
FROM orders o JOIN order_items oi USING(order_id)
WHERE o.order_status='Completed' GROUP BY sales_month ORDER BY sales_month;

-- Popular phone models
SELECT p.brand,p.model,SUM(oi.quantity) units_sold
FROM order_items oi JOIN products p USING(product_id) JOIN orders o USING(order_id)
WHERE o.order_status='Completed' GROUP BY p.brand,p.model ORDER BY units_sold DESC;

-- Sales by customer age band
SELECT c.age_band,COUNT(DISTINCT o.order_id) orders,
ROUND(SUM(oi.quantity*oi.unit_price_gbp*(1-oi.discount_pct/100.0)),2) sales_gbp
FROM customers c JOIN orders o USING(customer_id) JOIN order_items oi USING(order_id)
WHERE o.order_status='Completed' GROUP BY c.age_band;

-- Missing delivery estimate audit
SELECT COUNT(*) total_orders,SUM(delivery_days IS NULL) missing_delivery_days
FROM orders;

-- Duplicate business-event audit, excluding unique surrogate order_id
SELECT c.customer_id,o.order_date,oi.product_id,oi.quantity,oi.unit_price_gbp,COUNT(*) copies
FROM orders o JOIN customers c USING(customer_id) JOIN order_items oi USING(order_id)
GROUP BY c.customer_id,o.order_date,oi.product_id,oi.quantity,oi.unit_price_gbp
HAVING COUNT(*)>1 ORDER BY copies DESC;

-- Store performance
SELECT s.store_name,COUNT(DISTINCT o.order_id) order_count,
ROUND(SUM(oi.quantity*oi.unit_price_gbp*(1-oi.discount_pct/100.0)),2) sales_gbp
FROM stores s JOIN orders o USING(store_id) JOIN order_items oi USING(order_id)
WHERE o.order_status='Completed' GROUP BY s.store_id ORDER BY sales_gbp DESC;

-- Low stock alerts
SELECT s.store_name,p.brand,p.model,i.stock_quantity,i.reorder_level
FROM store_inventory i JOIN stores s USING(store_id) JOIN products p USING(product_id)
WHERE i.stock_quantity<=i.reorder_level ORDER BY s.store_name,p.brand;

-- Foreign key validation (expected no rows)
PRAGMA foreign_key_check;


-- Sales by payment method
SELECT o.payment_method, COUNT(DISTINCT o.order_id) order_count,
       ROUND(SUM(oi.quantity*oi.unit_price_gbp*(1-oi.discount_pct/100.0)),2) sales_gbp
FROM orders o
JOIN order_items oi USING(order_id)
WHERE o.order_status='Completed'
GROUP BY o.payment_method
ORDER BY sales_gbp DESC;

-- Product catalogue validation: ensure each product variant is unique
SELECT brand,model,storage_gb,colour,product_condition,COUNT(*) copies
FROM products
GROUP BY brand,model,storage_gb,colour,product_condition
HAVING COUNT(*)>1;
