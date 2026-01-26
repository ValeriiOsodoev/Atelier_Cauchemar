import sqlite3

conn = sqlite3.connect('atelier.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Tables:', tables)

for table_name, in tables:
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    print(f'\n{table_name} columns:')
    for col in columns:
        print(f'  {col}')

# Check some data
print('\n=== Sample Data ===')
for table_name, in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    print(f'{table_name}: {count} records')

conn.close()
