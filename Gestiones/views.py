import math
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.contrib.auth import login as auth_login
from django.db.models import Q
from django.shortcuts import redirect, render
from .forms import CitaPeluqueriaForm, RegistroClienteForm
from .models import CitaPeluqueria, Medicamento, Producto, ServicioPeluqueria, TipoMascota


COSTO_DESPACHO_DOMICILIO = 3500
PORCENTAJE_DESCUENTO_USUARIO = 35


def index(request):
    """Vista principal con acceso a los módulos del proyecto."""
    return render(request, 'Gestiones/index.html')


def registro_cliente(request):
    if request.user.is_authenticated:
        return redirect('inventario_carrito')

    form = RegistroClienteForm(data=request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        auth_login(request, usuario)
        return redirect('inventario_carrito')

    return render(request, 'registration/registro.html', {'form': form})


def modulo_inventario_carrito(request):
    """
    Módulo 1: Multiplicación de matrices y vectores (C = V * M)
    Calcula el costo del carrito de compras aplicando las cantidades seleccionadas (Vector V)
    sobre la matriz de productos e inventario (Matriz M).
    """
    tipos_mascota = TipoMascota.objects.order_by('nombre')
    mascota_id = request.POST.get('mascota', '') if request.method == 'POST' else request.GET.get('mascota', '')
    mascota_seleccionada = None
    productos = Producto.objects.all()
    total_carrito = 0
    subtotal_carrito = 0
    descuento_carrito = 0
    costo_despacho = 0
    detalle_compra = []
    error = None
    tipo_despacho = request.POST.get('tipo_despacho', '') if request.method == 'POST' else ''
    direccion_despacho = request.POST.get('direccion_despacho', '').strip() if request.method == 'POST' else ''

    if mascota_id:
        try:
            mascota_seleccionada = TipoMascota.objects.get(pk=mascota_id)
        except (TypeError, ValueError, TipoMascota.DoesNotExist):
            error = 'El tipo de mascota seleccionado no existe.'
            productos = Producto.objects.none()
        else:
            productos = productos.filter(
                Q(mascotas__isnull=True) | Q(mascotas=mascota_seleccionada)
            ).distinct()

    if request.method == 'POST':
        vector_cantidades = []
        if tipo_despacho not in ('retiro', 'domicilio'):
            error = 'Selecciona un tipo de despacho válido.'
        elif tipo_despacho == 'domicilio' and not direccion_despacho:
            error = 'Ingresa la dirección para el despacho a domicilio.'

        if error is None:
            for p in productos:
                cantidad_str = request.POST.get(f'producto_{p.id}', '0')
                try:
                    cantidad = int(cantidad_str)
                except (TypeError, ValueError):
                    error = 'Ingresa cantidades enteras iguales o mayores que cero.'
                    break

                if cantidad < 0:
                    error = 'Ingresa cantidades enteras iguales o mayores que cero.'
                    break

                if cantidad > p.stock:
                    error = f'No hay stock suficiente de {p.nombre}.'
                    break

                vector_cantidades.append(cantidad)

        if error is None:
            # Aplicando la lógica matricial C = V * M
            for i, p in enumerate(productos):
                cant = vector_cantidades[i]
                if cant > 0:
                    subtotal = cant * p.precio_unitario
                    total_carrito += subtotal
                    detalle_compra.append({
                        'nombre': p.nombre,
                        'categoria': p.categoria,
                        'precio': p.precio_unitario,
                        'cantidad': cant,
                        'subtotal': subtotal
                    })
            subtotal_carrito = total_carrito
            if request.user.is_authenticated and detalle_compra:
                descuento_carrito = (subtotal_carrito * PORCENTAJE_DESCUENTO_USUARIO + 50) // 100
                total_carrito -= descuento_carrito
            if detalle_compra and tipo_despacho == 'domicilio':
                costo_despacho = COSTO_DESPACHO_DOMICILIO
                total_carrito += costo_despacho

    context = {
        'productos': productos,
        'tipos_mascota': tipos_mascota,
        'mascota_seleccionada': mascota_seleccionada,
        'detalle_compra': detalle_compra,
        'tipo_despacho': tipo_despacho,
        'direccion_despacho': direccion_despacho,
        'subtotal_carrito': subtotal_carrito,
        'descuento_carrito': descuento_carrito,
        'porcentaje_descuento': PORCENTAJE_DESCUENTO_USUARIO,
        'costo_despacho': costo_despacho,
        'total_carrito': total_carrito,
        'error': error,
    }
    return render(request, 'Gestiones/inventario_carrito.html', context)


def modulo_cotizador_medicamentos(request):
    """Calcula el costo proporcional a partir del precio y contenido del envase."""
    medicamentos = Medicamento.objects.filter(
        volumen_ml__gt=0,
        precio__gt=0,
    ).order_by('nombre')
    resultado_cotizacion = None
    error = None

    if request.method == 'POST':
        med_id = request.POST.get('medicamento')
        try:
            med_id = int(med_id)
            dosis_ml = Decimal(request.POST.get('dosis_ml', ''))
        except (TypeError, ValueError, InvalidOperation):
            error = 'Selecciona un medicamento e ingresa una cantidad válida en ml.'
        else:
            if not dosis_ml.is_finite() or dosis_ml <= 0:
                error = 'La cantidad debe ser un número de ml mayor que cero.'
            else:
                medicamento_seleccionado = medicamentos.filter(id=med_id).first()
                if medicamento_seleccionado is None:
                    error = 'El medicamento seleccionado no existe.'
                else:
                    precio_por_ml = Decimal(medicamento_seleccionado.precio) / medicamento_seleccionado.volumen_ml
                    costo_total = (dosis_ml * precio_por_ml).quantize(
                        Decimal('0.01'),
                        rounding=ROUND_HALF_UP,
                    )

                    resultado_cotizacion = {
                        'nombre': medicamento_seleccionado.nombre,
                        'dosis_ml': dosis_ml,
                        'volumen_ml': medicamento_seleccionado.volumen_ml,
                        'precio_envase': medicamento_seleccionado.precio,
                        'precio_ml': precio_por_ml.quantize(
                            Decimal('0.01'),
                            rounding=ROUND_HALF_UP,
                        ),
                        'costo_total': costo_total,
                    }

    context = {
        'medicamentos': medicamentos,
        'resultado': resultado_cotizacion,
        'error': error,
    }
    return render(request, 'Gestiones/cotizador_medicamentos.html', context)


def modulo_peluqueria(request):
    """
    Módulo 3: Estimación conjunta de tiempo y costo de peluquería según servicios y peso.
    """
    servicios = ServicioPeluqueria.objects.all()
    estimacion = None
    error = None
    selected_servicio_ids = []
    form_cita = CitaPeluqueriaForm()
    cita_guardada = False

    if request.method == 'POST':
        selected_servicio_ids = request.POST.getlist('servicios')
        peso_str = request.POST.get('peso_peluqueria', '')

        if not selected_servicio_ids:
            error = 'Selecciona al menos un servicio.'
        else:
            try:
                selected_servicio_ids = [int(servicio_id) for servicio_id in selected_servicio_ids]
                peso = float(peso_str)
            except (TypeError, ValueError):
                error = 'Selecciona servicios válidos e ingresa un peso válido.'

            if error is None and (not math.isfinite(peso) or peso <= 0):
                error = 'El peso debe ser un número mayor que cero.'

            if error is None:
                servicios_seleccionados = list(servicios.filter(id__in=selected_servicio_ids))
                if len(servicios_seleccionados) != len(set(selected_servicio_ids)):
                    error = 'Uno o más servicios seleccionados no existen.'
                else:
                    # Factor de ajuste según el peso de la mascota
                    factor_peso = 1.0 if peso <= 10 else (1.3 if peso <= 25 else 1.6)
                    detalle_servicios = []
                    for servicio in servicios_seleccionados:
                        detalle_servicios.append({
                            'nombre': servicio.nombre,
                            'descripcion': servicio.descripcion,
                            'precio_final': int(servicio.precio_base * factor_peso),
                            'tiempo_final': int(servicio.tiempo_base_minutos * factor_peso),
                        })

                    estimacion = {
                        'servicios': detalle_servicios,
                        'peso': peso,
                        'precio_final': sum(servicio['precio_final'] for servicio in detalle_servicios),
                        'tiempo_final': sum(servicio['tiempo_final'] for servicio in detalle_servicios),
                    }

        if request.POST.get('accion') == 'guardar_cita':
            form_cita = CitaPeluqueriaForm(request.POST)
            if estimacion is not None and error is None and form_cita.is_valid():
                cita = form_cita.save(commit=False)
                cita.peso_mascota = peso
                cita.precio_estimado = estimacion['precio_final']
                cita.tiempo_estimado_minutos = estimacion['tiempo_final']
                cita.save()
                cita.servicios.set(servicios_seleccionados)
                cita_guardada = True

    context = {
        'servicios': servicios,
        'estimacion': estimacion,
        'error': error,
        'selected_servicio_ids': selected_servicio_ids,
        'form_cita': form_cita,
        'cita_guardada': cita_guardada,
    }
    return render(request, 'Gestiones/peluqueria.html', context)