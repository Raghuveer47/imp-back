# 🔧 Environment Variables Setup

## 📝 **Development Setup**

Create a `.env` file in your `imp-back` directory:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Cloudinary Settings (Get these from https://cloudinary.com)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Database Settings (for production)
DB_NAME=employeemanagement
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## 🚀 **Production Setup (Railway/Render/Heroku)**

Add these environment variables to your hosting platform:

### **Railway:**
1. Go to your project dashboard
2. Click "Variables" tab
3. Add each variable:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   DB_NAME=railway
   DB_USER=postgres
   DB_PASSWORD=railway-password
   DB_HOST=railway-host
   DB_PORT=5432
   ```

### **Render:**
1. Go to your service dashboard
2. Click "Environment" tab
3. Add each variable in the same format

### **Heroku:**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set CLOUDINARY_CLOUD_NAME=your_cloud_name
heroku config:set CLOUDINARY_API_KEY=your_api_key
heroku config:set CLOUDINARY_API_SECRET=your_api_secret
```

## 🔑 **Getting Cloudinary Credentials**

1. Go to [Cloudinary.com](https://cloudinary.com)
2. Sign up for free account
3. Go to Dashboard
4. Copy your credentials:
   - **Cloud Name**
   - **API Key**
   - **API Secret**

## 🧪 **Testing Cloudinary**

After setting up environment variables, test with:

```bash
# Start Django server
python manage.py runserver

# Try registering an employee - should see:
# ✅ Image uploaded to Cloudinary: https://res.cloudinary.com/...
```

## ⚠️ **Important Notes**

- **Never commit `.env` file** to git
- **Use different credentials** for development and production
- **Cloudinary free tier** is sufficient for your app
- **Face detection works** with or without Cloudinary (fallback to local) 