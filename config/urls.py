from django.contrib import admin
from django.urls import path, include

from pagos.auth_views import FoodPayLoginView
from pagos.logout_views import foodpay_logout


urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'login/',
        FoodPayLoginView.as_view(),
        name='login'
    ),

    path(
        'logout/',
        foodpay_logout,
        name='logout'
    ),

    path('', include('pagos.urls')),
]