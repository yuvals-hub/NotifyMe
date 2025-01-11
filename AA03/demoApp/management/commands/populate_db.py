from django.core.management.base import BaseCommand
from demoApp.models import CameraSet
from demoApp.models import YoutubeSet
import requests

# run 
# python manage.py populate_db
# to update database

class Command(BaseCommand):
    help = 'Populates the database with data from an API'

    def handle(self, *args, **options):
        response = requests.get('https://511on.ca/api/v2/get/cameras')
        data = response.json()

        for item in data:
            camera = CameraSet(
                latitude=item['Latitude'],
                longitude=item['Longitude'],
                status=item['Status'],
                cam_url=item['Url'],
                cam_name=item['Name']
            )
            camera.save()

    def youtube():

        allFeeds = [
            ['nyc', 'Time Square', 40.758, -73.9855, 'USA', 'https://www.youtube.com/watch?v=1-iS7LArMPA'],
            ['blueM', 'Blue Mountain Ski Resort', 44.5038, -80.3122, 'Canada', 'https://www.youtube.com/watch?v=2FC794xcbIo'],
            ['fortL', 'Fort Lauderdale Beach', 26.1625, -80.1003, 'USA', 'https://www.youtube.com/watch?v=WBvHHNXXeqw'],
            ['hollywoodB', 'Hollywood Beach BoardWalk', 26.0087, -80.117, 'USA', 'https://www.youtube.com/watch?v=cmkAbDUEoyA'],
            ['keyWest', 'Duval Street Keywest', 24.5591, -81.805, 'USA', 'https://www.youtube.com/watch?v=cI5EqFMJaMI'],
            ['deerfield', 'Deerfield Beach', 42.171139, -87.844513, 'USA', 'https://www.youtube.com/watch?v=-HAi_5IIAYg&ab_channel=CityofDeerfieldBeach'],
            ['kabukicho', 'Kabukicho Tokyo', 36.6961, 139.7026, 'Japan', 'https://www.youtube.com/watch?v=EHkMjfMw7oU&ab_channel=KABUKICHO'],
            ['niagra', 'Niagra Falls', 43.0896, 79.0849, 'Canada', 'https://www.youtube.com/watch?v=kxwuFPFUZyY&ab_channel=NiagaraFallsLive']
        ]

        for feed in allFeeds:
            video_id = feed[0]
            title = feed[1]
            latitude = feed[2]
            longitude = feed[3]
            country = feed[4]
            video = feed[5]

            # check if there is already an instance with the same video_id
            try:
                instance = YoutubeSet.objects.get(video_id=video_id)
            except YoutubeSet.DoesNotExist:
                instance = None

            # if instance exists, update it with new values
            if instance:
                instance.title = title
                instance.latitude = latitude
                instance.longitude = longitude
                instance.country = country
                instance.video = video
                instance.save()

            # if instance doesn't exist, create a new one
            else:
                feed = YoutubeSet(
                    video_id=video_id,
                    title=title,
                    latitude=latitude,
                    longitude=longitude,
                    country=country,
                    video=video
                )
                feed.save()
    
    youtube()