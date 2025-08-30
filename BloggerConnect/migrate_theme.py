#!/usr/bin/env python3
"""
Migration script to add theme_preference column to existing users
Run this once to update the database schema
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_theme_preference():
    """Add theme_preference column to existing users"""
    try:
        # Connect to database
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Try to add the column
        try:
            cursor.execute('ALTER TABLE "user" ADD COLUMN theme_preference VARCHAR(20) DEFAULT \'dark\'')
            conn.commit()
            print("✅ Added theme_preference column to user table")
        except psycopg2.errors.DuplicateColumn:
            print("ℹ️  theme_preference column already exists")
            conn.rollback()
        except Exception as e:
            print(f"❌ Error adding column: {e}")
            conn.rollback()
            return False
        
        # Update existing users who don't have a theme preference
        try:
            cursor.execute('UPDATE "user" SET theme_preference = \'dark\' WHERE theme_preference IS NULL')
            users_updated = cursor.rowcount
            conn.commit()
            print(f"✅ Updated {users_updated} users with default theme preference")
        except Exception as e:
            print(f"❌ Error updating users: {e}")
            conn.rollback()
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Starting theme preference migration...")
    if migrate_theme_preference():
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")