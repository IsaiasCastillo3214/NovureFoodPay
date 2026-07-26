from django.contrib.auth.views import LoginView

from .auth_forms import FoodPayLoginForm


class FoodPayLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = FoodPayLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)

        remember_me = form.cleaned_data.get('remember_me')

        if remember_me:
            self.request.session.set_expiry(60 * 60 * 24 * 14)
        else:
            self.request.session.set_expiry(0)

        return response