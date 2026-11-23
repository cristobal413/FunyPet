from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .forms import InicioSesionForm

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=InicioSesionForm,
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('accounts/registro/', views.registro_cliente, name='registro_cliente'),
    path('inventario/', views.modulo_inventario_carrito, name='inventario_carrito'),
    path('medicamentos/', views.modulo_cotizador_medicamentos, name='cotizador_medicamentos'),
    path('peluqueria/', views.modulo_peluqueria, name='peluqueria'),
]