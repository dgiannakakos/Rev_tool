from django.urls import path
from . import views  # Ensure `views.py` exists in `kpis` app

urlpatterns = [
    # KPI Endpoints
    path('kpis/', views.get_kpis, name='get_kpis'),
    path('submit_kpis/', views.submit_kpi_data, name='submit_kpi_data'),

    # Barriers and Disadvantages
    path('barriers/', views.get_barriers, name='get_barriers'),
    path('submit_barriers/', views.submit_barriers_data, name='submit_barriers_data'),

    # Climate Vulnerability
    path('climate_vulnerability/', views.get_climate_vulnerability, name='get_climate_vulnerability'),
    path('submit_climate_vulnerability/', views.submit_climate_vulnerability, name='submit_climate_vulnerability'),

    # Weather variables
    path('weather_variables/', views.get_weather_variables, name='get_weather_variables')
]