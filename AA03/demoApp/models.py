from django.db import models
from embed_video.fields import EmbedVideoField

# when anything is changed, run the following:
# python mange.py makemigrations
# python manage.py migrate

# to populate database see populate_db.py

# Create your models here.

class CameraSet(models.Model):
  latitude = models.FloatField()
  longitude = models.FloatField()
  status = models.CharField(max_length=10)
  cam_url = models.CharField(max_length=100)
  cam_name = models.CharField(max_length=100)

class YoutubeSet(models.Model):
  video_id = models.CharField(max_length = 50)
  title = models.CharField(max_length = 200)
  latitude = models.FloatField()
  longitude = models.FloatField()
  country = models.CharField(max_length = 50, blank = True, default = 'Country NA')
  #timestamp = models.DateTimeField(auto_now_add=True)
  video = EmbedVideoField(blank = True)

