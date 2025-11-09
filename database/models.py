# database/models.py
import sqlite3
import json
from datetime import datetime
import os

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
        self.init_database()

    def connect(self):
        try:
            # Create database directory if it doesn't exist
            os.makedirs('database', exist_ok=True)
            
            self.connection = sqlite3.connect('database/skillsense.db', check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # This enables column access by name
            print("✅ SQLite Database connected successfully")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")

    def init_database(self):
        try:
            cursor = self.connection.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Skill profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skill_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    profile_name TEXT,
                    source_type TEXT,
                    raw_text TEXT,
                    processed_data TEXT,
                    total_skills INTEGER DEFAULT 0,
                    overall_confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Skills table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER,
                    skill_name TEXT NOT NULL,
                    category TEXT,
                    confidence_score REAL,
                    source TEXT,
                    evidence TEXT,
                    mentions INTEGER DEFAULT 1,
                    is_explicit BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES skill_profiles(id)
                )
            """)
            
            # Job matches table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    job_title TEXT,
                    job_description TEXT,
                    match_percentage REAL,
                    matching_skills TEXT,
                    missing_skills TEXT,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Skill gaps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skill_gaps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    target_role TEXT,
                    current_coverage REAL,
                    missing_skills TEXT,
                    recommendations TEXT,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            self.connection.commit()
            print("✅ Database tables created successfully")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
        finally:
            if cursor:
                cursor.close()

    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                # Convert to list of dictionaries
                columns = [column[0] for column in cursor.description]
                result = [dict(zip(columns, row)) for row in result]
            else:
                self.connection.commit()
                result = cursor.lastrowid
            
            cursor.close()
            return result
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return None

    def close(self):
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")