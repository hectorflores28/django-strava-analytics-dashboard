from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_strava, name='login'),
    path('callback/', views.strava_callback, name='strava_callback'),
    path('logout/', views.logout_view, name='logout'),
    
    # Vistas Principales (Asumiendo que las vistas principales de Django migran aquí)
    path('', views.index, name='index'), # Dashboard
    path('activities/', views.activities_list, name='activities'),
    path('activities/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('monthly/', views.monthly_view, name='monthly_view'),
    path('weekly/', views.weekly_view, name='weekly_view'), # Aún por implementar

    # Tarea de sincronización
    path('refresh/', views.refresh_activities_view, name='refresh_activities'),
]