#!/usr/bin/env python3
"""
Script to run database seeding.
Usage: python run_seed.py
"""
import sys
sys.path.insert(0, '.')

from app.utils.seed_data import seed_database

if __name__ == "__main__":
    print("🌱 Running Rental Manager Database Seeder...")
    print("=" * 50)
    
    try:
        seed_database()
        print("=" * 50)
        print("✅ Seeding completed successfully!")
    except Exception as e:
        print("=" * 50)
        print(f"❌ Error: {e}")
        sys.exit(1)
