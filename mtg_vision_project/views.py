import os

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from requests import HTTPError

from .forms import SignUpForm
from .ebay_oauth_python_client.oauthclient.oauth2api import get_instance_oauth2api
from .ebay_oauth_python_client.oauthclient.model.model import environment


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


app_scopes = ["https://api.ebay.com/oauth/api_scope",
                  "https://api.ebay.com/oauth/api_scope/sell.inventory",
                  "https://api.ebay.com/oauth/api_scope/sell.marketing",
                  "https://api.ebay.com/oauth/api_scope/sell.account",
                  "https://api.ebay.com/oauth/api_scope/sell.fulfillment"]


@login_required()
def ebay_sign_in(request):
    app_config_path = os.path.join(os.path.split(__file__)[0], 'config',
                                   'ebay-config-sample.yaml')
    oauth2api_inst = get_instance_oauth2api(app_config_path)
    try:
        sign_in_url = oauth2api_inst.generate_user_authorization_url(environment.SANDBOX,
                                                                app_scopes)
        return HttpResponseRedirect(sign_in_url)
    except HTTPError:
        messages.add_message(request, messages.ERROR, 'Unable to get authorization '
                                                      'token.')
    return HttpResponseRedirect(reverse('home'))


@login_required()
def ebay_auth_code(request):
    if 'code' not in request.GET:
        return HttpResponseRedirect(reverse('ebay_sign_in'))

    code = request.GET.get('code')
    app_config_path = os.path.join(os.path.split(__file__)[0], 'config',
                                   'ebay-config-sample.yaml')
    oauth2api_inst = get_instance_oauth2api(app_config_path)
    try:
        user_token = oauth2api_inst.exchange_code_for_access_token(environment.SANDBOX,
                                                                   code)
        user = request.user
        user.user_tokens_profile.access_token = user_token.access_token
        user.user_tokens_profile.refresh_token = user_token.refresh_token
        user.save()
    except HTTPError:
        messages.add_message(request, messages.ERROR, 'Unable to create ebay link.')
        return render(request, 'home.html', {})
    return HttpResponseRedirect(reverse('home'))


# TODO: Do refresh token action for access token view (given invalid/expired access
#  token), then create views for actually posting to ebay. Probably first ensure that
#  setting up works on actual site automatically without any need to change URLs.


@login_required()
def home(request):
    template = 'home.html'
    return render(request, template)
