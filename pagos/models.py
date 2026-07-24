from django.db import models
from django.contrib.auth.models import User


class Vendedor(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_vendedor'
    )
    nombre = models.CharField(max_length=100, db_index=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['nombre']),
        ]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=120, db_index=True)
    precio = models.PositiveIntegerField()
    activo = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['activo']),
            models.Index(fields=['activo', 'nombre']),
        ]

    def __str__(self):
        return f'{self.nombre} - ${self.precio}'


class Pedido(models.Model):
    TIPO_ENTREGA_CHOICES = [
        ('delivery', 'Delivery'),
        ('retiro_tienda', 'Retiro en tienda'),
    ]

    TIPO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('debito', 'Débito'),
        ('credito', 'Crédito'),
        ('otro', 'Otro'),
    ]

    ESTADO_PEDIDO_CHOICES = [
        ('recibido', 'Recibido'),
        ('preparando', 'Preparando'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    ESTADO_PAGO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
    ]

    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.CASCADE,
        db_index=True
    )

    nombre_cliente = models.CharField(max_length=100, db_index=True)

    telefono_cliente = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_index=True
    )

    tipo_entrega = models.CharField(
        max_length=30,
        choices=TIPO_ENTREGA_CHOICES,
        default='delivery',
        db_index=True
    )

    detalle_entrega = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    pedido = models.TextField(blank=True, null=True)

    monto = models.PositiveIntegerField(default=0, db_index=True)

    tipo_pago = models.CharField(
        max_length=30,
        choices=TIPO_PAGO_CHOICES,
        default='efectivo'
    )

    estado_pedido = models.CharField(
        max_length=30,
        choices=ESTADO_PEDIDO_CHOICES,
        default='recibido',
        db_index=True
    )

    estado_pago = models.CharField(
        max_length=30,
        choices=ESTADO_PAGO_CHOICES,
        default='pendiente',
        db_index=True
    )

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['vendedor', 'fecha']),
            models.Index(fields=['tipo_entrega', 'fecha']),
            models.Index(fields=['estado_pago', 'fecha']),
            models.Index(fields=['estado_pedido', 'fecha']),
            models.Index(fields=['nombre_cliente']),
            models.Index(fields=['telefono_cliente']),
            models.Index(fields=['monto']),
        ]

    @property
    def numero_pedido(self):
        return f'{self.id:06d}'

    def __str__(self):
        return f'Pedido #{self.numero_pedido} - {self.nombre_cliente} - ${self.monto}'


class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
        db_index=True
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_index=True
    )

    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.PositiveIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['pedido']),
            models.Index(fields=['producto']),
            models.Index(fields=['pedido', 'producto']),
        ]

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'