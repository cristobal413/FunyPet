from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class TipoMascota(models.Model):
    TIPOS = [
        ('Perro', 'Perro'),
        ('Gato', 'Gato'),
        ('Ave', 'Ave'),
        ('Conejo', 'Conejo'),
        ('Roedor', 'Roedor'),
        ('Reptil', 'Reptil'),
        ('Otro', 'Otro'),
    ]
    nombre = models.CharField(max_length=20, choices=TIPOS, unique=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    CATEGORIAS = [
        ('Alimento', 'Alimento'),
        ('Juguete', 'Juguete'),
        ('Accesorio', 'Accesorio'),
    ]
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    precio_unitario = models.PositiveIntegerField(help_text="Precio en pesos chilenos (CLP)")
    stock = models.PositiveIntegerField(default=0)
    mascotas = models.ManyToManyField(TipoMascota, blank=True, related_name='productos')

    def __str__(self):
        return f"{self.nombre} (${self.precio_unitario})"


class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)
    dosis_recomendada = models.FloatField(
        help_text="Dosis estándar en mg/kg",
        null=True,
        blank=True,
    )
    costo_por_mg = models.FloatField(
        help_text="Costo unitario por miligramo (CLP)",
        null=True,
        blank=True,
    )
    volumen_ml = models.DecimalField(
        "Contenido del envase (ml)",
        max_digits=8,
        decimal_places=2,
        help_text="Cantidad total de medicamento que trae el envase.",
        null=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    precio = models.PositiveIntegerField(
        "Precio del envase (CLP)",
        help_text="Precio total del envase en pesos chilenos.",
        null=True,
        validators=[MinValueValidator(1)],
    )

    def __str__(self):
        return self.nombre


class ServicioPeluqueria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField("Descripción breve", max_length=250, blank=True)
    precio_base = models.PositiveIntegerField(help_text="Precio base en CLP")
    tiempo_base_minutos = models.PositiveIntegerField(help_text="Tiempo base en minutos")

    def __str__(self):
        return f"{self.nombre} - {self.tiempo_base_minutos} min"


class CitaPeluqueria(models.Model):
    nombre_dueno = models.CharField(max_length=100)
    nombre_mascota = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo_electronico = models.EmailField()
    fecha = models.DateField()
    hora = models.TimeField()
    peso_mascota = models.FloatField()
    servicios = models.ManyToManyField(ServicioPeluqueria, related_name='citas')
    precio_estimado = models.PositiveIntegerField()
    tiempo_estimado_minutos = models.PositiveIntegerField()
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('fecha', 'hora')

    def __str__(self):
        return f"{self.nombre_mascota} - {self.fecha} {self.hora}"