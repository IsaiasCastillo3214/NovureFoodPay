from .models import Negocio, Vendedor, DuenoNegocio


def rol_usuario(request):
    user = request.user

    es_admin_general = False
    es_dueno_local = False
    es_dueno = False
    negocio_activo = None
    modo_ayuda_activo = False

    if user.is_authenticated:
        es_admin_general = (
            user.is_superuser or
            user.groups.filter(name='Admin general').exists()
        )

        es_dueno_local = user.groups.filter(name='Dueño local').exists()

        es_dueno = es_admin_general or es_dueno_local

        if es_admin_general:
            negocio_id = request.session.get('negocio_activo_id')

            if negocio_id:
                negocio_activo = Negocio.objects.filter(
                    id=negocio_id,
                    activo=True
                ).first()

            modo_ayuda_activo = bool(
                request.session.get('modo_ayuda_activo') and negocio_activo
            )

        else:
            try:
                perfil_dueno = user.perfil_dueno

                if perfil_dueno.activo and perfil_dueno.negocio.activo:
                    negocio_activo = perfil_dueno.negocio

            except DuenoNegocio.DoesNotExist:
                pass

            if not negocio_activo:
                try:
                    vendedor = user.perfil_vendedor

                    if vendedor.negocio and vendedor.negocio.activo:
                        negocio_activo = vendedor.negocio

                except Vendedor.DoesNotExist:
                    pass

    return {
        'es_admin_general': es_admin_general,
        'es_dueno_local': es_dueno_local,
        'es_dueno': es_dueno,
        'negocio_activo': negocio_activo,
        'modo_ayuda_activo': modo_ayuda_activo,
    }