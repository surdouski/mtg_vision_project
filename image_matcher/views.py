from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import mixins, viewsets, serializers, permissions
from rest_framework.response import Response

from image_matcher.models import ImageUpload
from image_matcher.models.image_upload import CardListingDetails


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


@login_required()
def new_listing(request):
    if request.method == 'GET':
        return render(request, 'drag_and_drop.html', {})


class CardListingDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardListingDetails
        fields = '__all__'


class CardListingDetailsViewSet(mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = CardListingDetails.objects.all()
    serializer_class = CardListingDetailsSerializer

    def perform_destroy(self, instance):
        ImageUpload.objects.filter(listing_details=instance).delete()
        instance.delete()
        return Response({'message': 'successfully deleted'}, status=200)
