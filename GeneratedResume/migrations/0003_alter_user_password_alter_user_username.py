# Generated by Django 5.1.6 on 2025-03-13 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GeneratedResume', '0002_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]
