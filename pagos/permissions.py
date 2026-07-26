from functools import wraps

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404

from .models import (
    Pedido,
    Vendedor,
    Negocio,
    DuenoNegocio,
)


# ============================================================
# ROLES Y PERMISOS
# ============================================================

def es_admin_general(user):
    if not user.is_authenticated:
        return False

    return user.is_superuser or user.groups.filter(name='Admin general').exists()


def es_dueno_local(user):
    if not user.is_authenticated:
        return False

    return user.groups.filter(name='Dueño local').exists()


def es_dueno(user):
    return es_admin_general(user) or es_dueno_local(user)


def dueno_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not es_dueno(request.user):
            messages.error(
                request,
                'No tienes permisos para acceder al panel del dueño.'
            )
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)

    return wrapper


def admin_general_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not es_admin_general(request.user):
            messages.error(
                request,
                'Solo el admin general puede acceder a esta sección.'
            )
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)

    return wrapper


def obtener_vendedor_usuario(user):
    try:
        return user.perfil_vendedor
    except Vendedor.DoesNotExist:
        return None


def obtener_negocio_usuario(user):
    if es_admin_general(user):
        return None

    try:
        perfil_dueno = user.perfil_dueno

        if perfil_dueno.activo and perfil_dueno.negocio.activo:
            return perfil_dueno.negocio

    except DuenoNegocio.DoesNotExist:
        pass

    try:
        vendedor = user.perfil_vendedor

        if vendedor.negocio and vendedor.negocio.activo:
            return vendedor.negocio

    except Vendedor.DoesNotExist:
        pass

    return None


def obtener_negocio_activo(request):
    if not request.user.is_authenticated:
        return None

    if es_admin_general(request.user):
        negocio_id = request.session.get('negocio_activo_id')

        if negocio_id:
            return Negocio.objects.filter(
                id=negocio_id,
                activo=True
            ).first()

        return None

    return obtener_negocio_usuario(request.user)


def negocio_activo_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        negocio = obtener_negocio_activo(request)

        if negocio:
            return view_func(request, *args, **kwargs)

        if es_admin_general(request.user):
            messages.warning(
                request,
                'Debes seleccionar un negocio para continuar.'
            )
            return redirect('negocios_lista')

        raise Http404('Tu usuario no tiene un negocio activo asociado.')

    return wrapper


def obtener_pedido_permitido(request, pedido_id):
    negocio = obtener_negocio_activo(request)

    if not negocio:
        raise Http404('No hay negocio activo.')

    if es_dueno(request.user):
        return get_object_or_404(
            Pedido,
            id=pedido_id,
            negocio=negocio
        )

    vendedor = obtener_vendedor_usuario(request.user)

    if not vendedor:
        raise Http404('No tienes vendedor asociado.')

    return get_object_or_404(
        Pedido,
        id=pedido_id,
        negocio=negocio,
        vendedor=vendedor
    )
