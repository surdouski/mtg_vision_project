from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView
from .forms import SignUpForm


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'GET':
        return HttpResponseRedirect(reverse('info'))


def info(request):
    template = 'info.html'
    return render(request, template)


def signup(request):
    template = 'registration/signup.html'

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'GET':
        context = {'form': SignUpForm()}
        return render(request, template, context)

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse('home'))

        context = {'form': form}
        return render(request, template, context)


@login_required()
def home(request):
    template = 'home.html'
    return render(request, template)
