#!/usr/bin/env python3
"""
Smart Django Server Startup Script
Automatically detects the best IP address and starts the server
"""

import os
import sys
import subprocess
import socket
import requests
from pathlib import Path

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def get_network_ips():
    """Get all available network IPs"""
    ips = []
    try:
        # Get all network interfaces
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'inet ' in line and '127.0.0.1' not in line:
                    ip = line.split()[1]
                    if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
                        ips.append(ip)
    except:
        pass
    
    # Fallback to common local IPs
    if not ips:
        ips = ['192.168.1.1', '192.168.0.1', '10.0.0.1']
    
    return ips

def test_connection(ip, port=8000):
    """Test if a connection can be made to the IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((ip, port))
        s.close()
        return result == 0
    except:
        return False

def start_server():
    """Start the Django server with the best available IP"""
    print("🚀 Starting Employee Attendance System Server")
    print("=" * 50)
    
    # Get available IPs
    local_ip = get_local_ip()
    network_ips = get_network_ips()
    
    print(f"📍 Local IP: {local_ip}")
    print(f"🌐 Network IPs: {', '.join(network_ips)}")
    
    # Try different IP addresses
    ip_options = [
        "0.0.0.0",  # Allow all connections
        local_ip,
        "127.0.0.1",
        "localhost"
    ] + network_ips
    
    # Remove duplicates while preserving order
    seen = set()
    ip_options = [ip for ip in ip_options if not (ip in seen or seen.add(ip))]
    
    print("\n🔍 Testing connection options...")
    
    for ip in ip_options:
        print(f"  Testing {ip}:8000...", end=" ")
        if test_connection(ip, 8000):
            print("❌ Port 8000 in use")
        else:
            print("✅ Available")
    
    # Start server with 0.0.0.0 (allows connections from anywhere)
    print(f"\n🚀 Starting server on 0.0.0.0:8000")
    print("📱 This allows connections from:")
    print(f"   - Local: http://localhost:8000")
    print(f"   - Local: http://127.0.0.1:8000")
    print(f"   - Network: http://{local_ip}:8000")
    print(f"   - Any device on your network")
    print("\n🔗 API Endpoints:")
    print(f"   - Health Check: http://0.0.0.0:8000/api/health/")
    print(f"   - API Info: http://0.0.0.0:8000/api/info/")
    print(f"   - Employees: http://0.0.0.0:8000/api/employees/")
    print(f"   - Admin: http://0.0.0.0:8000/admin/")
    
    print("\n" + "=" * 50)
    print("✅ Server starting... Press Ctrl+C to stop")
    print("=" * 50)
    
    # Start Django server
    try:
        subprocess.run([
            sys.executable, "manage.py", "runserver", "0.0.0.0:8000"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

if __name__ == "__main__":
    start_server() 