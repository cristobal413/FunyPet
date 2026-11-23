from django.contrib import admin
from .models import CitaPeluqueria, Medicamento, Producto, ServicioPeluqueria, TipoMascota


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio_unitario", "stock")
    list_filter = ("categoria", "mascotas")
    search_fields = ("nombre",)
    ordering = ("nombre",)
    filter_horizontal = ("mascotas",)


@admin.register(TipoMascota)
class TipoMascotaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    ordering = ("nombre",)


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    fields = ("nombre", "volumen_ml", "precio")
    list_display = ("nombre", "volumen_ml", "precio")
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(ServicioPeluqueria)
class ServicioPeluqueriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio_base", "tiempo_base_minutos")
    search_fields = ("nombre", "descripcion")
    ordering = ("nombre",)


@admin.register(CitaPeluqueria)
class CitaPeluqueriaAdmin(admin.ModelAdmin):
    list_display = ("nombre_mascota", "nombre_dueno", "fecha", "hora", "precio_estimado")
    list_filter = ("fecha",)
    search_fields = ("nombre_mascota", "nombre_dueno", "telefono", "correo_electronico")
    ordering = ("fecha", "hora")
    filter_horizontal = ("servicios",)
    readonly_fields = ("creada_en",)