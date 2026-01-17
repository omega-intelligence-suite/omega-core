import os
import psycopg2
from psycopg2.extras import RealDictCursor

class Database:
  def __init__(self):
    self.USER = os.getenv("SUPABASE_DB_USER")
    self.PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
    self.HOST = os.getenv("SUPABASE_DB_HOST")
    self.PORT = os.getenv("SUPABASE_DB_PORT")
    self.DBNAME = os.getenv("SUPABASE_DB_NAME")
    self.connection = None
    self.cursor = None

  def connect(self):
    try:
      self.connection = psycopg2.connect(
        user=self.USER,
        password=self.PASSWORD,
        host=self.HOST,
        port=self.PORT,
        dbname=self.DBNAME,
        cursor_factory=RealDictCursor  # Returns results as dictionaries
      )
      print("Connection successful!")
      self.cursor = self.connection.cursor()
      return self.connection

    except Exception as e:
      print(f"Failed to connect: {e}")
      return None

  def close(self):
    if self.cursor:
      self.cursor.close()
    if self.connection:
      self.connection.close()
      print("Connection closed.")

  def execute(self, query, params=None):
    try:
      self.cursor.execute(query, params)
      self.connection.commit()

      # Fetch results for SELECT queries or INSERT/UPDATE/DELETE with RETURNING clause
      if query.strip().upper().startswith('SELECT') or 'RETURNING' in query.upper():
        return self.cursor.fetchall()
      else:
        # For INSERT, UPDATE, DELETE without RETURNING - return affected row count
        return self.cursor.rowcount

    except Exception as e:
      print(f"Database query failed: {e}")
      return None