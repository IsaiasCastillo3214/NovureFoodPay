from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    NegocioForm,
    DuenoNegocioUsuarioForm,
)

from .models import Negocio
from .permissions import admin_general_required


@admin_general_required
def negocios_lista(request):
    negocios = Negocio.objects.all().order_by('nombre')

    context = {
        'negocios': negocios,
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
                f'Negocio {negocio.nombre} creado correctamente.'
            )

            return redirect('negocios_lista')

    else:
        form = NegocioForm()

    context = {
        'form': form,
        'titulo': 'Crear negocio',
        'boton': 'Crear negocio',
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
                f'Negocio {negocio.nombre} actualizado correctamente.'
            )

            return redirect('negocios_lista')

    else:
        form = NegocioForm(instance=negocio)

    context = {
        'form': form,
        'titulo': 'Editar negocio',
        'boton': 'Guardar cambios',
        'negocio': negocio,
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
    request.session.pop('modo_ayuda_activo', None)
    request.session.modified = True

    messages.success(
        request,
        f'Estás gestionando el negocio {negocio.nombre}.'
    )

    return redirect('dashboard')


@admin_general_required
@require_POST
def negocio_modo_ayuda(request, negocio_id):
    negocio = get_object_or_404(
        Negocio,
        id=negocio_id,
        activo=True
    )

    request.session['negocio_activo_id'] = negocio.id
    request.session['modo_ayuda_activo'] = True
    request.session.modified = True

    messages.success(
        request,
        f'Entraste en Modo Ayuda para el negocio {negocio.nombre}.'
    )

    return redirect('dashboard')


@admin_general_required
@require_POST
def salir_modo_ayuda(request):
    request.session.pop('modo_ayuda_activo', None)
    request.session.pop('negocio_activo_id', None)
    request.session.modified = True

    messages.info(
        request,
        'Saliste del Modo Ayuda.'
    )

    return redirect('negocios_lista')


@admin_general_required
@require_POST
def salir_negocio_activo(request):
    request.session.pop('modo_ayuda_activo', None)
    request.session.pop('negocio_activo_id', None)
    request.session.modified = True

    messages.info(
        request,
        'Saliste del negocio activo.'
    )

    return redirect('negocios_lista')


@admin_general_required
def dueno_negocio_crear(request):
    if request.method == 'POST':
        form = DuenoNegocioUsuarioForm(request.POST)

        if form.is_valid():
            dueno_negocio = form.save()

            messages.success(
                request,
                f'Dueño local creado correctamente para {dueno_negocio.negocio.nombre}.'
            )

            return redirect('negocios_lista')

    else:
        form = DuenoNegocioUsuarioForm()

    context = {
        'form': form,
        'titulo': 'Crear dueño local',
        'boton': 'Crear dueño',
    }

    return render(request, 'pagos/dueno_negocio_form.html', context)