#!/usr/bin/env python3
"""
Database setup script for SQL agent example.

This script creates a sample SQLite database with realistic data
for demonstrating the Portia SQL tools.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import random


def create_sample_database(db_path: str = "sample_store.db") -> None:
    """Create a sample SQLite database with tables and data."""
    
    # Remove existing database if it exists
    db_file = Path(db_path)
    if db_file.exists():
        db_file.unlink()
        print(f"Removed existing database: {db_path}")
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create tables
        create_tables(cursor)
        
        # Insert sample data
        insert_sample_data(cursor)
        
        # Commit changes
        conn.commit()
        
        print(f"✅ Database created successfully: {db_path}")
        print_database_summary(cursor)
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def create_tables(cursor: sqlite3.Cursor) -> None:
    """Create all necessary tables."""
    
    # Users table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            age INTEGER,
            city VARCHAR(50),
            country VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    # Products table
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            cost DECIMAL(10, 2) NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    # Orders table
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'pending',
            total_amount DECIMAL(10, 2) NOT NULL,
            shipping_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Order items table
    cursor.execute("""
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)
    
    print("✅ Tables created successfully")


def insert_sample_data(cursor: sqlite3.Cursor) -> None:
    """Insert realistic sample data into all tables."""
    
    # Sample users data
    users_data = [
        ('alice_smith', 'alice.smith@email.com', 'Alice', 'Smith', 28, 'New York', 'USA'),
        ('bob_johnson', 'bob.j@email.com', 'Bob', 'Johnson', 35, 'Los Angeles', 'USA'),
        ('carol_brown', 'carol.brown@email.com', 'Carol', 'Brown', 42, 'Chicago', 'USA'),
        ('david_wilson', 'david.w@email.com', 'David', 'Wilson', 31, 'Houston', 'USA'),
        ('emma_davis', 'emma.davis@email.com', 'Emma', 'Davis', 26, 'Phoenix', 'USA'),
        ('frank_miller', 'frank.m@email.com', 'Frank', 'Miller', 39, 'Philadelphia', 'USA'),
        ('grace_taylor', 'grace.t@email.com', 'Grace', 'Taylor', 33, 'San Antonio', 'USA'),
        ('henry_anderson', 'henry.a@email.com', 'Henry', 'Anderson', 45, 'San Diego', 'USA'),
        ('ivy_thomas', 'ivy.thomas@email.com', 'Ivy', 'Thomas', 29, 'Dallas', 'USA'),
        ('jack_jackson', 'jack.j@email.com', 'Jack', 'Jackson', 37, 'San Jose', 'USA'),
    ]
    
    cursor.executemany("""
        INSERT INTO users (username, email, first_name, last_name, age, city, country)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, users_data)
    
    # Sample products data
    products_data = [
        ('Laptop Pro 15', 'Electronics', 1299.99, 899.99, 25, 'High-performance laptop for professionals'),
        ('Wireless Headphones', 'Electronics', 199.99, 89.99, 50, 'Premium noise-cancelling headphones'),
        ('Coffee Maker Deluxe', 'Appliances', 89.99, 45.00, 30, 'Programmable coffee maker with timer'),
        ('Organic Coffee Beans', 'Food', 24.99, 12.50, 100, 'Single-origin organic coffee beans'),
        ('Running Shoes', 'Sports', 129.99, 65.00, 40, 'Professional running shoes for athletes'),
        ('Yoga Mat Premium', 'Sports', 49.99, 20.00, 60, 'Non-slip premium yoga mat'),
        ('Smartphone Case', 'Electronics', 29.99, 8.00, 150, 'Protective case for smartphones'),
        ('Water Bottle', 'Sports', 19.99, 7.50, 80, 'Insulated stainless steel water bottle'),
        ('Desk Lamp LED', 'Furniture', 79.99, 35.00, 35, 'Adjustable LED desk lamp with USB charging'),
        ('Bluetooth Speaker', 'Electronics', 149.99, 75.00, 45, 'Portable Bluetooth speaker with bass boost'),
    ]
    
    cursor.executemany("""
        INSERT INTO products (name, category, price, cost, stock_quantity, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, products_data)
    
    # Generate sample orders
    base_date = datetime.now() - timedelta(days=90)
    order_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    
    for i in range(25):  # Create 25 orders
        user_id = random.randint(1, 10)
        order_date = base_date + timedelta(days=random.randint(0, 90))
        status = random.choice(order_statuses)
        
        # Calculate total amount (will be updated after inserting order items)
        cursor.execute("""
            INSERT INTO orders (user_id, order_date, status, total_amount, shipping_address)
            VALUES (?, ?, ?, 0, ?)
        """, (user_id, order_date, status, f"123 Main St, City {user_id}, State"))
        
        order_id = cursor.lastrowid
        
        # Add 1-4 items per order
        num_items = random.randint(1, 4)
        total_amount = 0
        
        for _ in range(num_items):
            product_id = random.randint(1, 10)
            quantity = random.randint(1, 3)
            
            # Get product price
            cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
            unit_price = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (order_id, product_id, quantity, unit_price))
            
            total_amount += quantity * unit_price
        
        # Update order total
        cursor.execute("""
            UPDATE orders SET total_amount = ? WHERE id = ?
        """, (total_amount, order_id))
    
    print("✅ Sample data inserted successfully")


def print_database_summary(cursor: sqlite3.Cursor) -> None:
    """Print a summary of the created database."""
    
    print("\n📊 Database Summary:")
    print("-" * 40)
    
    # Count records in each table
    tables = ['users', 'products', 'orders', 'order_items']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table.capitalize()}: {count} records")
    
    print("\n📋 Sample queries you can try:")
    print("- SELECT * FROM users LIMIT 5")
    print("- SELECT name, price FROM products WHERE category = 'Electronics'")
    print("- SELECT COUNT(*) as total_orders, status FROM orders GROUP BY status")
    print("- SELECT u.first_name, u.last_name, COUNT(o.id) as order_count")
    print("  FROM users u LEFT JOIN orders o ON u.id = o.user_id")
    print("  GROUP BY u.id ORDER BY order_count DESC")


if __name__ == "__main__":
    create_sample_database()
