from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('nuevo-pedido/', views.crear_pedido, name='crear_pedido'),
    path('pedido/<int:pedido_id>/editar/', views.editar_pedido, name='editar_pedido'),
    path('pedido/<int:pedido_id>/eliminar/', views.eliminar_pedido, name='eliminar_pedido'),
    path('pedido/<int:pedido_id>/actualizar-estado/', views.actualizar_estado, name='actualizar_estado'),

    path('productos/buscar/', views.buscar_productos, name='buscar_productos'),

    path('pedidos/exportar-excel/', views.exportar_pedidos_excel, name='exportar_pedidos_excel'),

    path('panel/', views.panel_dueno, name='panel_dueno'),

    path('panel/productos/', views.productos_lista, name='productos_lista'),
    path('panel/productos/crear/', views.producto_crear, name='producto_crear'),
    path('panel/productos/<int:producto_id>/editar/', views.producto_editar, name='producto_editar'),
    path('panel/productos/<int:producto_id>/eliminar/', views.producto_eliminar, name='producto_eliminar'),

    path('panel/vendedores/', views.vendedores_lista, name='vendedores_lista'),
    path('panel/vendedores/crear/', views.vendedor_crear, name='vendedor_crear'),
    path('panel/vendedores/<int:vendedor_id>/editar/', views.vendedor_editar, name='vendedor_editar'),
    path('panel/vendedores/<int:vendedor_id>/eliminar/', views.vendedor_eliminar, name='vendedor_eliminar'),
]