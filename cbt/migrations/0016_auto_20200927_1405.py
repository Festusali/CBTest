# Generated by Django 2.2.11 on 2020-09-27 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbt', '0015_auto_20190111_0428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='is_answer',
            field=models.BooleanField(blank=True, default=False, help_text='Is the answer correct?'),
        ),
    ]
