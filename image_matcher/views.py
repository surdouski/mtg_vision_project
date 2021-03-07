from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required()
def new_listing(request):
    if request.method == 'GET':
        return render(request, 'drag_and_drop.html', {})
