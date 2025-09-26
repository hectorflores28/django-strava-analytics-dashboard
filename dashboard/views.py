import requests
import os
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from .models import Athlete, Activity
from django.db.models import Sum, Count, F, Max
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone # Usamos timezone de Django

# --- Vistas de Dashboard ---

def index(request):
    """Vista principal del Dashboard."""
    athlete, access_token = get_athlete_and_token(request)

    if not athlete:
        # Usar la plantilla de bienvenida si no está autenticado
        return render(request, 'index.html', {'is_authenticated': False})

    # 1. Calcular Fechas Clave
    today = localdate() # Fecha local para las comparaciones
    start_of_week = today - timedelta(days=today.weekday()) # Lunes
    start_of_month = today.replace(day=1)
    
    # 2. Agregación Base (DRY - Don't Repeat Yourself)
    def get_summary(start_date, end_date=today + timedelta(days=1)):
        """Función auxiliar para obtener métricas agregadas."""
        summary = Activity.objects.filter(
            athlete=athlete,
            start_date_local__gte=start_date,
            start_date_local__lt=end_date
        ).aggregate(
            count=Count('id'),
            distance=Sum('distance') / 1000.0,  # km
            elevation=Sum('total_elevation_gain'), # m
            time=Sum('moving_time') / 3600.0, # horas
        )
        # Manejar None si no hay actividades
        return {k: v if v is not None else 0 for k, v in summary.items()}

    # 3. Obtener Resúmenes
    context = {
        'today': get_summary(today),
        'this_week': get_summary(start_of_week),
        'this_month': get_summary(start_of_month),
        'athlete': athlete,
        'is_authenticated': True
    }
    
    # [TODO: Implementar lógica de Rachas (Streaks) aquí]
    # [TODO: Implementar lógica de Distribución por Tipo de Actividad para Chart.js aquí]

    return render(request, 'index.html', context)


def monthly_view(request):
    """Vista de resumen mensual."""
    athlete, access_token = get_athlete_and_token(request)

    if not athlete:
        messages.warning(request, "Please log in to see the monthly view.")
        return redirect('login')

    # Usamos F() expressions y anotaciones para agrupar y agregar en la DB
    monthly_data_raw = Activity.objects.filter(
        athlete=athlete,
        start_date_local__gte=localdate() - timedelta(days=365)
    ).extra(
        select={'month_key': "strftime('%%Y-%%m', start_date_local)"} # SQLite formatting
    ).values('month_key').annotate(
        count=Count('id'),
        distance=Sum(F('distance') / 1000.0),
        elevation=Sum('total_elevation_gain'),
        time=Sum(F('moving_time') / 3600.0)
    ).order_by('-month_key')

    # Renombrar para que coincida con la plantilla de Flask
    monthly_data = [{
        'month': item['month_key'],
        'data': {k: item[k] for k in ['count', 'distance', 'elevation', 'time']}
    } for item in monthly_data_raw]

    return render(request, 'monthly.html', {'monthly_data': monthly_data, 'athlete': athlete})

# --- Funciones Auxiliares de API (Mejor práctica: Mover a un módulo `strava_api.py`) ---

def get_session():
    """Usa requests.Session para conexiones persistentes."""
    return requests.Session()

def refresh_strava_token(athlete):
    """Refresca el token de acceso de Strava."""
    url = f"{settings.STRAVA_OAUTH_URL}/token"
    payload = {
        'client_id': settings.STRAVA_CLIENT_ID,
        'client_secret': settings.STRAVA_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': athlete.refresh_token
    }
    
    with get_session() as s:
        response = s.post(url, data=payload)
    
    response.raise_for_status()
    data = response.json()
    
    # Actualizar el objeto Athlete en la DB
    athlete.access_token = data['access_token']
    athlete.refresh_token = data.get('refresh_token', athlete.refresh_token) # A veces no cambia
    athlete.expires_at = data['expires_at']
    athlete.save()
    
    return athlete

# --- Vistas de Autenticación ---

def login_strava(request):
    """Redirige al usuario a Strava para la autenticación OAuth."""
    client_id = settings.STRAVA_CLIENT_ID
    redirect_uri = request.build_absolute_uri(reverse('strava_callback'))
    scope = "read,activity:read_all" # read_all es esencial para el dashboard

    auth_url = (
        f"{settings.STRAVA_OAUTH_URL}/authorize?"
        f"client_id={client_id}&"
        f"response_type=code&"
        f"redirect_uri={redirect_uri}&"
        f"approval_prompt=force&" # Forzar al usuario a revisar los permisos
        f"scope={scope}"
    )
    return redirect(auth_url)

