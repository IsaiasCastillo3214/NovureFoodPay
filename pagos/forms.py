from django import forms
from django.contrib.auth.models import User, Group

from .models import Pedido, Producto, Vendedor


# ============================================================
# VALIDACIONES BASE PARA PEDIDOS
# ============================================================

class PedidoBaseValidation:
    def clean_nombre_cliente(self):
        nombre = self.cleaned_data.get('nombre_cliente')

        if not nombre or len(nombre.strip()) < 3:
            raise forms.ValidationError(
                'El nombre del cliente debe tener al menos 3 caracteres.'
            )

        return nombre.strip()

    def clean_telefono_cliente(self):
        telefono = self.cleaned_data.get('telefono_cliente')

        if not telefono:
            raise forms.ValidationError(
                'Debes ingresar el teléfono del cliente.'
            )

        telefono = telefono.strip()

        if not telefono.isdigit():
            raise forms.ValidationError(
                'El teléfono solo debe contener números.'
            )

        if len(telefono) < 8 or len(telefono) > 12:
            raise forms.ValidationError(
                'El teléfono debe tener entre 8 y 12 dígitos.'
            )

        return telefono

    def clean(self):
        cleaned_data = super().clean()

        tipo_entrega = cleaned_data.get('tipo_entrega')
        detalle_entrega = cleaned_data.get('detalle_entrega')

        if tipo_entrega == 'delivery':
            if not detalle_entrega or not detalle_entrega.strip():
                self.add_error(
                    'detalle_entrega',
                    'Debes ingresar la dirección si el pedido es delivery.'
                )

        if tipo_entrega == 'retiro_tienda':
            cleaned_data['detalle_entrega'] = 'Retiro en tienda'

        return cleaned_data


# ============================================================
# FORMULARIO PEDIDO PARA VENDEDOR
# No permite elegir vendedor, porque se asigna automáticamente
# según el usuario conectado.
# ============================================================

class PedidoForm(PedidoBaseValidation, forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'nombre_cliente',
            'telefono_cliente',
            'tipo_entrega',
            'detalle_entrega',
            'pedido',
            'tipo_pago',
            'estado_pedido',
            'estado_pago',
        ]

        widgets = {
            'pedido': forms.Textarea(attrs={
                'placeholder': 'Observación opcional del pedido',
                'rows': 3,
            }),
        }


# ============================================================
# FORMULARIO PEDIDO PARA DUEÑO
# El dueño sí puede elegir vendedor.
# ============================================================

class PedidoOwnerForm(PedidoBaseValidation, forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'vendedor',
            'nombre_cliente',
            'telefono_cliente',
            'tipo_entrega',
            'detalle_entrega',
            'pedido',
            'tipo_pago',
            'estado_pedido',
            'estado_pago',
        ]

        widgets = {
            'pedido': forms.Textarea(attrs={
                'placeholder': 'Observación opcional del pedido',
                'rows': 3,
            }),
        }


# ============================================================
# FORMULARIO PRODUCTOS
# CRUD del dueño local
# ============================================================

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'precio',
            'activo',
        ]

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if not nombre or len(nombre.strip()) < 3:
            raise forms.ValidationError(
                'El nombre del producto debe tener al menos 3 caracteres.'
            )

        return nombre.strip()

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')

        if precio is None or precio <= 0:
            raise forms.ValidationError(
                'El precio debe ser mayor a 0.'
            )

        return precio


# ============================================================
# FORMULARIO VENDEDORES + CREDENCIALES
# Permite crear vendedor y usuario al mismo tiempo.
# ============================================================

class VendedorUsuarioForm(forms.ModelForm):
    username = forms.CharField(
        label='Usuario',
        max_length=150,
        required=True,
        help_text='Nombre de usuario para iniciar sesión.'
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
        required=False,
        help_text='Déjala vacía al editar si no quieres cambiarla.'
    )

    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput,
        required=False
    )

    usuario_activo = forms.BooleanField(
        label='Usuario activo',
        required=False,
        initial=True
    )

    class Meta:
        model = Vendedor
        fields = [
            'nombre',
            'telefono',
            'correo',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        vendedor = self.instance

        if vendedor and vendedor.pk and vendedor.usuario:
            self.fields['username'].initial = vendedor.usuario.username
            self.fields['usuario_activo'].initial = vendedor.usuario.is_active

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if not nombre or len(nombre.strip()) < 3:
            raise forms.ValidationError(
                'El nombre del vendedor debe tener al menos 3 caracteres.'
            )

        return nombre.strip()

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username or len(username.strip()) < 3:
            raise forms.ValidationError(
                'El usuario debe tener al menos 3 caracteres.'
            )

        username = username.strip()

        vendedor = self.instance
        usuarios = User.objects.filter(username=username)

        if vendedor and vendedor.pk and vendedor.usuario:
            usuarios = usuarios.exclude(id=vendedor.usuario.id)

        if usuarios.exists():
            raise forms.ValidationError(
                'Ya existe un usuario con este nombre.'
            )

        return username

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        vendedor = self.instance
        creando_vendedor = not vendedor.pk
        vendedor_sin_usuario = vendedor.pk and not vendedor.usuario

        if creando_vendedor and not password:
            self.add_error(
                'password',
                'Debes ingresar una contraseña para el vendedor.'
            )

        if vendedor_sin_usuario and not password:
            self.add_error(
                'password',
                'Este vendedor no tiene usuario asociado. Debes ingresar una contraseña.'
            )

        if password or password_confirm:
            if password != password_confirm:
                self.add_error(
                    'password_confirm',
                    'Las contraseñas no coinciden.'
                )

            if password and len(password) < 6:
                self.add_error(
                    'password',
                    'La contraseña debe tener al menos 6 caracteres.'
                )

        return cleaned_data

    def save(self, commit=True):
        vendedor = super().save(commit=False)

        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        usuario_activo = self.cleaned_data.get('usuario_activo')

        if vendedor.usuario:
            usuario = vendedor.usuario
        else:
            usuario = User()

        usuario.username = username
        usuario.email = vendedor.correo or ''
        usuario.is_active = usuario_activo
        usuario.is_staff = False
        usuario.is_superuser = False

        if password:
            usuario.set_password(password)

        usuario.save()

        grupo_vendedor, _ = Group.objects.get_or_create(name='Vendedor')
        usuario.groups.set([grupo_vendedor])

        vendedor.usuario = usuario

        if commit:
            vendedor.save()

        return vendedor