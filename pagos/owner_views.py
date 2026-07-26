from datetime import timedelta

from django.db.models import (
    Q,
    Sum,
    Count,
    Value,
    IntegerField,
    F,
    ExpressionWrapper,
)
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone

from .models import (
    Pedido,
    DetallePedido,
)
from .permissions import (
    dueno_required,
    negocio_activo_required,
    obtener_negocio_activo,
    es_admin_general,
)


# ============================================================
# PANEL DEL DUEÑO
# ============================================================

@dueno_required
@negocio_activo_required
def panel_dueno(request):
    negocio = obtener_negocio_activo(request)
    filtro_fecha = request.GET.get('rango', 'mes')

    pedidos = Pedido.objects.select_related('vendedor').filter(
        negocio=negocio
    )

    hoy = timezone.localdate()

    if filtro_fecha == 'hoy':
        pedidos = pedidos.filter(fecha__date=hoy)

    elif filtro_fecha == 'semana':
        inicio = hoy - timedelta(days=7)
        pedidos = pedidos.filter(fecha__date__gte=inicio)

    elif filtro_fecha == 'mes':
        inicio = hoy.replace(day=1)
        pedidos = pedidos.filter(fecha__date__gte=inicio)

    elif filtro_fecha == 'todos':
        pedidos = pedidos.all()

    resumen = pedidos.aggregate(
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
        total_pedidos=Count('id'),
        pedidos_delivery=Count(
            'id',
            filter=Q(tipo_entrega='delivery')
        ),
        pedidos_retiro=Count(
            'id',
            filter=Q(tipo_entrega='retiro_tienda')
        ),
        pedidos_pagados=Count(
            'id',
            filter=Q(estado_pago='pagado')
        ),
        pedidos_pendientes=Count(
            'id',
            filter=Q(estado_pago='pendiente')
        ),
    )

    total_pedidos = resumen['total_pedidos'] or 0
    total_vendido = resumen['total_vendido'] or 0

    if total_pedidos > 0:
        ticket_promedio = round(total_vendido / total_pedidos)
    else:
        ticket_promedio = 0

    subtotal_expression = ExpressionWrapper(
        F('cantidad') * F('precio_unitario'),
        output_field=IntegerField()
    )

    productos_top = (
        DetallePedido.objects
        .filter(pedido__in=pedidos)
        .values('producto__nombre')
        .annotate(
            cantidad_vendida=Coalesce(
                Sum('cantidad'),
                Value(0),
                output_field=IntegerField()
            ),
            total_vendido=Coalesce(
                Sum(subtotal_expression),
                Value(0),
                output_field=IntegerField()
            )
        )
        .order_by('-cantidad_vendida')[:6]
    )

    vendedores_top = (
        pedidos
        .values('vendedor__nombre')
        .annotate(
            total_vendido=Coalesce(
                Sum('monto'),
                Value(0),
                output_field=IntegerField()
            ),
            total_pedidos=Count('id')
        )
        .order_by('-total_vendido')[:6]
    )

    ultimos_pedidos = (
        pedidos
        .select_related('vendedor')
        .order_by('-fecha')[:8]
    )

    context = {
        'filtro_fecha': filtro_fecha,

        'total_vendido': total_vendido,
        'total_pagado': resumen['total_pagado'],
        'total_pendiente': resumen['total_pendiente'],
        'total_pedidos': total_pedidos,

        'pedidos_delivery': resumen['pedidos_delivery'],
        'pedidos_retiro': resumen['pedidos_retiro'],
        'pedidos_pagados': resumen['pedidos_pagados'],
        'pedidos_pendientes': resumen['pedidos_pendientes'],
        'ticket_promedio': ticket_promedio,

        'productos_top': productos_top,
        'vendedores_top': vendedores_top,
        'ultimos_pedidos': ultimos_pedidos,

        'es_admin_general': es_admin_general(request.user),
    }

    return render(request, 'pagos/panel_dueno.html', context)
