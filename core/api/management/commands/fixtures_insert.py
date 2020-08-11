import os
import subprocess

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Insert all default data'

    def handle(self, *args, **options):
        try:
            subprocess.call("python manage.py loaddata fixtures/"+'types_user_action.json',shell=True)
            subprocess.call("python manage.py loaddata fixtures/"+'users.json',shell=True)

            self.stdout.write(self.style.SUCCESS('Successfully load fixtures'))

        except Exception as e:
            self.stdout.write(self.style.ERROR('An error happened: "%s"' % str(e)))
