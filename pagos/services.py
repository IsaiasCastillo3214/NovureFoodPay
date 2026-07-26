from .models import (
    Producto,
    DetallePedido,
)


# ============================================================
# PRODUCTOS / DETALLES DE PEDIDO
# ============================================================

def obtener_productos_json(productos):
    return [
        {
            'id': str(producto.id),
            'nombre': producto.nombre,
            'precio': producto.precio,
        }
        for producto in productos
    ]


def obtener_lineas_productos(request, negocio):
    productos_ids = request.POST.getlist('producto[]')
    cantidades = request.POST.getlist('cantidad[]')

    lineas = []
    total = 0

    for producto_id, cantidad in zip(productos_ids, cantidades):
        if not producto_id:
            continue

        try:
            cantidad = int(cantidad)
        except ValueError:
            return None, 'La cantidad debe ser un número válido.'

        if cantidad <= 0:
            return None, 'La cantidad debe ser mayor a 0.'

        producto = Producto.objects.filter(
            id=producto_id,
            negocio=negocio,
            activo=True
        ).first()

        if not producto:
            return None, 'Uno de los productos seleccionados no existe o no pertenece a este negocio.'

        precio_unitario = producto.precio
        total += precio_unitario * cantidad

        lineas.append({
            'producto': producto,
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
        })

    if not lineas:
        return None, 'Debes seleccionar al menos un producto.'

    return {
        'lineas': lineas,
        'total': total,
    }, None


def guardar_detalles_pedido(pedido, lineas):
    pedido.detalles.all().delete()

    total = 0

    for linea in lineas:
        DetallePedido.objects.create(
            pedido=pedido,
            producto=linea['producto'],
            cantidad=linea['cantidad'],
            precio_unitario=linea['precio_unitario'],
        )

        total += linea['cantidad'] * linea['precio_unitario']

    pedido.monto = total
    pedido.save(update_fields=['monto'])
