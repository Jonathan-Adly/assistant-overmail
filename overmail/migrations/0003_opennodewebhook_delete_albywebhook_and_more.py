# Generated by Django 4.2.10 on 2024-02-21 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('overmail', '0002_delete_emailwebhook'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenNodeWebhook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('charge_id', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('received_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='AlbyWebhook',
        ),
        migrations.AlterField(
            model_name='stripewebhook',
            name='event_id',
            field=models.CharField(max_length=255),
        ),
    ]
