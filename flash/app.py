import os
from flask import Flask, redirect, request, url_for, render_template
from stravalib.client import Client
from config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET

app = Flask(__name__)

REDIRECT_URI = 'http://127.0.0.1:5000/callback'

strava_token = None

@app.route('/')
def index():
    """Ruta de inicio. Redirige al usuario a Strava para la autorización."""
    client = Client()
    
    authorize_url = client.get_authorization_url(
        client_id=STRAVA_CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=['activity:read_all']
    )
    
    return render_template('index.html', authorize_url=authorize_url)

@app.route('/callback')
def callback():
    """Ruta de retorno después de la autorización de Strava."""
    global strava_token
    
    code = request.args.get('code')
    
    if code:
        client = Client()
        
        token_response = client.exchange_code_for_token(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            code=code
        )
        
        strava_token = token_response['access_token']
        
        return redirect(url_for('dashboard'))
    
    return 'Error de autenticación con Strava.'

@app.route('/dashboard')
def dashboard():
    """Muestra un ejemplo de cómo obtener las actividades del usuario."""
    if not strava_token:
        return 'No hay token de acceso. Por favor, autoriza la aplicación primero.', 401
    
    try:
        client = Client(access_token=strava_token)
        
        activities = client.get_activities(limit=5)
        
        activity_list = []
        for activity in activities:
            activity_list.append({
                'name': activity.name,
                'type': activity.type,
                'distance': activity.distance.kilometers,
                'start_date': activity.start_date_local.strftime('%Y-%m-%d %H:%M')
            })

        return render_template('dashboard.html', activities=activity_list)

    except Exception as e:
        return f"Ocurrió un error al obtener las actividades: {e}"

if __name__ == '__main__':
    app.run(debug=True)