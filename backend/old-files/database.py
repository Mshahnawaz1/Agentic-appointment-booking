import psycopg2
from pydantic import Base64Bytes


class Database:
    def __init__(self, host, port, database, user, password):
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()

    def execute(self, query, params=None):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetchall(self):
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    db = Database("localhost", 5432, "school", "myuser", "mypassword")
    
    db.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id SERIAL PRIMARY KEY,
            doctor_name VARCHAR(100),
            age INTEGER,
            grade VARCHAR(10)
        )
    """)
    
    db.execute("""
        INSERT INTO students (name, age, grade) 
        VALUES (%s, %s, %s)
    """, ("Jane Doe", 16, "12th"))
    
    db.execute("SELECT * FROM students")
    print(db.fetchall())
    
    db.close()