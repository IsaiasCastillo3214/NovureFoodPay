from django.contrib import admin
from .models import Vendedor, Producto, Pedido, DetallePedido


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'correo')
    search_fields = ('nombre', 'telefono', 'correo')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('precio_unitario',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
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
        'tipo_entrega',
        'tipo_pago',
        'estado_pedido',
        'estado_pago',
        'fecha',
        'vendedor',
    )

    search_fields = (
        'nombre_cliente',
        'telefono_cliente',
        'detalle_entrega',
        'vendedor__nombre',
    )

    inlines = [DetallePedidoInline]