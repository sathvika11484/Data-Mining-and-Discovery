"""
Mobile Phone Retail and Sales Database — synthetic dataset generator.
All records are simulated; no real customers or IMEI numbers are used.
Fixed seed ensures reproducibility.
"""
import sqlite3, random
from pathlib import Path
from datetime import date, timedelta

SEED = 20261106
random.seed(SEED)
DB = Path("mobile_phone_retail.sqlite")

BRANDS = ["Apple", "Samsung", "Google", "Motorola", "OnePlus", "Xiaomi"]
MODELS = {
 "Apple": ["iPhone 15", "iPhone 15 Pro", "iPhone 16", "iPhone 16 Pro"],
 "Samsung": ["Galaxy S24", "Galaxy S24 Ultra", "Galaxy A55", "Galaxy Z Flip6"],
 "Google": ["Pixel 8", "Pixel 8 Pro", "Pixel 9", "Pixel 9 Pro"],
 "Motorola": ["Edge 50", "Moto G85", "Razr 50"],
 "OnePlus": ["OnePlus 12", "OnePlus 12R", "Nord 4"],
 "Xiaomi": ["Redmi Note 13", "Xiaomi 14", "Poco X6"]
}
COLOURS = ["Black", "White", "Blue", "Silver", "Green", "Graphite", "Pink"]
STORAGE = [64, 128, 256, 512, 1024]
REGIONS = ["London", "South East", "South West", "North West", "North East",
           "East Midlands", "West Midlands", "Yorkshire", "Scotland", "Wales",
           "Northern Ireland", "East of England"]
PAYMENTS = ["Debit card", "Credit card", "PayPal", "Cash", "Buy now pay later"]
CHANNELS = ["In-store", "Website", "Mobile app"]
CONDITIONS = ["New", "Refurbished", "Open-box"]

