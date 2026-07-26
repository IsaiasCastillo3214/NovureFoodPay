from datetime import timedelta

from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import Pedido
from .permissions import (
    es_dueno,
    obtener_negocio_activo,
    obtener_vendedor_usuario,
)


# ============================================================
# FILTROS Y CONSULTAS GENERALES
# ============================================================

def construir_querystring(request, **overrides):
    query = request.GET.copy()

    if 'page' in query:
        query.pop('page')

    for key, value in overrides.items():
        if value is None or value == '':
            query.pop(key, None)
        elif key == 'tipo_entrega' and value == 'todos':
            query.pop(key, None)
        else:
            query[key] = value

    return query.urlencode()


def aplicar_filtro_fecha(request, pedidos):
    rango_fecha = request.GET.get('rango_fecha', 'todos')
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()

    hoy = timezone.localdate()

    if rango_fecha == 'hoy':
        pedidos = pedidos.filter(fecha__date=hoy)

    elif rango_fecha == 'semana':
        inicio = hoy - timedelta(days=7)
        pedidos = pedidos.filter(fecha__date__gte=inicio)

    elif rango_fecha == 'mes':
        inicio = hoy.replace(day=1)
        pedidos = pedidos.filter(fecha__date__gte=inicio)

    elif rango_fecha == 'personalizado':
        fecha_inicio_parseada = parse_date(fecha_inicio) if fecha_inicio else None
        fecha_fin_parseada = parse_date(fecha_fin) if fecha_fin else None

        if fecha_inicio_parseada:
            pedidos = pedidos.filter(fecha__date__gte=fecha_inicio_parseada)

        if fecha_fin_parseada:
            pedidos = pedidos.filter(fecha__date__lte=fecha_fin_parseada)

    return pedidos


def aplicar_busqueda(request, pedidos):
    busqueda = request.GET.get('q', '').strip()

    if not busqueda:
        return pedidos

    filtros_busqueda = (
        Q(nombre_cliente__icontains=busqueda) |
        Q(telefono_cliente__icontains=busqueda) |
        Q(detalle_entrega__icontains=busqueda) |
        Q(pedido__icontains=busqueda) |
        Q(vendedor__nombre__icontains=busqueda) |
        Q(detalles__producto__nombre__icontains=busqueda)
    )

    busqueda_numerica = ''.join(c for c in busqueda if c.isdigit())

    if busqueda_numerica:
        valor_numerico = int(busqueda_numerica)

        filtros_busqueda = (
            filtros_busqueda |
            Q(id=valor_numerico) |
            Q(monto=valor_numerico)
        )

    return pedidos.filter(filtros_busqueda).distinct()


def aplicar_filtro_tipo_entrega(request, pedidos):
    filtro_tipo_entrega = request.GET.get('tipo_entrega', 'todos')

    if filtro_tipo_entrega == 'delivery':
        return pedidos.filter(tipo_entrega='delivery')

    if filtro_tipo_entrega == 'retiro_tienda':
        return pedidos.filter(tipo_entrega='retiro_tienda')

    return pedidos


def obtener_pedidos_base_usuario(request):
    negocio = obtener_negocio_activo(request)

    if not negocio:
        return Pedido.objects.none()

    pedidos = Pedido.objects.filter(negocio=negocio)

    if es_dueno(request.user):
        return pedidos

    vendedor = obtener_vendedor_usuario(request.user)

    if not vendedor or vendedor.negocio_id != negocio.id:
        messages.error(
            request,
            'Tu usuario no tiene un vendedor asociado a este negocio.'
        )
        return Pedido.objects.none()

    return pedidos.filter(vendedor=vendedor)
