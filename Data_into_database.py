import sqlite3
import pandas as pd
import hashlib

DB_name = 'identifier.sqlite' #Database name

def hash_password(password): #Hash password for insert into database
  return hashlib.sha256(password.encode()).hexdigest()

def connect(): #Create connection to the database
  return sqlite3.connect(DB_name)

#Insertion functions for each table/relation in the database
def insert_address(connection, address):
  address.to_sql('Address', connection, if_exists='append', index=False)
  print("INSERT Address DONE")

def insert_Auction_Listings(connection, Auction_Listings):
  Auction_Listings.to_sql('Auction_Listings', connection, if_exists='append', index=False)
  print("INSERT Auction_Listings DONE")

def insert_Bidders(connection, Bidders):
  Bidders.to_sql('Bidders', connection, if_exists='append', index=False)
  print("INSERT Bidders DONE")

def insert_Bids(connection, Bids):
  Bids.to_sql('Bids', connection, if_exists='append', index=False)
  print("INSERT Bids DONE")

def insert_Categories(connection, Categories):
  Categories.to_sql('Categories', connection, if_exists='append', index=False)
  print("INSERT Categories DONE")

def insert_Credit_Cards(connection, Credit_Cards):
  Credit_Cards.to_sql('Credit_Cards', connection, if_exists='append', index=False)
  print("INSERT Credit_Cards DONE")

def insert_HelpDesk(connection, HelpDesk):
  HelpDesk.to_sql('HelpDesk', connection, if_exists='append', index=False)
  print("INSERT HelpDesk DONE")

def insert_Local_Vendors(connection, Local_Vendors):
  Local_Vendors.to_sql('Local_Vendors', connection, if_exists='append', index=False)
  print("INSERT Local_Vendors DONE")

def insert_Rating(connection, Ratings):
  Ratings.to_sql('Rating', connection, if_exists='append', index=False)
  print("INSERT Rating DONE")

def insert_Requests(connection, Requests):
  Requests.to_sql('Requests', connection, if_exists='append', index=False)
  print("INSERT Requests DONE")

def insert_Sellers(connection, Sellers):
  Sellers.to_sql('Sellers', connection, if_exists='append', index=False)
  print("INSERT Sellers DONE")

def insert_Transactions(connection, Transactions):
  Transactions.to_sql('Transactions', connection, if_exists='append', index=False)
  print("INSERT Transactions DONE")

def insert_Users(connection, Users):
  Users.to_sql('Users', connection, if_exists='append', index=False)
  print("INSERT Users DONE")

def insert_Zipcode_Info(connection, Zipcode_Info):
  Zipcode_Info.to_sql('Zipcode_Info', connection, if_exists='append', index=False)
  print("INSERT Zipcode_Info DONE")


def update_Triggers(connection, check_auction, enforce_min_bid, enforce_rating):
  # The table holds binary values for each trigger 1 for active 0 for inactive
  cursor = connection.cursor()
  # Creates a cursor to update the Triggers_Settings table
  #Uses try and except block to update the values with the arguments
  try:
    cursor.execute(
                  "UPDATE Trigger_Settings"
                  "SET check_auction = ?"
                  "SET enforce_min_bid = ?"
                  "SET trigger_id = ?"
        , (check_auction, enforce_min_bid, enforce_rating))
  except sqlite3.Error as e: #If there is an error retrieves it and prints out an error
    connection.rollback()
    print(f"Database error: {e}")
  #Commits the changes to the table
  connection.commit()
  print("Triggers setting Set")


if __name__ == "__main__":
  #Creates the connection to the database
  connection = connect()

  #Updates triggers to 0 to turn them off to allow data initialization easily
  update_Triggers(connection, 0, 0, 0)

  DATA_PATH = 'data/' #Create file paths for each csv file
  address = pd.read_csv(DATA_PATH + 'Address.csv')
  Auction_Listings = pd.read_csv(DATA_PATH + 'Auction_Listings.csv')
  Bidders = pd.read_csv(DATA_PATH + 'Bidders.csv')
  Bids = pd.read_csv(DATA_PATH + 'Bids.csv')
  Categories = pd.read_csv(DATA_PATH + 'Categories.csv')
  Credit_Cards = pd.read_csv(DATA_PATH + 'Credit_Cards.csv')
  Helpdesk = pd.read_csv(DATA_PATH + 'Helpdesk.csv')
  Local_Vendors = pd.read_csv(DATA_PATH + 'Local_Vendors.csv')
  Ratings = pd.read_csv(DATA_PATH + 'Ratings.csv')
  Requests = pd.read_csv(DATA_PATH + 'Requests.csv')
  Sellers = pd.read_csv(DATA_PATH + 'Sellers.csv')
  Transactions = pd.read_csv(DATA_PATH + 'Transactions.csv')
  Users = pd.read_csv(DATA_PATH + 'Users.csv')
  Zipcode_Info = pd.read_csv(DATA_PATH + 'Zipcode_Info.csv')

  #Hashes the passwords for Users
  Users['password'] = Users['password'].apply(hash_password)

  #Inserts the CSV Files into the tables
  insert_address(connection, address)
  insert_Auction_Listings(connection, Auction_Listings)
  insert_Bidders(connection, Bidders)
  insert_Bids(connection, Bids)
  insert_Categories(connection, Categories)
  insert_Credit_Cards(connection, Credit_Cards)
  insert_HelpDesk(connection, Helpdesk)
  insert_Local_Vendors(connection, Local_Vendors)
  insert_Rating(connection, Ratings)
  insert_Requests(connection, Requests)
  insert_Sellers(connection, Sellers)
  insert_Transactions(connection, Transactions)
  insert_Users(connection, Users)
  insert_Zipcode_Info(connection, Zipcode_Info)

  #Turns the triggers back on so any subsequent insertions are checked with the constraints
  update_Triggers(connection, 1, 1, 1)
  #Closes the connection to the database
  connection.close()


