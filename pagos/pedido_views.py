from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect

from .forms import (
    PedidoForm,
    PedidoOwnerForm,
)
from .models import Pedido
from .permissions import (
    negocio_activo_required,
    es_admin_general,
    es_dueno,
    obtener_negocio_activo,
    obtener_pedido_permitido,
    obtener_vendedor_usuario,
)
from .services import (
    obtener_lineas_productos,
    guardar_detalles_pedido,
)


# ============================================================
# PEDIDOS
# ============================================================

@login_required
@negocio_activo_required
def crear_pedido(request):
    negocio = obtener_negocio_activo(request)
    producto_error = None

    if es_dueno(request.user):
        form_class = PedidoOwnerForm
    else:
        form_class = PedidoForm

    if request.method == 'POST':
        if es_dueno(request.user):
            form = form_class(request.POST, negocio=negocio)
        else:
            form = form_class(request.POST)

        resultado_productos, producto_error = obtener_lineas_productos(
            request,
            negocio
        )

        if form.is_valid() and not producto_error:
            with transaction.atomic():
                pedido = form.save(commit=False)
                pedido.negocio = negocio

                if not es_dueno(request.user):
                    vendedor = obtener_vendedor_usuario(request.user)

                    if not vendedor or vendedor.negocio_id != negocio.id:
                        messages.error(
                            request,
                            'Tu usuario no tiene vendedor asociado a este negocio.'
                        )
                        return redirect('dashboard')

                    pedido.vendedor = vendedor

                else:
                    if pedido.vendedor.negocio_id != negocio.id:
                        messages.error(
                            request,
                            'El vendedor seleccionado no pertenece a este negocio.'
                        )
                        return redirect('crear_pedido')

                pedido.monto = resultado_productos['total']
                pedido.save()

                guardar_detalles_pedido(
                    pedido,
                    resultado_productos['lineas']
                )

            messages.success(request, 'Pedido registrado correctamente.')
            return redirect('dashboard')

    else:
        if es_dueno(request.user):
            form = form_class(negocio=negocio)
        else:
            form = form_class()

    context = {
        'form': form,
        'producto_error': producto_error,
        'titulo': 'Registrar pedido',
        'boton': 'Guardar pedido',
        'detalles_existentes': None,
        'es_dueno': es_dueno(request.user),
        'es_admin_general': es_admin_general(request.user),
    }

    return render(request, 'pagos/crear_pedido.html', context)


@login_required
@negocio_activo_required
def editar_pedido(request, pedido_id):
    negocio = obtener_negocio_activo(request)
    pedido = obtener_pedido_permitido(request, pedido_id)

    producto_error = None

    if es_dueno(request.user):
        form_class = PedidoOwnerForm
    else:
        form_class = PedidoForm

    if request.method == 'POST':
        if es_dueno(request.user):
            form = form_class(
                request.POST,
                instance=pedido,
                negocio=negocio
            )
        else:
            form = form_class(request.POST, instance=pedido)

        resultado_productos, producto_error = obtener_lineas_productos(
            request,
            negocio
        )

        if form.is_valid() and not producto_error:
            with transaction.atomic():
                pedido = form.save(commit=False)
                pedido.negocio = negocio

                if not es_dueno(request.user):
                    vendedor = obtener_vendedor_usuario(request.user)

                    if not vendedor or vendedor.negocio_id != negocio.id:
                        messages.error(
                            request,
                            'Tu usuario no tiene vendedor asociado a este negocio.'
                        )
                        return redirect('dashboard')

                    pedido.vendedor = vendedor

                else:
                    if pedido.vendedor.negocio_id != negocio.id:
                        messages.error(
                            request,
                            'El vendedor seleccionado no pertenece a este negocio.'
                        )
                        return redirect('editar_pedido', pedido_id=pedido.id)

                pedido.monto = resultado_productos['total']
                pedido.save()

                guardar_detalles_pedido(
                    pedido,
                    resultado_productos['lineas']
                )

            messages.success(request, 'Pedido actualizado correctamente.')
            return redirect('dashboard')

    else:
        if es_dueno(request.user):
            form = form_class(instance=pedido, negocio=negocio)
        else:
            form = form_class(instance=pedido)

    context = {
        'form': form,
        'producto_error': producto_error,
        'titulo': 'Editar pedido',
        'boton': 'Actualizar pedido',
        'detalles_existentes': pedido.detalles.select_related('producto').all(),
        'es_dueno': es_dueno(request.user),
        'es_admin_general': es_admin_general(request.user),
    }

    return render(request, 'pagos/crear_pedido.html', context)


@login_required
@negocio_activo_required
def eliminar_pedido(request, pedido_id):
    pedido = obtener_pedido_permitido(request, pedido_id)

    if request.method == 'POST':
        pedido.delete()
        messages.success(request, 'Pedido eliminado correctamente.')
        return redirect('dashboard')

    context = {
        'pedido': pedido,
    }

    return render(request, 'pagos/confirmar_eliminar.html', context)


@login_required
@negocio_activo_required
def actualizar_estado(request, pedido_id):
    pedido = obtener_pedido_permitido(request, pedido_id)

    if request.method == 'POST':
        nuevo_estado_pedido = request.POST.get('estado_pedido')
        nuevo_estado_pago = request.POST.get('estado_pago')

        estados_pedido_validos = [
            estado[0] for estado in Pedido.ESTADO_PEDIDO_CHOICES
        ]

        estados_pago_validos = [
            estado[0] for estado in Pedido.ESTADO_PAGO_CHOICES
        ]

        if nuevo_estado_pedido in estados_pedido_validos:
            pedido.estado_pedido = nuevo_estado_pedido

        if nuevo_estado_pago in estados_pago_validos:
            pedido.estado_pago = nuevo_estado_pago

        pedido.save()
        messages.success(request, 'Estado actualizado correctamente.')

    return redirect('dashboard')
