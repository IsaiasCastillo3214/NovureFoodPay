"""
Punto de entrada de vistas para mantener compatibilidad con pagos/urls.py.

Las vistas reales están separadas por responsabilidad para que el proyecto sea
más mantenible:
- admin_views.py: administración general de negocios y dueños.
- dashboard_views.py: dashboard principal y búsqueda AJAX.
- pedido_views.py: creación, edición, eliminación y estados de pedidos.
- owner_views.py: panel del dueño.
- producto_views.py: CRUD de productos.
- vendedor_views.py: CRUD de vendedores.
- exports.py: exportación Excel.
"""

from .admin_views import (
    negocios_lista,
    negocio_crear,
    negocio_editar,
    negocio_seleccionar,
    dueno_negocio_crear,
)
from .dashboard_views import (
    dashboard,
    buscar_productos,
)
from .exports import exportar_pedidos_excel
from .owner_views import panel_dueno
from .pedido_views import (
    crear_pedido,
    editar_pedido,
    eliminar_pedido,
    actualizar_estado,
)
from .producto_views import (
    productos_lista,
    producto_crear,
    producto_editar,
    producto_eliminar,
)
from .vendedor_views import (
    vendedores_lista,
    vendedor_crear,
    vendedor_editar,
    vendedor_eliminar,
)


__all__ = [
    'dashboard',
    'crear_pedido',
    'editar_pedido',
    'eliminar_pedido',
    'actualizar_estado',
    'buscar_productos',
    'exportar_pedidos_excel',
    'panel_dueno',
    'negocios_lista',
    'negocio_crear',
    'negocio_editar',
    'negocio_seleccionar',
    'dueno_negocio_crear',
    'productos_lista',
    'producto_crear',
    'producto_editar',
    'producto_eliminar',
    'vendedores_lista',
    'vendedor_crear',
    'vendedor_editar',
    'vendedor_eliminar',
]
