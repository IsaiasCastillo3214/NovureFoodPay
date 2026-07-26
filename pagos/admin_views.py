from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .forms import (
    NegocioForm,
    DuenoNegocioUsuarioForm,
)
from .models import Negocio
from .permissions import (
    admin_general_required,
    obtener_negocio_activo,
)


# ============================================================
# ADMIN GENERAL - NEGOCIOS
# ============================================================

@admin_general_required
def negocios_lista(request):
    negocios = Negocio.objects.all().order_by('nombre')

    context = {
        'negocios': negocios,
        'negocio_activo': obtener_negocio_activo(request),
    }

    return render(request, 'pagos/negocios_lista.html', context)


@admin_general_required
def negocio_crear(request):
    if request.method == 'POST':
        form = NegocioForm(request.POST)

        if form.is_valid():
            negocio = form.save()
            messages.success(
                request,
                f'Negocio "{negocio.nombre}" creado correctamente.'
            )
            return redirect('negocios_lista')

    else:
        form = NegocioForm()

    context = {
        'form': form,
        'titulo': 'Crear negocio',
        'boton': 'Guardar negocio',
    }

    return render(request, 'pagos/negocio_form.html', context)


@admin_general_required
def negocio_editar(request, negocio_id):
    negocio = get_object_or_404(Negocio, id=negocio_id)

    if request.method == 'POST':
        form = NegocioForm(request.POST, instance=negocio)

        if form.is_valid():
            negocio = form.save()
            messages.success(
                request,
                f'Negocio "{negocio.nombre}" actualizado correctamente.'
            )
            return redirect('negocios_lista')

    else:
        form = NegocioForm(instance=negocio)

    context = {
        'form': form,
        'titulo': 'Editar negocio',
        'boton': 'Actualizar negocio',
    }

    return render(request, 'pagos/negocio_form.html', context)


@admin_general_required
def negocio_seleccionar(request, negocio_id):
    negocio = get_object_or_404(
        Negocio,
        id=negocio_id,
        activo=True
    )

    request.session['negocio_activo_id'] = negocio.id

    messages.success(
        request,
        f'Ahora estás gestionando el negocio: {negocio.nombre}.'
    )

    return redirect('panel_dueno')


@admin_general_required
def dueno_negocio_crear(request):
    if request.method == 'POST':
        form = DuenoNegocioUsuarioForm(request.POST)

        if form.is_valid():
            dueno_negocio = form.save()
            messages.success(
                request,
                f'Dueño creado para el negocio {dueno_negocio.negocio.nombre}.'
            )
            return redirect('negocios_lista')

    else:
        form = DuenoNegocioUsuarioForm()

    context = {
        'form': form,
        'titulo': 'Crear dueño de negocio',
        'boton': 'Guardar dueño',
    }

    return render(request, 'pagos/dueno_negocio_form.html', context)
