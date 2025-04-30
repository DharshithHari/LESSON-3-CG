import sqlite3

# --------------------------
# Database Initialization
# --------------------------
class DatabaseInitializer:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.create_tables()
        self.insert_sample_data()
    
    def create_tables(self):
        """Creates the products table structure"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                category TEXT NOT NULL
            )''')
            
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions(
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            total_amount REAL NOT NULL,
            transaction_date TEXT NOT NULL)''')
            
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaction_item(
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY(transaction_id) REFERENCES transactions(transaction_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id))''')
            
        self.conn.commit()
    
    def insert_sample_data(self):
        """Pre-populates initial products"""
        products = [
            (1, 'Apple', 0.99, 100, 'Fruits'),
            (2, 'Milk', 2.49, 50, 'Dairy'),
            (3, 'Bread', 1.99, 75, 'Bakery'),
            (4, 'Eggs', 3.49, 60, 'Dairy'),
            (5, 'Chicken', 5.99, 40, 'Meat')
        ]
        cursor = self.conn.cursor()
        cursor.executemany("INSERT INTO products VALUES (?,?,?,?,?)", products)
        self.conn.commit()

# --------------------------
# Product Management
# --------------------------
class ProductManager:
    def __init__(self, conn):
        self.conn = conn
    
    def add_product(self):
        """Handles product addition with user input"""
        print("\n--- Add New Product ---")
        try:
            product_id = int(input("Enter product ID: "))
            name = input("Enter product name: ").strip()
            price = float(input("Enter product price: "))
            quantity = int(input("Enter stock quantity: "))
            category = input("Enter category: ").strip().capitalize()
            
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO products VALUES (?,?,?,?,?)",
                         (product_id, name, price, quantity, category))
            self.conn.commit()
            print(f"\n✅ Product '{name}' added successfully!")
        
        except ValueError:
            print("\n❌ Error: Invalid input format!")
        except sqlite3.IntegrityError:
            print("\n❌ Error: Product ID already exists!")
    
    def view_products(self):
        """Displays all products in formatted table"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY category, name")
        products = cursor.fetchall()
        
        if not products:
            print("\n⚠️ No products found!")
            return
        
        # Table Header
        print("\n{:<10} {:<20} {:<10} {:<10} {:<15}".format(
            "ID", "Name", "Price", "Stock", "Category"))
        print("-" * 65)
        
        # Table Rows
        for product in products:
            print("{:<10} {:<20} ${:<9.2f} {:<10} {:<15}".format(
                product[0], product[1], product[2], product[3], product[4]))

# ============================================
# Transaction Handling
# ============================================

class TransactionHandler:
    def __init__(self,conn):
        self.conn = conn
        self.current_cart = []
        self.transaction_date = datetime.now().strf("%Y-%m-%d %H:%M:%S")
        
    def start_transaction(self):
        self.current_cart = []
        self.customer_name = customer_name
        self.transaction_date = datetime.now().strf("%Y-%m-%d %H:%M:%S")
        
    def add_to_cart(self):
        try:
            product_id = int(input("Enter Product ID: "))
            quantity = int(input("Enter Quantity: "))
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM products WHERE product_id=?",(product_id,))
            product = cursor.fetchone()
            
            if not product:
                print("X ERROR: Product not found..")
                return
            
            _, name, price,stock, category = product
            
            if stock < quantity:
                print(f"Error: Only {stock} available in stock")
                return
            
            self.current_cart.append({
                'product_id': product_id,
                'name' : name,
                'price' : price
                'quantity' : quantity
            })
            
            cursor.execute("UPDATE products SET quantity = quantity-? WHERE product_id = ?",(quantity,product_id))
            print(f"Added {quantity}x{name} to cart")
        except ValueError:
            print("Please enter number's alone")
            
    def commit_transaction(self):
        if not self.current_cart:
            print("Error: Cart is Empty")
            return
        
        total = sum(item['price']*item['quantity'] for item in self.current_cart)
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO transactions(customer_name,total_amount,transaction_date) VALUE (?,?,?)''',(self.customer_name,total,self.transaction_date))
            
            for item in self.current_cart:
                cursor.execute('''
            INSERT INTO transaction_item(transacation_id, product_id, quantity,price) VALUE (?,?,?,?)''',(transaction_id,item['product_id'],item['quantity'],item['price']))
            
            self.conn.commit()
            return False
            
        except: sqlite3.Error as e:
            print(f"Transaction failed: {e}")
            self.conn.rollback()
            return false
        
# --------------------------
# Main System
# --------------------------
class GroceryStoreSystem:
    def __init__(self):
        self.db = DatabaseInitializer()
        self.product_manager = ProductManager(self.db.conn)
    
    def main_menu(self):
        """Handles the main user interface"""
        while True:
            print("\n=== GROCERY STORE MENU ===")
            print("1. Add Product")
            print("2. View Products")
            print("3. Exit")
            
            choice = input("Enter your choice (1-3): ")
            
            if choice == '1':
                self.product_manager.add_product()
            elif choice == '2':
                self.product_manager.view_products()
            elif choice == '3':
                print("Exiting system...")
                self.db.conn.close()
                break
            else:
                print("Invalid choice! Please try again.")

# --------------------------
# Program Entry Point
# --------------------------
if __name__ == "__main__":
    try:
        store_system = GroceryStoreSystem()
        store_system.main_menu()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
