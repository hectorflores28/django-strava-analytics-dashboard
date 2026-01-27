1. Bitmap (Longitud y Latitud, Graficar, Tomar cada registro individual)
2. Comparativa
    - Si tienes datos GPS, aquí puedes dibujar la ruta:
    - var route = [[lat1, lon1], [lat2, lon2], ...];
    - L.polyline(route, {color: 'red'}).addTo(map);