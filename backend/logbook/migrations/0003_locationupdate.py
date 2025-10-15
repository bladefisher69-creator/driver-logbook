from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('logbook', '0002_trip_coords'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('accuracy', models.FloatField(blank=True, null=True)),
                ('speed', models.FloatField(blank=True, null=True)),
                ('recorded_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_updates', to='logbook.driver')),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='logbook.trip')),
            ],
            options={'db_table': 'location_updates', 'ordering': ['-recorded_at']},
        ),
        migrations.AddIndex(
            model_name='locationupdate',
            index=models.Index(fields=['trip', 'recorded_at'], name='logbook_loc_trip_rec_1234ab'),
        ),
        migrations.AddIndex(
            model_name='locationupdate',
            index=models.Index(fields=['driver', 'recorded_at'], name='logbook_loc_drv_rec_5678cd'),
        ),
    ]