@require_http_methods(["GET"])
def strava_callback(request):
    """Maneja el callback de Strava y el intercambio de código por tokens."""
    code = request.GET.get('code')
    error = request.GET.get('error')

    if error:
        messages.error(request, f"Strava authentication failed: {error}")
        return redirect('index')

    if not code:
        messages.error(request, "Authorization code missing.")
        return redirect('index')

    token_url = f"{settings.STRAVA_OAUTH_URL}/token"
    payload = {
        'client_id': settings.STRAVA_CLIENT_ID,
        'client_secret': settings.STRAVA_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
    }

    try:
        with get_session() as s:
            response = s.post(token_url, data=payload)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error exchanging code for token: {e}")
        return redirect('index')

    # Guardar o actualizar el Athlete
    athlete_data = data['athlete']
    athlete_id = athlete_data['id']
    
    # Usamos transaction.atomic para asegurar la consistencia
    with transaction.atomic():
        athlete, created = Athlete.objects.update_or_create(
            id=athlete_id,
            defaults={
                'access_token': data['access_token'],
                'refresh_token': data['refresh_token'],
                'expires_at': data['expires_at'],
                'firstname': athlete_data.get('firstname'),
                'lastname': athlete_data.get('lastname'),
                'username': athlete_data.get('username'),
                'profile': athlete_data.get('profile'),
                'profile_medium': athlete_data.get('profile_medium'),
                # ... otros campos ...
            }
        )
    
    # Iniciar sesión de Django (guardar el ID del atleta en la sesión)
    request.session['athlete_id'] = athlete_id
    messages.success(request, f"Welcome back, {athlete.firstname}!")
    
    # Iniciar la primera sincronización de datos
    return redirect(reverse('refresh_activities'))


def logout_view(request):
    """Cierra la sesión de Django."""
    if 'athlete_id' in request.session:
        del request.session['athlete_id']
    messages.info(request, "Successfully logged out.")
    return redirect('index')

def get_athlete_and_token(request):
    """Obtiene el atleta de la sesión y refresca el token si es necesario."""
    athlete_id = request.session.get('athlete_id')
    if not athlete_id:
        return None, None
        
    athlete = get_object_or_404(Athlete, id=athlete_id)
    
    if athlete.is_token_expired():
        try:
            athlete = refresh_strava_token(athlete)
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Token refresh failed. Please re-login: {e}")
            return None, None
            
    return athlete, athlete.access_token


def fetch_and_sync_activities(athlete, access_token):
    """
    Obtiene las actividades nuevas del atleta desde Strava y las sincroniza con la DB.
    Esta lógica DEBE ser reutilizada en el cron job (`daily_update.py`).
    """
    # 1. Determinar el punto de partida (after parameter de la API)
    # Buscamos la fecha de inicio más reciente en nuestra DB para este atleta
    last_activity = Activity.objects.filter(athlete=athlete).aggregate(Max('start_date'))
    # Si hay actividades, establecemos el timestamp de inicio para buscar SOLO nuevas
    after_timestamp = 0
    if last_activity['start_date__max']:
        # Convertir a timestamp UNIX, restamos un día por seguridad
        last_date = last_activity['start_date__max'] - timedelta(days=1)
        after_timestamp = int(last_date.timestamp())

    # 2. Bucle de paginación para obtener actividades
    activities_url = f"{settings.STRAVA_API_URL}/athlete/activities"
    page = 1
    new_activities_count = 0

    with get_session() as s:
        # Usamos requests.Session() para conexiones persistentes (Mejor Práctica)
        while True:
            params = {
                'page': page,
                'per_page': 50,
                'after': after_timestamp # Solo actividades después de este timestamp
            }
            headers = {'Authorization': f'Bearer {access_token}'}

            response = s.get(activities_url, headers=headers, params=params)
            response.raise_for_status()
            strava_activities = response.json()
            
            if not strava_activities:
                break # No hay más actividades

            # 3. Sincronizar con la DB
            for item in strava_activities:
                # Comprobar si ya existe (evitar duplicados, aunque el filtro `after` ya ayuda)
                if Activity.objects.filter(id=item['id']).exists():
                    continue

                # Convertir la fecha UTC (string) a objeto datetime
                start_date_utc = datetime.strptime(item['start_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                start_date_local = datetime.strptime(item['start_date_local'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                
                # Crear la actividad
                Activity.objects.create(
                    id=item['id'],
                    athlete=athlete,
                    name=item['name'],
                    distance=item['distance'],
                    moving_time=item['moving_time'],
                    elapsed_time=item['elapsed_time'],
                    total_elevation_gain=item['total_elevation_gain'],
                    type=item['type'],
                    sport_type=item['sport_type'],
                    average_speed=item['average_speed'],
                    max_speed=item['max_speed'],
                    has_heartrate=item.get('has_heartrate', False),
                    average_heartrate=item.get('average_heartrate'),
                    max_heartrate=item.get('max_heartrate'),
                    start_date=start_date_utc,
                    start_date_local=start_date_local,
                    timezone=item['timezone'],
                )
                new_activities_count += 1
                
            page += 1
            # Strava tiene un límite de 200 por página, pero 50 es más seguro.
            if len(strava_activities) < 50:
                break # Menos del límite significa que es la última página

    return new_activities_count

# --- Vista para la Sincronización Manual ---

def refresh_activities_view(request):
    """Endpoint de Django para la sincronización manual de datos."""
    athlete, access_token = get_athlete_and_token(request)

    if not athlete:
        return redirect('login') # Si no hay atleta o falla el refresh, redirigir al login

    try:
        count = fetch_and_sync_activities(athlete, access_token)
        messages.success(request, f"Data synchronization complete. {count} new activities added.")
    except requests.exceptions.HTTPError as e:
        # Manejar errores de la API (ej: 401 Unauthorized, 404 Not Found)
        messages.error(request, f"Strava API Error during sync. Status: {e.response.status_code}. Message: {e.response.text}")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred during sync: {e}")
        
    return redirect('index')