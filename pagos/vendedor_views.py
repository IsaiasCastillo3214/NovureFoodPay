from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .forms import VendedorUsuarioForm
from .models import (
    Pedido,
    Vendedor,
)
from .permissions import (
    dueno_required,
    negocio_activo_required,
    obtener_negocio_activo,
)


# ============================================================
# CRUD VENDEDORES
# ============================================================

@dueno_required
@negocio_activo_required
def vendedores_lista(request):
    negocio = obtener_negocio_activo(request)

    vendedores = (
        Vendedor.objects
        .filter(negocio=negocio)
        .select_related('usuario', 'negocio')
        .order_by('nombre')
    )

    context = {
        'vendedores': vendedores,
    }

    return render(request, 'pagos/vendedores_lista.html', context)


@dueno_required
@negocio_activo_required
def vendedor_crear(request):
    negocio = obtener_negocio_activo(request)

    if request.method == 'POST':
        form = VendedorUsuarioForm(request.POST, negocio=negocio)

        if form.is_valid():
            form.save()
            messages.success(request, 'Vendedor creado correctamente.')
            return redirect('vendedores_lista')

    else:
        form = VendedorUsuarioForm(negocio=negocio)

    context = {
        'form': form,
        'titulo': 'Crear vendedor',
        'boton': 'Guardar vendedor',
        'editando': False,
    }

    return render(request, 'pagos/vendedor_form.html', context)


@dueno_required
@negocio_activo_required
def vendedor_editar(request, vendedor_id):
    negocio = obtener_negocio_activo(request)

    vendedor = get_object_or_404(
        Vendedor,
        id=vendedor_id,
        negocio=negocio
    )

    if request.method == 'POST':
        form = VendedorUsuarioForm(
            request.POST,
            instance=vendedor,
            negocio=negocio
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Vendedor actualizado correctamente.')
            return redirect('vendedores_lista')

    else:
        form = VendedorUsuarioForm(
            instance=vendedor,
            negocio=negocio
        )

    context = {
        'form': form,
        'titulo': 'Editar vendedor',
        'boton': 'Actualizar vendedor',
        'editando': True,
    }

    return render(request, 'pagos/vendedor_form.html', context)


@dueno_required
@negocio_activo_required
def vendedor_eliminar(request, vendedor_id):
    negocio = obtener_negocio_activo(request)

    vendedor = get_object_or_404(
        Vendedor.objects.select_related('usuario', 'negocio'),
        id=vendedor_id,
        negocio=negocio
    )

    if request.method == 'POST':
        usuario = vendedor.usuario

        tiene_pedidos = Pedido.objects.filter(
            negocio=negocio,
            vendedor=vendedor
        ).exists()

        if tiene_pedidos:
            if usuario:
                usuario.is_active = False
                usuario.save(update_fields=['is_active'])

            messages.warning(
                request,
                'Este vendedor tiene pedidos asociados. No fue eliminado, pero su usuario fue desactivado.'
            )

            return redirect('vendedores_lista')

        vendedor.delete()

        if usuario:
            usuario.delete()

        messages.success(request, 'Vendedor eliminado correctamente.')
        return redirect('vendedores_lista')

    context = {
        'vendedor': vendedor,
    }

    return render(
        request,
        'pagos/vendedor_confirmar_eliminar.html',
        context
    )
