# Generated by Django 5.1.3 on 2024-11-29 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_alter_tvshow_finish_time_alter_tvshow_start_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='tvshow',
            name='main_category',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='tvshow',
            name='name',
            field=models.CharField(max_length=300),
        ),
    ]
