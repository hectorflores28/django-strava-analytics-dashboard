from django.db import models
from django.utils import timezone
from datetime import timedelta

# --- Modelos de Datos Replicando la Estructura de SQLAlchemy ---

class Athlete(models.Model):
    # Campos básicos del atleta
    id = models.BigIntegerField(primary_key=True, help_text="Strava Athlete ID")
    username = models.CharField(max_length=100, blank=True, null=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    profile_medium = models.CharField(max_length=200, blank=True, null=True)
    profile = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    sex = models.CharField(max_length=10, blank=True, null=True)

    # Campos de autenticación (los más cruciales)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.IntegerField() # Timestamp UNIX para manejar la expiración

    # Campos de auditoría
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def is_token_expired(self):
        """Verifica si el token de acceso ha expirado."""
        return timezone.now().timestamp() > self.expires_at - 600 # 10 minutos de margen

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.id})"


class Activity(models.Model):
    # Campos primarios de la actividad
    id = models.BigIntegerField(primary_key=True, help_text="Strava Activity ID")
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='activities')

    # Métricas de la actividad
    name = models.CharField(max_length=255)
    distance = models.FloatField(help_text="Distance in meters")
    moving_time = models.IntegerField(help_text="Moving time in seconds")
    elapsed_time = models.IntegerField(help_text="Elapsed time in seconds")
    total_elevation_gain = models.FloatField(help_text="Elevation gain in meters")
    type = models.CharField(max_length=50, help_text="e.g., Run, Ride, Swim")
    sport_type = models.CharField(max_length=50, help_text="e.g., Running, Cycling, Swimming")
    average_speed = models.FloatField(help_text="Average speed in m/s")
    max_speed = models.FloatField(help_text="Max speed in m/s")
    has_heartrate = models.BooleanField(default=False)
    average_heartrate = models.FloatField(blank=True, null=True)
    max_heartrate = models.FloatField(blank=True, null=True)
    
    # Fechas y geolocalización
    start_date = models.DateTimeField(help_text="Start date in UTC")
    start_date_local = models.DateTimeField(help_text="Start date in local time zone")
    timezone = models.CharField(max_length=100)
    
    # Campo para la racha (streak) u otros metadatos calculados
    calculated_day = models.DateField(db_index=True, help_text="Date part of start_date_local for daily grouping")

    # Método de utilidad para la plantilla
    def distance_km(self):
        """Convierte la distancia (metros) a kilómetros."""
        return self.distance / 1000.0 if self.distance else 0.0

    def moving_time_formatted(self):
        """Convierte el tiempo de movimiento (segundos) a HHh MMm SSs."""
        seconds = self.moving_time or 0
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        # Formato compacto HHh MMm
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m"
        elif minutes > 0:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{int(seconds)}s"

    def average_speed_kmh(self):
        """Convierte la velocidad media (m/s) a km/h."""
        # m/s * 3.6 = km/h
        return self.average_speed * 3.6 if self.average_speed else 0.0

    class Meta:
        ordering = ['-start_date_local']
        verbose_name_plural = "Activities"
        
    def save(self, *args, **kwargs):
        # Aseguramos que el campo `calculated_day` se calcule antes de guardar
        if self.start_date_local:
            self.calculated_day = self.start_date_local.date()
        super().save(*args, **kwargs)

    def get_pace(self):
        """Calcula el ritmo en min/km (asumiendo metros y segundos)."""
        if self.distance > 0 and self.moving_time > 0:
            pace_sec_per_m = self.moving_time / self.distance
            pace_sec_per_km = pace_sec_per_m * 1000
            
            minutes = int(pace_sec_per_km // 60)
            seconds = int(pace_sec_per_km % 60)
            return f"{minutes:02d}:{seconds:02d}"
        return "N/A"

    def __str__(self):
        return self.name