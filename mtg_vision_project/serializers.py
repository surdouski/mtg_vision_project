from django import forms
from django.utils import timezone
from rest_framework import serializers

from image_matcher.ebay_listing import CardListingObject
from image_matcher.models import ImageUpload
from image_matcher.models.image_upload import CardListingDetails


class UploadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = '__all__'


class OutPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = '__all__'
    image_input = serializers.ImageField(use_url=False)


class ImageUploadIdConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = ['id']


class ListingSerializer(serializers.ModelSerializer):
    listed_datetime = serializers.DateTimeField(default=None)
    listing_title = serializers.CharField(max_length=80)
    listed_price = serializers.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        model = CardListingDetails
        fields = ['listed_datetime', 'listing_title', 'listed_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['listed_datetime'].default = timezone.now()

    def update(self, instance, validated_data):
        user = validated_data['user']
        card_listing_object = CardListingObject(instance, user)
        card_listing_object.create_listing(validated_data['listing_title'],
                                           validated_data['listed_price'],
                                           instance.ebay_image_url)

        instance.listed_datetime = validated_data['listed_datetime']
        instance.listing_title = validated_data['listing_title']
        instance.listed_price = validated_data['listed_price']
        instance.is_listed = True
        instance.save()
        return instance
