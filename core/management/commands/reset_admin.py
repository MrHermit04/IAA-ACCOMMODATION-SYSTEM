from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Reset admin password'

    def handle(self, *args, **kwargs):
        user, created = User.objects.get_or_create(username='admin', defaults={'is_superuser': True, 'is_staff': True})
        user.set_password('Group39@2025') # <-- Weka password unayotaka hapa
        user.save()
        self.stdout.write(self.style.SUCCESS('Admin password set to Group39@2025'))
