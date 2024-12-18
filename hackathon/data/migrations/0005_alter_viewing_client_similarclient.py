# Generated by Django 5.1.3 on 2024-11-29 14:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_alter_category_name_alter_tvshow_main_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='viewing',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='data.client'),
        ),
        migrations.CreateModel(
            name='SimilarClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similarity_score', models.FloatField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='similar_clients', to='data.client')),
                ('similar_client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='similar_to', to='data.client')),
            ],
        ),
    ]
