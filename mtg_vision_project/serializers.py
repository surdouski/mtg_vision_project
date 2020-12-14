import logging

import cv2
import pandas as pd
import numpy as np
from PIL import Image
from django.contrib.auth.decorators import login_required

from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from image_matcher.detect_image import find_cards
from image_matcher.models import ImageUpload

from .settings import MEDIA_ROOT, CARD_POOLS_ALL_SETS_PCK


class UploadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = '__all__'


class OutPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = '__all__'
    image_input = serializers.ImageField(use_url=False)


@login_required()
@api_view(['POST'])
def upload_api_view(request):
    try:
        serializer = UploadImageSerializer(data=request.data)
        is_valid = serializer.is_valid()
        if is_valid:
            image_upload_object = serializer.save()
            #image = Image.open(serializer.validated_data['image_input'])
            image = cv2.imread(f'{MEDIA_ROOT}{image_upload_object.image_input}')
            del image_upload_object
            hash_pool = pd.read_pickle(CARD_POOLS_ALL_SETS_PCK)
            hash_pool = flatten_hash_array(hash_pool)
            detected_cards = find_cards(image, hash_pool)
            del hash_pool
            del serializer
            del image
            card_models = [
                ImageUpload.objects.create(image_input=path.image_path,
                                           image_name=path.card_name)
                for path in detected_cards
            ]
            del detected_cards
            card_serializers = OutPutSerializer(card_models, many=True)
            return Response({"message": "Success.", "data": card_serializers.data})
    except Exception as e:
        logging.critical('failed, shut down everything', e.with_traceback())
        exit(1)
    return Response({"message": "Bad input type.", "data": "failed"}, status=400)


def flatten_hash_array(card_pool):
    card_hk = 'card_hash_32'
    card_pool = card_pool[
        ['id', 'name', 'set', 'collector_number', card_hk]
    ]
    card_pool[card_hk] = card_pool[card_hk].apply(lambda x: x.hash.flatten())
    return card_pool
