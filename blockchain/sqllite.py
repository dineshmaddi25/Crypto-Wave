import sqlite3
from blockchain import Block, Blockchain

# Custom exceptions for transaction errors
class InvalidTransactionException(Exception):
    pass

class InsufficientFundsException(Exception):
    pass

# Define the Table class
class Table():
    # Specify the table name and columns
    def __init__(self, table_name, *args):
        self.table = table_name
        self.columns = "(%s)" % ",".join(args)
        self.columnsList = args
        # If table does not already exist, create it.
        if self.isnewtable(table_name):
            self.create_table()

    # Get all the values from the table
    def getall(self):
        with sqlite3.connect('C:/Users/dines/blockchain/crypto.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table}")
            return cursor.fetchall()

    # Get one value from the table based on a column's data
    def getone(self, search, value):
        with sqlite3.connect('C:/Users/dines/blockchain/crypto.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table} WHERE {search} = ?", (value,))
            return cursor.fetchone()

    # Delete a value from the table based on column's data
    def deleteone(self, search, value):
        with sqlite3.connect('C:/Users/dines/blockchain/crypto.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE from {self.table} where {search} = ?", (value,))
            conn.commit()

    # Delete all values from the table.
    def deleteall(self):
        self.drop()  # Remove table and recreate
        self.__init__(self.table, *self.columnsList)

    # Remove table from SQLite3
    def drop(self):
        with sqlite3.connect('C:/Users/dines/blockchain/crypto.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE {self.table}")

    # Create the table in SQLite3
    def create_table(self):
        with sqlite3.connect('C:/Users/dines/blockchain/crypto.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE TABLE {self.table} ({','.join([f'{col} varchar(100)' for col in self.columnsList])})")

    # Insert values into the table
    def insert(self, *args):
        data = ",".join(["?" for _ in args])  # Generate placeholders
        with sqlite3.connect('C:/Users/dines/blockchain/crypto.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {self.table}{self.columns} VALUES({data})", args)
            conn.commit()

    # Check if table already exists
    def isnewtable(self, tableName):
        with sqlite3.connect('C:/Users/dines/blockchain/crypto.db') as conn:
            cursor = conn.cursor()
            try:  # Attempt to get data from table
                cursor.execute(f"SELECT * from {tableName}")
                cursor.fetchall()
            except sqlite3.OperationalError:
                return True
            else:
                return False

    # Send money from one user to another
    def send_money(self, sender, recipient, amount):
        # Verify that the amount is a valid float value
        try:
            amount = float(amount)
        except ValueError:
            raise InvalidTransactionException("Invalid Transaction.")

        # Verify that the user has enough money to send (exception if it is the BANK)
        if amount > self.get_balance(sender) and sender != "BANK":
            raise InsufficientFundsException("Insufficient Funds.")

        # Verify that the user is not sending money to themselves or the amount is less than or equal to 0
        elif sender == recipient or amount <= 0.00:
            raise InvalidTransactionException("Invalid Transaction.")

        # Verify that the recipient exists
        elif self.isnewuser(recipient):
            raise InvalidTransactionException("User Does Not Exist.")

        # Update the blockchain and sync to SQLite3
        blockchain = self.get_blockchain()
        number = len(blockchain.chain) + 1
        data = "%s-->%s-->%s" % (sender, recipient, amount)
        blockchain.mine(Block(number, data=data))
        self.sync_blockchain(blockchain)

    # Get the balance of a user
    def get_balance(self, username):
        balance = 0.00
        blockchain = self.get_blockchain()

        # Loop through the blockchain and update balance
        for block in blockchain.chain:
            data = block.data.split("-->")
            if username == data[0]:
                balance -= float(data[2])
            elif username == data[1]:
                balance += float(data[2])
        return balance

    # Get the blockchain from SQLite3 and convert to Blockchain object
    def get_blockchain(self):
        blockchain = Blockchain()
        blockchain_sql = Table("blockchain", "number", "hash", "previous", "data", "nonce")
        for b in blockchain_sql.getall():
            blockchain.add(Block(int(b.get('number')), b.get('previous'), b.get('data'), int(b.get('nonce'))))

        return blockchain

    # Update blockchain in SQLite3 table
    def sync_blockchain(self, blockchain):
        blockchain_sql = Table("blockchain", "number", "hash", "previous", "data", "nonce")
        blockchain_sql.deleteall()

        for block in blockchain.chain:
            blockchain_sql.insert(str(block.number), block.hash(), block.previous_hash, block.data, block.nonce)

    # Check if user already exists
    def isnewuser(self, username):
        # Access the users table and get all values from column "username"
        users = Table("users", "name", "email", "username", "password")
        data = users.getall()
        usernames = [user.get('username') for user in data]

        return False if username in usernames else True

# Define Flask routes and functionality here...
