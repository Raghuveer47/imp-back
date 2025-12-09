#!/usr/bin/env python3
"""
Cloudinary Setup Script
This script helps you set up Cloudinary credentials
"""

import os
from pathlib import Path

def setup_cloudinary():
    print("🚀 Cloudinary Setup for Employee Attendance System")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path('.env')
    
    if env_file.exists():
        print("✅ .env file already exists")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'CLOUDINARY_CLOUD_NAME' in content:
                print("✅ Cloudinary credentials already configured")
                return
    else:
        print("📝 Creating .env file...")
    
    print("\n🔑 To get your Cloudinary credentials:")
    print("1. Go to https://cloudinary.com")
    print("2. Sign up for a free account")
    print("3. Go to Dashboard")
    print("4. Copy your credentials")
    print("\n" + "=" * 50)
    
    # Get user input
    cloud_name = input("Enter your Cloudinary Cloud Name: ").strip()
    api_key = input("Enter your Cloudinary API Key: ").strip()
    api_secret = input("Enter your Cloudinary API Secret: ").strip()
    
    if not all([cloud_name, api_key, api_secret]):
        print("❌ All fields are required!")
        return
    
    # Create .env content
    env_content = f"""# Django Settings
SECRET_KEY=django-insecure-dvemcyi2l-i)f^fz2&6n$&+onq)aw5xe6wzn(--tx@#&x^2_7a
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Cloudinary Settings
CLOUDINARY_CLOUD_NAME={cloud_name}
CLOUDINARY_API_KEY={api_key}
CLOUDINARY_API_SECRET={api_secret}

# Database Settings (for production)
DB_NAME=employeemanagement
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
"""
    
    # Write to .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("\n✅ Cloudinary credentials saved to .env file!")
    print("🔒 Remember: Never commit .env file to git")
    
    # Test configuration
    print("\n🧪 Testing Cloudinary configuration...")
    try:
        import cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        print("✅ Cloudinary configuration successful!")
        print("🚀 You can now run: python manage.py runserver")
    except Exception as e:
        print(f"❌ Error testing Cloudinary: {e}")
        print("💡 Make sure you have the correct credentials")

if __name__ == "__main__":
    setup_cloudinary() 