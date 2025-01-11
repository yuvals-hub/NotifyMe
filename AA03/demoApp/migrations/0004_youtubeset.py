# Generated by Django 3.1.7 on 2023-04-01 19:10

from django.db import migrations, models
import embed_video.fields


class Migration(migrations.Migration):

    dependencies = [
        ('demoApp', '0003_auto_20230216_2148'),
    ]

    operations = [
        migrations.CreateModel(
            name='YoutubeSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_id', models.CharField(max_length=50)),
                ('title', models.CharField(max_length=200)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('country', models.CharField(blank=True, default='Country NA', max_length=50)),
                ('video', embed_video.fields.EmbedVideoField(blank=True)),
            ],
        ),
    ]
