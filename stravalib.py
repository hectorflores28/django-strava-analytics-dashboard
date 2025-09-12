from stravalib.client import Client

# Initialize the client with your access token
client = Client(access_token="YOUR_ACCESS_TOKEN")

# Fetch athlete's activities
activities = client.get_activities(limit=10)

for activity in activities:
    print(f"Activity Name: {activity.name}, Type: {activity.type}")
