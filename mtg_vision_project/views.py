import logging
import os

import cv2
import pandas as pd

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from requests import HTTPError
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.generics import get_object_or_404
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from image_matcher.detect_image import find_cards
from image_matcher.ebay_listing import CardListingObject
from image_matcher.forms import get_ebay_settings_form, get_sell_settings_form
from image_matcher.models import ImageUpload
from image_matcher.models.image_upload import upload_image, CardListingDetails
from image_matcher.models.profile import WebUser
from .forms import SignUpForm
from .ebay_oauth_python_client.oauthclient.oauth2api import \
    oauth2api, get_instance_oauth2api
from .ebay_oauth_python_client.oauthclient.model.model import environment
from .serializers import UploadImageSerializer, OutPutSerializer, ListingSerializer
from image_matcher.hash_matcher import flatten_hash_array
from .settings import MEDIA_ROOT, PICKLED_CARDS_PATH


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
    try:
        sign_in_url = oauth2api.generate_user_authorization_url(app_scopes)
        return HttpResponseRedirect(sign_in_url)
    except HTTPError:
        messages.add_message(request, messages.ERROR, 'Unable to get authorization '
                                                      'token.')
    return HttpResponseRedirect(reverse('home'))


@login_required()
def ebay_auth_code(request):
    if 'code' not in request.GET:
        return HttpResponseRedirect(reverse('ebay_sign_in '))

    code = request.GET.get('code')
    app_config_path = os.path.join(os.path.split(__file__)[0], 'config',
                                   'ebay-config-sample.yaml')
    oauth2api_inst = get_instance_oauth2api(app_config_path)
    try:
        user_token = oauth2api_inst.exchange_code_for_access_token(environment.SANDBOX,
                                                                   code)
        user = WebUser.get_user(request.user)
        user.access_token = user_token.access_token
        user.refresh_token = user_token.refresh_token
        user.save()
    except HTTPError:
        messages.add_message(request, messages.ERROR, 'Unable to create ebay link.')
        return render(request, 'home.html', {})
    return HttpResponseRedirect(reverse('home'))


@login_required()
def home(request):
    template = 'home.html'
    return render(request, template)


@login_required()
def ebay_settings_view(request):
    template = 'settings/basic_form.html'
    title = 'eBay Settings'

    if request.method == 'GET':
        form = get_ebay_settings_form(request.user)
        context = {
            'form': form,
            'title': title
        }
        return render(request, template, context)

    if request.method == 'POST':
        form = get_ebay_settings_form(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'eBay Settings Updated!')
        context = {
            'form': form,
            'title': title
        }
        return render(request, template, context)


@login_required()
def sell_settings_view(request):
    template = 'settings/basic_form.html'
    title = 'Sell Settings'

    if request.method == 'GET':
        form = get_sell_settings_form(request.user)
        context = {
            'form': form,
            'title': title
        }
        return render(request, template, context)

    if request.method == 'POST':
        form = get_sell_settings_form(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Sell Settings Updated!')
        context = {
            'form': form,
            'title': title
        }
        return render(request, template, context)


@login_required()
@api_view(['POST'])
def upload_api_view(request):
    try:
        serializer = UploadImageSerializer(data=request.data)
        is_valid = serializer.is_valid()
        if is_valid:
            image_upload_object = serializer.save()
            image = cv2.imread(f'{MEDIA_ROOT}/{image_upload_object.image_input}')
            del image_upload_object
            hash_pool = pd.read_pickle(PICKLED_CARDS_PATH)
            hash_pool = flatten_hash_array(hash_pool)
            card_models = find_cards(image, hash_pool)
            del hash_pool
            del serializer
            del image
            card_serializers = OutPutSerializer(card_models, many=True)
            return Response({"message": "Success.", "data": card_serializers.data})
    except Exception as e:
        logging.exception(e)
        exit(1)
    return Response({"message": "Bad input type.", "data": "failed"}, status=400)


@login_required()
@api_view(['POST'])
def upload_selected_images_to_ebay_view(request):
    try:
        listing_details = []
        for image_id in request.data:
            image_id = image_id['id']
            image_upload_instance = get_object_or_404(ImageUpload, pk=image_id)
            listing_helper = CardListingObject(image_upload_instance.listing_details,
                                               request.user)
            ebay_image_url = listing_helper.upload_image(
                image_upload_instance.image_input.name)
            listing_details.append(
                image_upload_instance.update_url_details(ebay_image_url))
        for listing in listing_details:
            listing.user = request.user
            listing.save()
            listing.update_price()
        return Response('hooray for nothing', status=200)
    except Exception as e:
        logging.exception(str(e))
        return Response({"message": "status 500: internal server error"}, status=500)


@login_required()
@api_view(['GET'])
def create_listing_redirect_view(request):
    current_user_listings = CardListingDetails.objects.filter(user=request.user,
                                                              is_listed=False,
                                                              ebay_image_url__isnull=False,
                                                              price_pull_failed=False,
                                                              price__isnull=False)
    if current_user_listings.exists():
        pk = current_user_listings.order_by('listed_datetime').last().pk
        return HttpResponseRedirect(reverse('listing-detail', args=(int(pk),)))
    messages.add_message(request, messages.INFO, 'No more listings, please upload '
                                                 'another photo to continue listing.')
    return HttpResponseRedirect(reverse('drag_n_drop'))


@login_required()
@api_view(['GET', 'POST'])
@renderer_classes([TemplateHTMLRenderer])
def create_listing_view(request, pk):
    if request.method == 'GET':
        listing_detail = get_object_or_404(CardListingDetails, pk=pk)
        serializer = ListingSerializer(listing_detail, initial={'test'})
        return Response(
            {'serializer': serializer, 'pk': pk, 'detail': listing_detail},
            template_name='listing_form.html')
    if request.method == 'POST':
        print('in request.method POST')
        listing_detail = get_object_or_404(CardListingDetails, pk=pk)
        print('after listing_detail')
        serializer = ListingSerializer(listing_detail, data=request.data)
        print('aFTer serializer')
        if serializer.is_valid():
            print('is_valid: true')
            serializer.save(user=request.user)
            return HttpResponseRedirect(reverse('listing-redirect'))
        print(serializer)
        print(serializer.errors)
        return HttpResponseRedirect(reverse('drag_n_drop'))


