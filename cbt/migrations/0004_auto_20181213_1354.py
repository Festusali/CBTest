# Generated by Django 2.0.7 on 2018-12-13 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbt', '0003_auto_20181213_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseresult',
            name='grade',
            field=models.CharField(blank=True, help_text='What is the grade?', max_length=2, null=True),
        ),
    ]
