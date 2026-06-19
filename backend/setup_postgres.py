#!/usr/bin/env python
"""
PostgreSQL Database Setup Script for Financial Analytics System

This script helps set up the PostgreSQL database and user for the application.
Run this script after installing PostgreSQL to prepare the database.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, check=True, capture_output=True):
    """Run a command and return the result"""
    try:
        # Use full path to psql for Windows
        if command.startswith('psql'):
            command = f'"C:\\Program Files\\PostgreSQL\\18\\bin\\psql.exe" {command[5:]}'
        result = subprocess.run(command, shell=True, check=check, capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return None

def check_postgresql_connection():
    """Check if PostgreSQL is running and accessible"""
    print("🔍 Checking PostgreSQL connection...")
    
    # Try to connect to PostgreSQL
    result = run_command('psql -U postgres -c "SELECT version();"')
    if result and result.returncode == 0:
        print("✅ PostgreSQL connection successful")
        return True
    else:
        print("❌ PostgreSQL connection failed")
        print("Please ensure PostgreSQL is running and you can connect as postgres user")
        return False

def create_database():
    """Create the financial_analytics database"""
    print("🗄️ Creating database...")
    
    # Check if database already exists
    result = run_command('psql -U postgres -lqt | cut -d \\| -f 1 | grep -qw financial_analytics')
    if result and result.returncode == 0:
        print("✅ Database 'financial_analytics' already exists")
        return True
    
    # Create database
    result = run_command('psql -U postgres -c "CREATE DATABASE financial_analytics;"')
    if result and result.returncode == 0:
        print("✅ Database 'financial_analytics' created successfully")
        return True
    else:
        print("❌ Failed to create database")
        return False

def create_user():
    """Create a dedicated user for the application"""
    print("👤 Creating database user...")
    
    # Check if user already exists
    result = run_command('psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname=\'financial_user\'"')
    if result and result.returncode == 0 and result.stdout.strip() == '1':
        print("✅ User 'financial_user' already exists")
        return True
    
    # Create user
    result = run_command('psql -U postgres -c "CREATE USER financial_user WITH PASSWORD \'secure_password_123\';"')
    if result and result.returncode != 0:
        print("❌ Failed to create user")
        return False
    
    # Grant privileges
    result = run_command('psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE financial_analytics TO financial_user;"')
    if result and result.returncode == 0:
        print("✅ User 'financial_user' created and granted privileges")
        return True
    else:
        print("❌ Failed to grant privileges to user")
        return False

def test_database_connection():
    """Test connection to the new database"""
    print("🔧 Testing database connection...")
    
    # Test connection with the new user
    result = run_command('psql -U financial_user -d financial_analytics -c "SELECT current_database();"')
    if result and result.returncode == 0:
        print("✅ Database connection test successful")
        return True
    else:
        print("❌ Database connection test failed")
        return False

def update_env_file():
    """Update .env file with PostgreSQL configuration"""
    print("📝 Updating .env file...")
    
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found. Please copy .env.example to .env first")
        return False
    
    # Read current .env file
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Update database configuration
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('DB_NAME='):
            updated_lines.append('DB_NAME=financial_analytics')
        elif line.startswith('DB_USER='):
            updated_lines.append('DB_USER=financial_user')
        elif line.startswith('DB_PASSWORD='):
            updated_lines.append('DB_PASSWORD=secure_password_123')
        elif line.startswith('DB_HOST='):
            updated_lines.append('DB_HOST=localhost')
        elif line.startswith('DB_PORT='):
            updated_lines.append('DB_PORT=5432')
        else:
            updated_lines.append(line)
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ .env file updated with PostgreSQL configuration")
    return True

def main():
    """Main setup function"""
    print("🚀 PostgreSQL Setup for Financial Analytics System")
    print("=" * 50)
    
    # Check PostgreSQL connection
    if not check_postgresql_connection():
        print("\n❌ Setup failed: Cannot connect to PostgreSQL")
        print("Please ensure:")
        print("1. PostgreSQL is installed")
        print("2. PostgreSQL service is running")
        print("3. You can connect as postgres user")
        return False
    
    # Create database
    if not create_database():
        print("\n❌ Setup failed: Cannot create database")
        return False
    
    # Create user
    if not create_user():
        print("\n❌ Setup failed: Cannot create database user")
        return False
    
    # Test connection
    if not test_database_connection():
        print("\n❌ Setup failed: Cannot connect to database")
        return False
    
    # Update .env file
    if not update_env_file():
        print("\n❌ Setup failed: Cannot update .env file")
        return False
    
    print("\n🎉 PostgreSQL setup completed successfully!")
    print("\nNext steps:")
    print("1. Run: python manage.py makemigrations")
    print("2. Run: python manage.py migrate")
    print("3. Run: python manage.py runserver")
    print("\nDatabase connection details:")
    print("- Database: financial_analytics")
    print("- User: financial_user")
    print("- Password: secure_password_123")
    print("- Host: localhost")
    print("- Port: 5432")
    
    return True

if __name__ == '__main__':
    main()
