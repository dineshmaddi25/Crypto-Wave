import sqlite3

conn = sqlite3.connect('crypto.db')
cursor = conn.cursor()

# Define the SQL statement with appropriate data types
create_table_query = '''
    CREATE TABLE IF NOT EXISTS blocjchain (
        number VARCHAR(10),
        hash VARCHAR(64),
        previous_hash VARCHAR(64),
        data VARCHAR(100),
        nonce VARCHAR(15)
    )
'''

# Execute the SQL statement to create the table
cursor.execute(create_table_query)
# Commit the changes and close the connection
conn.commit()
conn.close()