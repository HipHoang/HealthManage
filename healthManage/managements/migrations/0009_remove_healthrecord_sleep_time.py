# Generated by Django 5.1.2 on 2025-06-05 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managements', '0008_alter_healthdiary_options_alter_usergoal_goal_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='healthrecord',
            name='sleep_time',
        ),
    ]
