"""
CronJobs:

# Ejemplo de entrada en crontab -e (se ejecuta a las 2:00 AM todos los días)
# Asegúrate de usar la ruta completa al entorno y manage.py
0 2 * * * /path/to/venv/bin/python /path/to/project/manage.py sync_strava_data >> /path/to/project/logs/sync_strava_data.log 2>&1

"""
# Crear la estructura de directorios: dashboard/management/commands/
from django.core.management.base import BaseCommand
from django.conf import settings
from dashboard.models import Athlete
from dashboard.views import fetch_and_sync_activities, refresh_strava_token
import requests
from django.db.models import Max

class Command(BaseCommand):
    help = 'Sincroniza las actividades de Strava para todos los atletas.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting Strava data synchronization...'))
        
        # Iterar sobre todos los atletas con tokens de acceso
        athletes = Athlete.objects.all()
        
        if not athletes:
            self.stdout.write(self.style.WARNING("No athletes found in the database."))
            return

        for athlete in athletes:
            self.stdout.write(self.style.NOTICE(f"Processing athlete: {athlete.id} ({athlete.firstname} {athlete.lastname})"))

            try:
                # 1. Refrescar el token si es necesario
                if athlete.is_token_expired():
                    self.stdout.write(self.style.WARNING("Token is expired, refreshing..."))
                    athlete = refresh_strava_token(athlete)
                
                # 2. Sincronizar actividades
                new_count = fetch_and_sync_activities(athlete, athlete.access_token)
                
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully synced {new_count} new activities for {athlete.firstname}."
                ))
                
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(
                    f"API Error for {athlete.firstname}: {e.response.status_code if e.response else 'Unknown'}."
                    "Skipping this athlete."
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Unexpected error for {athlete.firstname}: {e}. Skipping this athlete."
                ))

        self.stdout.write(self.style.NOTICE('Strava data synchronization finished.'))