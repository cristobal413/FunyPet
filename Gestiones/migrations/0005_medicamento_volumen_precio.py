import decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Gestiones', '0004_citapeluqueria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicamento',
            name='dosis_recomendada',
            field=models.FloatField(blank=True, help_text='Dosis estándar en mg/kg', null=True),
        ),
        migrations.AlterField(
            model_name='medicamento',
            name='costo_por_mg',
            field=models.FloatField(blank=True, help_text='Costo unitario por miligramo (CLP)', null=True),
        ),
        migrations.AddField(
            model_name='medicamento',
            name='volumen_ml',
            field=models.DecimalField(
                decimal_places=2,
                help_text='Cantidad total de medicamento que trae el envase.',
                max_digits=8,
                null=True,
                validators=[MinValueValidator(decimal.Decimal('0.01'))],
                verbose_name='Contenido del envase (ml)',
            ),
        ),
        migrations.AddField(
            model_name='medicamento',
            name='precio',
            field=models.PositiveIntegerField(
                help_text='Precio total del envase en pesos chilenos.',
                null=True,
                validators=[MinValueValidator(1)],
                verbose_name='Precio del envase (CLP)',
            ),
        ),
    ]
