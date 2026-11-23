from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Medicamento


class MedicamentoAdminTests(TestCase):
    def test_admin_crea_medicamento_con_ml_y_precio_sin_datos_en_mg(self):
        usuario = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='clave-segura-123',
        )
        self.client.force_login(usuario)

        response = self.client.post(reverse('admin:Gestiones_medicamento_add'), {
            'nombre': 'Jarabe',
            'volumen_ml': '100.00',
            'precio': '15000',
            '_save': 'Guardar',
        })

        self.assertEqual(response.status_code, 302)
        medicamento = Medicamento.objects.get(nombre='Jarabe')
        self.assertEqual(medicamento.volumen_ml, Decimal('100.00'))
        self.assertEqual(medicamento.precio, 15000)
        self.assertIsNone(medicamento.dosis_recomendada)
        self.assertIsNone(medicamento.costo_por_mg)

    def test_admin_solo_muestra_nombre_contenido_y_precio(self):
        medicamento_admin = admin.site._registry[Medicamento]

        self.assertEqual(medicamento_admin.fields, ('nombre', 'volumen_ml', 'precio'))


class CotizadorMedicamentosTests(TestCase):
    def test_calcula_costo_proporcional_a_los_ml_indicados(self):
        medicamento = Medicamento.objects.create(
            nombre='Jarabe',
            volumen_ml=Decimal('100.00'),
            precio=15000,
        )

        response = self.client.post('/medicamentos/', {
            'medicamento': medicamento.id,
            'dosis_ml': '2.5',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['resultado']['costo_total'], Decimal('375.00'))
