# config.py
import mysql.connector

class Config:
    SECRET_KEY = 'your_secret_key'
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_NAME = 'TrackMyFunds'

# Create a database connection
db = mysql.connector.connect(
    host=Config.DB_HOST,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME
)
