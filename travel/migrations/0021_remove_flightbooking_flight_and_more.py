# Generated by Django 5.1.6 on 2025-03-18 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0020_alter_flight_flightnumber_alter_flightbooking_flight_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flightbooking',
            name='flight',
        ),
        migrations.RemoveField(
            model_name='flightbooking',
            name='user',
        ),
        migrations.DeleteModel(
            name='Flight',
        ),
        migrations.DeleteModel(
            name='FlightBooking',
        ),
    ]
