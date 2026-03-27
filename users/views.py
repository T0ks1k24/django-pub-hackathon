from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout, authenticate
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView

from ecp_lib.auth import authenticate_with_private_key, read_private_key
from ecp_lib.auth import create_user_keys

import logging

from .forms import RegisterForm, LoginForm

logger = logging.getLogger("ecp")
sec_logger = logging.getLogger("security")


class LoginView(DjangoLoginView):
    template_name = "auth/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        key_file = self.request.FILES.get("key_file")

        if not key_file:
            form.add_error("key_file", "Файл ключа обязателен")
            return self.form_invalid(form)

        logger.info(f"Password verified | user={username}")

        try:
            private_key = read_private_key(key_file)
            logger.debug(f"Private key file received | user={username}")

            ecp_user, error= authenticate_with_private_key(
                self.request,
                username=username,
                password=password,
                private_key=private_key
            )

            if ecp_user is None:
                form.add_error(None, error)
                return self.form_invalid(form)
            # logger.info(f"ECP authentication success | user={username} | ip={ip}")
            return super().form_valid(form)


        except Exception as e:
            logger.exception(f"ECP verification error | user={username}")
            form.add_error(None, f"Помилка перевірки ключа")

        return self.form_invalid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = "login"


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "auth/register.html"
    success_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logger.info(f"Authenticated user tried to access register | user={request.user}")
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        request = self.request
        ip = request.META.get("REMOTE_ADDR")

        self.object = form.save()
        user = self.object

        logger.info(f"User registered | user={user.username} | ip={ip}")

        try:
            private_key = create_user_keys(self.object)
            logger.info(f"RSA key pair generated | user={user.username}")

            # Store the key in the session for download after redirect
            request.session["private_key_download"] = private_key
            request.session["private_key_filename"] = f"{user.username}_private_key.pem"

            return redirect(f"{self.success_url}?registered=1")

        except Exception:
            logger.exception(f"Error during registration | user={user.username}")
            raise


class DownloadKeyView(View):
    def get(self, request):
        private_key = request.session.pop("private_key_download", None)
        filename = request.session.pop("private_key_filename", "private_key.pem")

        if not private_key:
            return HttpResponse("Key not found or already downloaded", status=404)

        response = HttpResponse(
            private_key,
            content_type="application/x-pem-file",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class LogoutView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect("login")
