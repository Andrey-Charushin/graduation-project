import logging
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView

from .models import Profile
from .forms import EditProfileForm

log = logging.getLogger(__name__)

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "accountsapp/register.html"
    success_url = reverse_lazy("accountsapp:profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        log.info("Register user %s with username %s", user, username)
        return response


class AboutMeView(LoginRequiredMixin, TemplateView):
    template_name = "accountsapp/about_me.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        log.info('Profile %s', request.user.username)
        return self.render_to_response(context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль был успешно обновлен!')
            return redirect('accountsapp:profile')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'accountsapp/edit_profile.html', {'form': form})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("accountsapp:login"))

