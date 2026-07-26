from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ProductoForm
from .models import Producto
from .permissions import (
    dueno_required,
    negocio_activo_required,
    obtener_negocio_activo,
)


# ============================================================
# CRUD PRODUCTOS
# ============================================================

@dueno_required
@negocio_activo_required
def productos_lista(request):
    negocio = obtener_negocio_activo(request)

    productos = Producto.objects.filter(
        negocio=negocio
    ).order_by('nombre')

    context = {
        'productos': productos,
    }

    return render(request, 'pagos/productos_lista.html', context)


@dueno_required
@negocio_activo_required
def producto_crear(request):
    negocio = obtener_negocio_activo(request)

    if request.method == 'POST':
        form = ProductoForm(request.POST, negocio=negocio)

        if form.is_valid():
            producto = form.save(commit=False)
            producto.negocio = negocio
            producto.save()

            messages.success(request, 'Producto creado correctamente.')
            return redirect('productos_lista')

    else:
        form = ProductoForm(negocio=negocio)

    context = {
        'form': form,
        'titulo': 'Crear producto',
        'boton': 'Guardar producto',
    }

    return render(request, 'pagos/producto_form.html', context)


@dueno_required
@negocio_activo_required
def producto_editar(request, producto_id):
    negocio = obtener_negocio_activo(request)

    producto = get_object_or_404(
        Producto,
        id=producto_id,
        negocio=negocio
    )

    if request.method == 'POST':
        form = ProductoForm(
            request.POST,
            instance=producto,
            negocio=negocio
        )

        if form.is_valid():
            producto = form.save(commit=False)
            producto.negocio = negocio
            producto.save()

            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('productos_lista')

    else:
        form = ProductoForm(instance=producto, negocio=negocio)

    context = {
        'form': form,
        'titulo': 'Editar producto',
        'boton': 'Actualizar producto',
    }

    return render(request, 'pagos/producto_form.html', context)


@dueno_required
@negocio_activo_required
def producto_eliminar(request, producto_id):
    negocio = obtener_negocio_activo(request)

    producto = get_object_or_404(
        Producto,
        id=producto_id,
        negocio=negocio
    )

    if request.method == 'POST':
        try:
            producto.delete()
            messages.success(
                request,
                'Producto eliminado correctamente.'
            )

        except ProtectedError:
            producto.activo = False
            producto.save(update_fields=['activo'])

            messages.warning(
                request,
                'Este producto ya tiene ventas asociadas. No se eliminó, pero fue marcado como inactivo.'
            )

        return redirect('productos_lista')

    context = {
        'producto': producto,
    }

    return render(
        request,
        'pagos/producto_confirmar_eliminar.html',
        context
    )
