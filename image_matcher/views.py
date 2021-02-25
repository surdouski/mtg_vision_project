from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from requests import HTTPError


@login_required()
def new_listing(request):
    if request.method == 'GET':
        return render(request, 'drag_and_drop.html', {})
