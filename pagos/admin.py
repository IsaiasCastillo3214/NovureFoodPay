from django.contrib import admin

from .models import (
    Negocio,
    DuenoNegocio,
    Vendedor,
    Producto,
    Pedido,
    DetallePedido,
)


@admin.register(Negocio)
class NegocioAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'telefono',
        'correo',
        'activo',
        'creado_en',
    )
    search_fields = (
        'nombre',
        'telefono',
        'correo',
    )
    list_filter = (
        'activo',
    )


@admin.register(DuenoNegocio)
class DuenoNegocioAdmin(admin.ModelAdmin):
    list_display = (
        'usuario',
        'negocio',
        'activo',
        'creado_en',
    )
    search_fields = (
        'usuario__username',
        'usuario__first_name',
        'usuario__email',
        'negocio__nombre',
    )
    list_filter = (
        'activo',
        'negocio',
    )


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'negocio',
        'usuario',
        'telefono',
        'correo',
    )
    search_fields = (
        'nombre',
        'telefono',
        'correo',
        'usuario__username',
        'negocio__nombre',
    )
    list_filter = (
        'negocio',
    )


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'negocio',
        'precio',
        'activo',
    )
    search_fields = (
        'nombre',
        'negocio__nombre',
    )
    list_filter = (
        'activo',
        'negocio',
    )


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = (
        'precio_unitario',
    )


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'numero_pedido',
        'negocio',
        'nombre_cliente',
        'telefono_cliente',
        'vendedor',
        'monto',
        'tipo_pago',
        'estado_pedido',
        'estado_pago',
        'fecha',
    )

    list_filter = (
        'negocio',
        'tipo_entrega',
        'tipo_pago',
        'estado_pedido',
        'estado_pago',
        'fecha',
        'vendedor',
    )

    search_fields = (
        'id',
        'nombre_cliente',
        'telefono_cliente',
        'detalle_entrega',
        'vendedor__nombre',
        'negocio__nombre',
    )

    inlines = [
        DetallePedidoInline,
    ]