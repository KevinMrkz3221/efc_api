# Generated by Django 5.2.3 on 2025-07-14 16:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('almacenamiento', models.PositiveIntegerField(default=0)),
                ('archivo', models.FileField(upload_to='datastages/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organizacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datastages', to='organization.organizacion')),
            ],
            options={
                'verbose_name': 'DataStage',
                'verbose_name_plural': 'DataStages',
                'db_table': 'datastage',
            },
        ),
    ]
