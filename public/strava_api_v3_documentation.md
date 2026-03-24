# Resumen de la API de Strava v3

## Descripción General
La API de Strava v3 permite a los desarrolladores interactuar con los datos de Strava. Todas las solicitudes requieren autenticación mediante OAuth2. Las características principales incluyen seguimiento de actividades, perfiles de atletas, clubes, segmentos y más.

## Autenticación
- Todas las solicitudes requieren un token de acceso OAuth2
- Se requieren diferentes alcances (scopes) para diferentes endpoints (ej: `activity:read`, `profile:read_all`)
- Guía de Introducción disponible para nuevos desarrolladores
- Playground de Swagger disponible para pruebas

## Resumen de Endpoints

### Actividades
- **Crear Actividad** (`POST /activities`) - Crear actividades manuales
- **Obtener Actividad** (`GET /activities/{id}`) - Recuperar actividad específica
- **Listar Comentarios de Actividad** (`GET /activities/{id}/comments`) - Obtener comentarios de actividad
- **Listar Kudos de Actividad** (`GET /activities/{id}/kudos`) - Obtener atletas que dieron kudos
- **Listar Vueltas de Actividad** (`GET /activities/{id}/laps`) - Obtener vueltas de actividad
- **Listar Actividades del Atleta** (`GET /athlete/activities`) - Obtener actividades del atleta autenticado
- **Obtener Zonas de Actividad** (`GET /activities/{id}/zones`) - Obtener zonas de actividad (función Summit)
- **Actualizar Actividad** (`PUT /activities/{id}`) - Actualizar detalles de actividad

### Atletas
- **Obtener Atleta Autenticado** (`GET /athlete`) - Obtener perfil del atleta actual
- **Obtener Zonas** (`GET /athlete/zones`) - Obtener zonas de frecuencia cardíaca y potencia
- **Obtener Estadísticas del Atleta** (`GET /athletes/{id}/stats`) - Obtener estadísticas del atleta
- **Actualizar Atleta** (`PUT /athlete`) - Actualizar perfil del atleta

### Clubes
- **Listar Actividades del Club** (`GET /clubs/{id}/activities`) - Obtener actividades recientes del club
- **Listar Administradores del Club** (`GET /clubs/{id}/admins`) - Obtener administradores del club
- **Obtener Club** (`GET /clubs/{id}`) - Obtener detalles del club
- **Listar Miembros del Club** (`GET /clubs/{id}/members`) - Obtener miembros del club
- **Listar Clubes del Atleta** (`GET /athlete/clubs`) - Obtener clubes del atleta

### Equipamiento
- **Obtener Equipamiento** (`GET /gear/{id}`) - Obtener información del equipamiento

### Rutas
- **Exportar Ruta GPX** (`GET /routes/{id}/export_gpx`) - Exportar ruta como GPX
- **Exportar Ruta TCX** (`GET /routes/{id}/export_tcx`) - Exportar ruta como TCX
- **Obtener Ruta** (`GET /routes/{id}`) - Obtener detalles de la ruta
- **Listar Rutas del Atleta** (`GET /athletes/{id}/routes`) - Obtener rutas del atleta

### Esfuerzos en Segmentos
- **Listar Esfuerzos en Segmentos** (`GET /segment_efforts`) - Obtener esfuerzos en segmentos
- **Obtener Esfuerzo en Segmento** (`GET /segment_efforts/{id}`) - Obtener esfuerzo específico en segmento

### Segmentos
- **Explorar Segmentos** (`GET /segments/explore`) - Descubrir segmentos por área
- **Listar Segmentos Favoritos** (`GET /segments/starred`) - Obtener segmentos favoritos del atleta
- **Obtener Segmento** (`GET /segments/{id}`) - Obtener detalles del segmento
- **Marcar Segmento como Favorito** (`PUT /segments/{id}/starred`) - Marcar/desmarcar segmento como favorito

### Streams (Flujos de Datos)
- **Obtener Streams de Actividad** (`GET /activities/{id}/streams`) - Obtener flujos de datos de actividad
- **Obtener Streams de Ruta** (`GET /routes/{id}/streams`) - Obtener flujos de datos de ruta
- **Obtener Streams de Esfuerzo en Segmento** (`GET /segment_efforts/{id}/streams`) - Obtener flujos de datos de esfuerzo en segmento
- **Obtener Streams de Segmento** (`GET /segments/{id}/streams`) - Obtener flujos de datos de segmento

### Cargas
- **Cargar Actividad** (`POST /uploads`) - Cargar archivos de datos de actividad
- **Obtener Estado de Carga** (`GET /uploads/{uploadId}`) - Obtener estado de carga

## Parámetros Comunes
- `id`: Identificador de recurso (parámetro de ruta)
- `page`: Número de página para paginación
- `per_page`: Elementos por página (predeterminado: 30)
- Varios parámetros de filtrado para tiempo, ubicación, etc.

## Tipos de Respuesta
La API devuelve varios objetos estructurados que incluyen:
- DetailedActivity, SummaryActivity
- DetailedAthlete, SummaryAthlete
- DetailedSegment, SummarySegment
- Objetos Club
- Objetos Gear (Equipamiento)
- Objetos de datos Stream
- Y muchos más

## Límites de Tasa de Solicitud
La API aplica límites de tasa (detalles en la documentación oficial)

## Soporte
- Contacto: developers@strava.com
- Documentación: https://developers.strava.com
- Guía de Introducción disponible para nuevos usuarios