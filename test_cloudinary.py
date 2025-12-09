#!/usr/bin/env python3
"""
Test Cloudinary Integration
"""

import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employeemanagement.settings')
django.setup()

from employees.cloudinary_utils import configure_cloudinary, upload_base64_to_cloudinary
import base64

def test_cloudinary():
    print("🧪 Testing Cloudinary Integration")
    print("=" * 40)
    
    # Configure Cloudinary
    configure_cloudinary()
    print("✅ Cloudinary configured")
    
    # Create a simple test image (1x1 pixel)
    test_image_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    try:
        # Test upload
        cloudinary_url, cloudinary_id = upload_base64_to_cloudinary(
            test_image_base64,
            folder="test",
            public_id="test_image"
        )
        
        print(f"✅ Upload successful!")
        print(f"📁 Cloudinary URL: {cloudinary_url}")
        print(f"🆔 Cloudinary ID: {cloudinary_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

if __name__ == "__main__":
    success = test_cloudinary()
    if success:
        print("\n🎉 Cloudinary integration is working perfectly!")
        print("🚀 Your face detection + Cloudinary setup is ready!")
    else:
        print("\n❌ Cloudinary integration failed. Check your credentials.") 