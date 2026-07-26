from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Negocio(models.Model):
    nombre = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=250, blank=True, null=True)
    activo = models.BooleanField(default=True, db_index=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['activo']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            contador = 1

            while Negocio.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                contador += 1
                slug = f'{base_slug}-{contador}'

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class DuenoNegocio(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil_dueno'
    )
    negocio = models.ForeignKey(
        Negocio,
        on_delete=models.CASCADE,
        related_name='duenos',
        db_index=True
    )
    activo = models.BooleanField(default=True, db_index=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['negocio']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f'{self.usuario.username} - {self.negocio.nombre}'


class Vendedor(models.Model):
    negocio = models.ForeignKey(
        Negocio,
        on_delete=models.CASCADE,
        related_name='vendedores',
        null=True,
        blank=True,
        db_index=True
    )

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
            models.Index(fields=['negocio']),
            models.Index(fields=['nombre']),
            models.Index(fields=['negocio', 'nombre']),
        ]

    def __str__(self):
        if self.negocio:
            return f'{self.nombre} - {self.negocio.nombre}'

        return self.nombre


class Producto(models.Model):
    negocio = models.ForeignKey(
        Negocio,
        on_delete=models.CASCADE,
        related_name='productos',
        null=True,
        blank=True,
        db_index=True
    )

    nombre = models.CharField(max_length=120, db_index=True)
    precio = models.PositiveIntegerField()
    activo = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['negocio']),
            models.Index(fields=['nombre']),
            models.Index(fields=['activo']),
            models.Index(fields=['negocio', 'activo']),
            models.Index(fields=['negocio', 'nombre']),
            models.Index(fields=['activo', 'nombre']),
        ]

    def __str__(self):
        if self.negocio:
            return f'{self.nombre} - {self.negocio.nombre} - ${self.precio}'

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

    negocio = models.ForeignKey(
        Negocio,
        on_delete=models.CASCADE,
        related_name='pedidos',
        null=True,
        blank=True,
        db_index=True
    )

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
            models.Index(fields=['negocio']),
            models.Index(fields=['fecha']),
            models.Index(fields=['negocio', 'fecha']),
            models.Index(fields=['vendedor', 'fecha']),
            models.Index(fields=['tipo_entrega', 'fecha']),
            models.Index(fields=['estado_pago', 'fecha']),
            models.Index(fields=['estado_pedido', 'fecha']),
            models.Index(fields=['negocio', 'tipo_entrega', 'fecha']),
            models.Index(fields=['negocio', 'estado_pago', 'fecha']),
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