def create_database(path=DB):
    path = Path(path)
    if path.exists(): path.unlink()
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys=ON")
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE customers(
      customer_id INTEGER PRIMARY KEY,
      first_name TEXT NOT NULL,
      last_name TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      age_band TEXT NOT NULL CHECK(age_band IN ('18-24','25-34','35-44','45-54','55-64','65+')),
      region TEXT NOT NULL,
      customer_since_year INTEGER NOT NULL CHECK(customer_since_year BETWEEN 2018 AND 2026),
      marketing_consent INTEGER NOT NULL CHECK(marketing_consent IN (0,1))
    );
    CREATE TABLE products(
      product_id INTEGER PRIMARY KEY,
      brand TEXT NOT NULL,
      model TEXT NOT NULL,
      storage_gb INTEGER NOT NULL CHECK(storage_gb IN (64,128,256,512,1024)),
      colour TEXT NOT NULL,
      operating_system TEXT NOT NULL CHECK(operating_system IN ('iOS','Android')),
      screen_inches REAL NOT NULL CHECK(screen_inches BETWEEN 4.5 AND 8.5),
      launch_year INTEGER NOT NULL CHECK(launch_year BETWEEN 2019 AND 2026),
      list_price_gbp REAL NOT NULL CHECK(list_price_gbp BETWEEN 80 AND 2500),
      product_condition TEXT NOT NULL CHECK(product_condition IN ('New','Refurbished','Open-box')),
      UNIQUE(brand, model, storage_gb, colour, product_condition)
    );
    CREATE TABLE stores(
      store_id INTEGER PRIMARY KEY,
      store_name TEXT NOT NULL UNIQUE,
      region TEXT NOT NULL,
      store_type TEXT NOT NULL CHECK(store_type IN ('High street','Shopping centre','Online fulfilment'))
    );
    CREATE TABLE orders(
      order_id INTEGER PRIMARY KEY,
      customer_id INTEGER NOT NULL,
      store_id INTEGER NOT NULL,
      order_date TEXT NOT NULL,
      sales_channel TEXT NOT NULL CHECK(sales_channel IN ('In-store','Website','Mobile app')),
      payment_method TEXT NOT NULL CHECK(payment_method IN ('Debit card','Credit card','PayPal','Cash','Buy now pay later')),
      delivery_days INTEGER CHECK(delivery_days IS NULL OR delivery_days BETWEEN 0 AND 14),
      order_status TEXT NOT NULL CHECK(order_status IN ('Completed','Dispatched','Returned','Cancelled')),
      FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
      FOREIGN KEY(store_id) REFERENCES stores(store_id)
    );
    CREATE TABLE order_items(
      order_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      quantity INTEGER NOT NULL CHECK(quantity BETWEEN 1 AND 3),
      unit_price_gbp REAL NOT NULL CHECK(unit_price_gbp BETWEEN 50 AND 3000),
      discount_pct REAL NOT NULL CHECK(discount_pct BETWEEN 0 AND 50),
      warranty_months INTEGER NOT NULL CHECK(warranty_months IN (3,6,12,24)),
      PRIMARY KEY(order_id, product_id),
      FOREIGN KEY(order_id) REFERENCES orders(order_id),
      FOREIGN KEY(product_id) REFERENCES products(product_id)
    );
    CREATE TABLE store_inventory(
      store_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      stock_quantity INTEGER NOT NULL CHECK(stock_quantity BETWEEN 0 AND 500),
      reorder_level INTEGER NOT NULL CHECK(reorder_level BETWEEN 1 AND 100),
      last_restocked TEXT NOT NULL,
      PRIMARY KEY(store_id, product_id),
      FOREIGN KEY(store_id) REFERENCES stores(store_id),
      FOREIGN KEY(product_id) REFERENCES products(product_id)
    );
    CREATE INDEX idx_orders_date ON orders(order_date);
    CREATE INDEX idx_orders_customer ON orders(customer_id);
    CREATE INDEX idx_items_product ON order_items(product_id);
    """)

    first_names = ["Oliver","Amelia","George","Isla","Harry","Ava","Noah","Mia","Jack","Lily",
                   "Leo","Freya","Arthur","Grace","Oscar","Ella","Muhammad","Sofia","Charlie","Emily"]
    last_names = ["Smith","Jones","Taylor","Brown","Wilson","Davies","Evans","Thomas","Roberts","Johnson",
                  "Walker","Wright","Thompson","White","Green","Hall","Wood","Clarke","Patel","Khan"]
    # 320 synthetic customers; fictional example.org emails prevent real contact.
    for cid in range(1,321):
        fn, ln = random.choice(first_names), random.choice(last_names)
        email = f"customer{cid:04d}@example.org"
        age = random.choices(["18-24","25-34","35-44","45-54","55-64","65+"],[18,28,20,15,12,7])[0]
        cur.execute("""INSERT INTO customers VALUES(?,?,?,?,?,?,?,?)""",
          (cid,fn,ln,email,age,random.choice(REGIONS),random.randint(2018,2026),random.randint(0,1)))

    store_data = [
      ("London Central","London","High street"),("Croydon Store","London","Shopping centre"),
      ("Brighton Mobile","South East","High street"),("Birmingham Connect","West Midlands","Shopping centre"),
      ("Manchester Phones","North West","High street"),("Leeds Digital","Yorkshire","Shopping centre"),
      ("Glasgow Mobile","Scotland","High street"),("Cardiff Devices","Wales","Shopping centre"),
      ("Online Warehouse","South East","Online fulfilment")
    ]
    cur.executemany("INSERT INTO stores(store_name,region,store_type) VALUES(?,?,?)",store_data)

    # Create 63 product variants with plausible specifications and prices.
    pid=1
    for brand, models in MODELS.items():
      for model in models:
        for storage in random.sample(STORAGE, 3):
          colour = random.choice(COLOURS)
          os_name = "iOS" if brand=="Apple" else "Android"
          screen = round(random.uniform(5.8,7.0),1)
          launch = random.randint(2021,2026)
          base_price = {"Apple":850,"Samsung":720,"Google":650,"Motorola":330,"OnePlus":560,"Xiaomi":390}[brand]
          price = round(base_price * (storage/128)**0.22 * random.uniform(.88,1.14),2)
          condition = random.choices(CONDITIONS,[78,15,7])[0]
          cur.execute("""INSERT INTO products VALUES(?,?,?,?,?,?,?,?,?,?)""",
             (pid,brand,model,storage,colour,os_name,screen,launch,price,condition))
          pid += 1

    # Store-level stock with composite primary key (store_id, product_id).
    for store_id in range(1, 10):
      for product_id in range(1, pid):
        stock = random.choices([0, random.randint(1,8), random.randint(9,35)], [0.08,0.52,0.40])[0]
        reorder = random.randint(3,12)
        restock_date = date(2026,1,1)+timedelta(days=random.randint(0,309))
        cur.execute("INSERT INTO store_inventory VALUES(?,?,?,?,?)",
                    (store_id,product_id,stock,reorder,restock_date.isoformat()))

    # 1,500 orders and 1,720 line items; one table exceeds 1,000 rows.
    order_rows=[]
    item_rows=[]
    start=date(2026,1,1)
    for oid in range(1,1501):
      cid=random.randint(1,320); sid=random.randint(1,9)
      dt=start+timedelta(days=random.randint(0,309))
      channel=random.choices(CHANNELS,[35,45,20])[0]
      pay=random.choices(PAYMENTS,[35,28,15,12,10])[0]
      delivery=random.randint(0,7)
      status=random.choices(["Completed","Dispatched","Returned","Cancelled"],[76,12,7,5])[0]
      # Deliberately inject missing delivery estimates in 4.5% of orders.
      if random.random()<0.045: delivery=None
      order_rows.append((oid,cid,sid,dt.isoformat(),channel,pay,delivery,status))
      for product_id in random.sample(range(1,pid), random.choices([1,2],[.86,.14])[0]):
        prod_price=cur.execute("SELECT list_price_gbp FROM products WHERE product_id=?",(product_id,)).fetchone()[0]
        unit=round(prod_price*random.uniform(.90,1.03),2)
        discount=random.choice([0,0,0,5,10,15,20])
        qty=random.choices([1,2,3],[.92,.07,.01])[0]
        warranty=random.choice([3,6,12,24])
        item_rows.append((oid,product_id,qty,unit,discount,warranty))

    cur.executemany("INSERT INTO orders VALUES(?,?,?,?,?,?,?,?)",order_rows)
    cur.executemany("INSERT INTO order_items VALUES(?,?,?,?,?,?)",item_rows)

    # Deliberately create duplicate business events as additional order line records.
    # The composite PK is preserved by placing duplicate facts under a new order ID:
    # the duplicate audit key is customer + date + product + quantity + price.
    duplicate_sources=random.sample(item_rows,35)
    for j,src in enumerate(duplicate_sources, start=1501):
      original_order=cur.execute("SELECT customer_id,store_id,order_date,sales_channel,payment_method,delivery_days,order_status FROM orders WHERE order_id=?",(src[0],)).fetchone()
      cid,sid,dt,ch,pay,delivery,status=original_order
      cur.execute("INSERT INTO orders VALUES(?,?,?,?,?,?,?,?)",(j,cid,sid,dt,ch,pay,delivery,status))
      cur.execute("INSERT INTO order_items VALUES(?,?,?,?,?,?)",(j,src[1],src[2],src[3],src[4],src[5]))

    con.commit()
    assert cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0]==1535
    assert cur.execute("SELECT COUNT(*) FROM order_items").fetchone()[0] >= 1500
    assert cur.execute("PRAGMA foreign_key_check").fetchall()==[]
    con.close()
    return path

if __name__=="__main__":
    print("Created:",create_database().resolve())
