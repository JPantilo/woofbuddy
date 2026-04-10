from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_admin_user(apps, schema_editor):
    User = apps.get_model('users', 'User')
    
    # Check if admin user already exists
    if not User.objects.filter(username='admin').exists():
        # Create admin user
        admin = User.objects.create(
            username='admin',
            email='admin@woofbuddy.com',
            password=make_password('Admin123!'),  # Change this in production
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        print(f"Admin user created: {admin.username}")

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin_user),
    ]
