import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'grooming.settings_prod')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin():
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    password = os.environ.get('ADMIN_PASSWORD', 'Admin123!')

    user, created = User.objects.get_or_create(username=username, defaults={
        'email': email,
        'is_staff': True,
        'is_superuser': True
    })

    if created:
        user.set_password(password)
        print(f"Created superuser {username}")
    else:
        # Force staff and superuser status even if user exists
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password) # Ensure password is correct
        print(f"Updated existing user {username} to superuser status")
    
    user.save()

if __name__ == "__main__":
    create_admin()
