import sqlite3
import hashlib
import pandas as pd # used for reading CSV data

DB_NAME = 'identifier.sqlite'

def hash_password(password):
  return hashlib.sha256(password.encode()).hexdigest()

def connect():
  return sqlite3.connect(DB_NAME)

def create_tables(connection):
  connection.executescript("""
    DROP TABLE IF EXISTS Sellers;
    DROP TABLE IF EXISTS Bidders;
    DROP TABLE IF EXISTS Helpdesk;
    DROP TABLE IF EXISTS Users;

    CREATE TABLE IF NOT EXISTS Users(email TEXT PRIMARY KEY, password TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS Helpdesk(email TEXT PRIMARY KEY, position TEXT NOT NULL, FOREIGN KEY(email) REFERENCES Users(email));
    CREATE TABLE IF NOT EXISTS Bidders(email TEXT PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL, age REAL NOT NULL, home_address_id INTEGER NOT NULL, major TEXT NOT NULL, FOREIGN KEY(email) REFERENCES Users(email));
    CREATE TABLE IF NOT EXISTS Sellers(email TEXT PRIMARY KEY, bank_routing_number TEXT NOT NULL, bank_account_number TEXT NOT NULL, balance REAL NOT NULL, FOREIGN KEY(email) REFERENCES Users(email));
  """)
  connection.commit()
  print("CREATE TABLES DONE")

def insert_users(connection, users):
  users.to_sql('Users', connection, if_exists='append', index=False)
  print("INSERT USERS DONE")

def insert_helpdesk(connection, helpdesk):
  helpdesk.to_sql('Helpdesk', connection, if_exists='append', index=False)
  print("INSERT HELP DESK DONE")

def insert_bidders(connection, bidders):
  bidders.to_sql('Bidders', connection, if_exists='append', index=False)
  print("INSERT BIDDERS DONE")

def insert_sellers(connection, sellers):
  sellers.to_sql('Sellers', connection, if_exists='append', index=False)
  print("INSERT SELLERS DONE")

if __name__ == "__main__":
  connection = connect()
  # create_tables(connection)

  DATA_PATH = 'data/'
  users = pd.read_csv(DATA_PATH + 'users.csv')
  users['password'] = users['password'].apply(hash_password)
  insert_users(connection, users)

  helpdesk = pd.read_csv(DATA_PATH + 'helpdesk.csv')
  insert_helpdesk(connection, helpdesk)

  bidders = pd.read_csv(DATA_PATH + 'bidders.csv')
  insert_bidders(connection, bidders)

  sellers = pd.read_csv(DATA_PATH + 'sellers.csv')
  insert_sellers(connection, sellers)