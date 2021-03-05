from rest_framework import serializers

from image_matcher.models import ImageUpload


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
