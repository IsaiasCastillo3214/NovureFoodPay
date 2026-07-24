def rol_usuario(request):
    user = request.user

    es_dueno = False

    if user.is_authenticated:
        es_dueno = user.is_superuser or user.groups.filter(name='Dueño local').exists()

    return {
        'es_dueno': es_dueno
    }