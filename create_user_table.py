import mysql.connector

# Connect to MySQL (without specifying a database)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

cursor = db.cursor()

# Create the database if it doesn't exist
cursor.execute("CREATE DATABASE IF NOT EXISTS TrackMyFunds")
cursor.execute("USE TrackMyFunds")
print("Create the database if it doesn't exist.")

# Drop tables if they exist
cursor.execute("DROP TABLE IF EXISTS expenses")
cursor.execute("DROP TABLE IF EXISTS users")
print("Droping expenses table if exists.")
print("Droping user table if exists.")

# Create `users` table
cursor.execute("""
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
)
""")
print("Create `users` table.")

# Create `expenses` table
cursor.execute("""
CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    date DATE NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
print("Create `expenses` table.")

db.commit()
cursor.close()
db.close()

print("Tables created successfully.")
