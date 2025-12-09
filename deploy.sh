#!/bin/bash

echo "🚀 Starting deployment process..."

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the Django project root."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
    echo "✅ .env file created"
fi

# Install production requirements
echo "📦 Installing production requirements..."
pip install -r requirements_deploy.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed
echo "👤 Do you want to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

echo "✅ Deployment preparation complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Push your code to GitHub"
echo "2. Deploy to Railway/Render/Heroku"
echo "3. Set environment variables on your hosting platform"
echo "4. Update frontend API base URL"
echo ""
echo "📚 See DEPLOYMENT_GUIDE.md for detailed instructions" 