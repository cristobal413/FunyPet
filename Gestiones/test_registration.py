from django.contrib.auth import get_user_model
from django.test import TestCase

from .forms import RegistroClienteForm
from .models import Producto


class RegistroClienteTests(TestCase):
    def test_cliente_crea_cuenta_con_su_contrasena_y_inicia_sesion(self):
        producto = Producto.objects.create(
            nombre='Alimento',
            categoria='Alimento',
            precio_unitario=10000,
            stock=1,
        )
        response = self.client.post('/accounts/registro/', {
            'username': 'Ana',
            'password1': 'Mascotas2026Segura',
            'password2': 'Mascotas2026Segura',
        })

        self.assertRedirects(response, '/inventario/')
        usuario = get_user_model().objects.get(username='Ana')
        self.assertTrue(usuario.check_password('Mascotas2026Segura'))
        self.assertTrue(self.client.get('/').context['user'].is_authenticated)
        carrito = self.client.post('/inventario/', {
            'tipo_despacho': 'retiro',
            f'producto_{producto.id}': '1',
        })
        self.assertEqual(carrito.context['descuento_carrito'], 3500)

    def test_no_crea_cuenta_si_las_contrasenas_no_coinciden(self):
        response = self.client.post('/accounts/registro/', {
            'username': 'Ana',
            'password1': 'Mascotas2026!Segura',
            'password2': 'OtraClave2026!Segura',
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('password2', response.context['form'].errors)
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_nombre_corto_sin_simbolos_es_valido(self):
        form = RegistroClienteForm(data={
            'username': 'Ana',
            'password1': 'Mascotas2026Segura',
            'password2': 'Mascotas2026Segura',
        })

        self.assertTrue(form.is_valid(), form.errors)

    def test_contrasena_numerica_de_seis_caracteres_es_valida(self):
        form = RegistroClienteForm(data={
            'username': 'Ana',
            'password1': '246810',
            'password2': '246810',
        })

        self.assertTrue(form.is_valid(), form.errors)

    def test_contrasena_menor_a_seis_caracteres_no_es_valida(self):
        form = RegistroClienteForm(data={
            'username': 'Ana',
            'password1': '12345',
            'password2': '12345',
        })

        self.assertIn('password2', form.errors)

    def test_nombre_con_simbolos_o_muy_largo_no_es_valido(self):
        for username in ('Ana_1', 'A' * 21):
            with self.subTest(username=username):
                form = RegistroClienteForm(data={
                    'username': username,
                    'password1': 'Mascotas2026Segura',
                    'password2': 'Mascotas2026Segura',
                })
                self.assertIn('username', form.errors)
