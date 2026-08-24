import os
import re
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_dev')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.publications.models import Publication

User = get_user_model()
client = Client()
user = User.objects.first()
client = Client()
client.force_login(User.objects.first())

pub = Publication.objects.filter(is_active=True).first()
if pub:
    client = Client()
    client.force_login(User.objects.first())
    response = client.get('/publication/{}/read/page/1/'.format(pub.slug))
    content = response.content.decode('utf-8')
    
    # Check for the ad container
    match = re.search(r'id=["\']container-[^\'"]+["\']', content)
    if match:
        print('Container ID found:', match.group(0))
    else:
        print('No container ID found')
    
    # Check for script tags with src
    script_matches = re.findall(r'<script[^>]*src=["\']([^"\']+)["\'][^>]*>', content)
    for src in script_matches:
        print('Script src:', src)