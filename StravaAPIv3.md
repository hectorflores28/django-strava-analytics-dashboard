# Strava API v3 - Summary

## Overview
The Strava API v3 allows developers to interact with Strava data. All requests require authentication via OAuth2. Key features include activity tracking, athlete profiles, clubs, segments, and more.

## Authentication
- All requests require an OAuth2 access token
- Different scopes required for different endpoints (e.g., `activity:read`, `profile:read_all`)
- Getting Started Guide available for new developers
- Swagger Playground available for testing

## Endpoints Summary

### Activities
- **Create Activity** (`POST /activities`) - Create manual activities
- **Get Activity** (`GET /activities/{id}`) - Retrieve specific activity
- **List Activity Comments** (`GET /activities/{id}/comments`) - Get activity comments
- **List Activity Kudoers** (`GET /activities/{id}/kudos`) - Get athletes who kudoed
- **List Activity Laps** (`GET /activities/{id}/laps`) - Get activity laps
- **List Athlete Activities** (`GET /athlete/activities`) - Get authenticated athlete's activities
- **Get Activity Zones** (`GET /activities/{id}/zones`) - Get activity zones (Summit feature)
- **Update Activity** (`PUT /activities/{id}`) - Update activity details

### Athletes
- **Get Authenticated Athlete** (`GET /athlete`) - Get current athlete profile
- **Get Zones** (`GET /athlete/zones`) - Get heart rate and power zones
- **Get Athlete Stats** (`GET /athletes/{id}/stats`) - Get athlete statistics
- **Update Athlete** (`PUT /athlete`) - Update athlete profile

### Clubs
- **List Club Activities** (`GET /clubs/{id}/activities`) - Get recent club activities
- **List Club Administrators** (`GET /clubs/{id}/admins`) - Get club admins
- **Get Club** (`GET /clubs/{id}`) - Get club details
- **List Club Members** (`GET /clubs/{id}/members`) - Get club members
- **List Athlete Clubs** (`GET /athlete/clubs`) - Get athlete's clubs

### Gears
- **Get Equipment** (`GET /gear/{id}`) - Get gear information

### Routes
- **Export Route GPX** (`GET /routes/{id}/export_gpx`) - Export route as GPX
- **Export Route TCX** (`GET /routes/{id}/export_tcx`) - Export route as TCX
- **Get Route** (`GET /routes/{id}`) - Get route details
- **List Athlete Routes** (`GET /athletes/{id}/routes`) - Get athlete's routes

### Segment Efforts
- **List Segment Efforts** (`GET /segment_efforts`) - Get segment efforts
- **Get Segment Effort** (`GET /segment_efforts/{id}`) - Get specific segment effort

### Segments
- **Explore Segments** (`GET /segments/explore`) - Discover segments by area
- **List Starred Segments** (`GET /segments/starred`) - Get athlete's starred segments
- **Get Segment** (`GET /segments/{id}`) - Get segment details
- **Star Segment** (`PUT /segments/{id}/starred`) - Star/unstar a segment

### Streams
- **Get Activity Streams** (`GET /activities/{id}/streams`) - Get activity data streams
- **Get Route Streams** (`GET /routes/{id}/streams`) - Get route data streams
- **Get Segment Effort Streams** (`GET /segment_efforts/{id}/streams`) - Get segment effort streams
- **Get Segment Streams** (`GET /segments/{id}/streams`) - Get segment streams

### Uploads
- **Upload Activity** (`POST /uploads`) - Upload activity data files
- **Get Upload** (`GET /uploads/{uploadId}`) - Get upload status

## Common Parameters
- `id`: Resource identifier (path parameter)
- `page`: Pagination page number
- `per_page`: Items per page (default: 30)
- Various filtering parameters for time, location, etc.

## Response Types
The API returns various structured objects including:
- DetailedActivity, SummaryActivity
- DetailedAthlete, SummaryAthlete  
- DetailedSegment, SummarySegment
- Club objects
- Gear objects
- Stream data objects
- And many more

## Rate Limits
The API enforces rate limits (details in official documentation)

## Support
- Contact: developers@strava.com
- Documentation: https://developers.strava.com
- Getting Started Guide available for newcomers