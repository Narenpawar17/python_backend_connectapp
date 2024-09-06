# Generated by Django 5.1 on 2024-09-01 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0002_tag_remove_user_tags_user_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='tags',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
        migrations.AddField(
            model_name='user',
            name='tags',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
