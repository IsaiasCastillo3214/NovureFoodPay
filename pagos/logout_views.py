from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


@require_POST
@csrf_exempt
def foodpay_logout(request):
    logout(request)

    messages.info(
        request,
        'Sesión cerrada correctamente.'
    )

    return redirect('login')