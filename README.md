# Mobile Phone Retail SQL Project Pack

## Project
A fictional mobile-phone retailer database built in SQLite. All records are synthetic and are not real customer or UK market data.

## Files
- `mobile_phone_retail.sqlite` — populated six-table SQLite database
- `generate_database.py` — reproducible Python data generator (fixed seed: 20261106)
- `mobile_phone_database_notebook.ipynb` — notebook documenting generation, schema, scales, intentional quality cases and validation
- `analysis_queries.sql` — example business analysis and data-quality audit queries
- `ER_Diagram.png` — entity relationship diagram
- `SQL_Project_Report.pdf` — three-page report

## Verified row counts
- customers: 320
- products: 63
- stores: 9
- orders: 1,535
- order_items: 1,748
- store_inventory: 567

- Missing delivery estimates: 59
- Duplicate business-event groups: 35
- Foreign-key violations: 0

## Run
Use Python 3. The generator uses only the Python standard library:
```bash
python generate_database.py
```
Open the notebook in Jupyter or Google Colab from the same folder. Run cells from top to bottom. The notebook reads the deliberate missing/duplicate insertion excerpts directly from `generate_database.py`.

## Data quality design
- Missing values are intentionally placed in optional `orders.delivery_days`.
- Duplicate business events are intentionally inserted with new order IDs. The audit compares customer, date, product, quantity and unit price rather than the unique order ID.
- The fixed seed makes the generated counts reproducible.

## Privacy
All customer email addresses use `example.org`. No real telephone numbers, payment-card details or IMEI identifiers are included.
