from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Gestiones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviciopeluqueria',
            name='descripcion',
            field=models.CharField(blank=True, max_length=250, verbose_name='Descripción breve'),
        ),
    ]
