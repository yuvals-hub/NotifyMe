from django.contrib import admin
from embed_video.admin import AdminVideoMixin
from .models import YoutubeSet

# Register your models here.

class YoutubeSetAdmin(AdminVideoMixin, admin.ModelAdmin):
    pass

admin.site.register(YoutubeSet, YoutubeSetAdmin)