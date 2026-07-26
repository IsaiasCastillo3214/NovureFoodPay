from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import (
    Q,
    Sum,
    Count,
    Value,
    IntegerField,
    Prefetch,
)
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render

from .models import (
    Pedido,
    Producto,
    DetallePedido,
)
from .permissions import (
    negocio_activo_required,
    es_admin_general,
    es_dueno,
    obtener_negocio_activo,
)
from .selectors import (
    aplicar_filtro_fecha,
    aplicar_busqueda,
    aplicar_filtro_tipo_entrega,
    obtener_pedidos_base_usuario,
    construir_querystring,
)


# ============================================================
# DASHBOARD Y AJAX
# ============================================================

@login_required
@negocio_activo_required
def dashboard(request):
    filtro_tipo_entrega = request.GET.get('tipo_entrega', 'todos')
    busqueda = request.GET.get('q', '').strip()
    rango_fecha = request.GET.get('rango_fecha', 'todos')
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()
    pagina = request.GET.get('page', 1)

    pedidos_base = obtener_pedidos_base_usuario(request)

    pedidos_base = aplicar_filtro_fecha(request, pedidos_base)
    pedidos_base = aplicar_busqueda(request, pedidos_base)

    resumen = pedidos_base.aggregate(
        total_vendido=Coalesce(
            Sum('monto'),
            Value(0),
            output_field=IntegerField()
        ),
        total_pagado=Coalesce(
            Sum('monto', filter=Q(estado_pago='pagado')),
            Value(0),
            output_field=IntegerField()
        ),
        total_pendiente=Coalesce(
            Sum('monto', filter=Q(estado_pago='pendiente')),
            Value(0),
            output_field=IntegerField()
        ),
        total_delivery=Coalesce(
            Sum('monto', filter=Q(tipo_entrega='delivery')),
            Value(0),
            output_field=IntegerField()
        ),
        total_retiro=Coalesce(
            Sum('monto', filter=Q(tipo_entrega='retiro_tienda')),
            Value(0),
            output_field=IntegerField()
        ),
        cantidad_total=Count('id', distinct=True),
        cantidad_delivery=Count(
            'id',
            filter=Q(tipo_entrega='delivery'),
            distinct=True
        ),
        cantidad_retiro=Count(
            'id',
            filter=Q(tipo_entrega='retiro_tienda'),
            distinct=True
        ),
    )

    pedidos_filtrados = aplicar_filtro_tipo_entrega(request, pedidos_base)

    detalles_optimizados = Prefetch(
        'detalles',
        queryset=DetallePedido.objects.select_related('producto')
    )

    pedidos_filtrados = (
        pedidos_filtrados
        .select_related('vendedor', 'negocio')
        .prefetch_related(detalles_optimizados)
        .order_by('-fecha')
    )

    paginator = Paginator(pedidos_filtrados, 12)
    pedidos = paginator.get_page(pagina)

    query_sin_page = construir_querystring(request)
    query_sin_busqueda = construir_querystring(request, q=None)
    query_todos = construir_querystring(request, tipo_entrega='todos')
    query_delivery = construir_querystring(request, tipo_entrega='delivery')
    query_retiro = construir_querystring(request, tipo_entrega='retiro_tienda')

    context = {
        'pedidos': pedidos,

        'total_vendido': resumen['total_vendido'],
        'total_pagado': resumen['total_pagado'],
        'total_pendiente': resumen['total_pendiente'],

        'cantidad_total': resumen['cantidad_total'],
        'cantidad_delivery': resumen['cantidad_delivery'],
        'cantidad_retiro': resumen['cantidad_retiro'],
        'cantidad_pedidos_vista': pedidos.paginator.count,

        'total_delivery': resumen['total_delivery'],
        'total_retiro': resumen['total_retiro'],

        'filtro_tipo_entrega': filtro_tipo_entrega,
        'busqueda': busqueda,
        'rango_fecha': rango_fecha,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,

        'query_sin_page': query_sin_page,
        'query_sin_busqueda': query_sin_busqueda,
        'query_todos': query_todos,
        'query_delivery': query_delivery,
        'query_retiro': query_retiro,
        'export_querystring': query_sin_page,

        'estados_pedido': Pedido.ESTADO_PEDIDO_CHOICES,
        'estados_pago': Pedido.ESTADO_PAGO_CHOICES,

        'es_dueno': es_dueno(request.user),
        'es_admin_general': es_admin_general(request.user),
        'page_obj': pedidos,
    }

    return render(request, 'pagos/dashboard.html', context)


@login_required
def buscar_productos(request):
    negocio = obtener_negocio_activo(request)

    if not negocio:
        return JsonResponse({
            'productos': []
        })

    busqueda = request.GET.get('q', '').strip()

    productos = Producto.objects.filter(
        negocio=negocio,
        activo=True
    )

    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    else:
        productos = productos.none()

    productos = productos.order_by('nombre').values(
        'id',
        'nombre',
        'precio'
    )[:20]

    return JsonResponse({
        'productos': list(productos)
    })
