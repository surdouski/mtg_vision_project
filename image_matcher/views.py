from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework import mixins, viewsets, serializers, permissions
from rest_framework.response import Response

from image_matcher.models import ImageUpload
from image_matcher.models.image_upload import CardListingDetails


class IsOwnerOrAdminOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


@login_required()
def new_listing(request):
    if request.method == 'GET':
        return render(request, 'drag_and_drop.html', {})


class CardListingDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardListingDetails
        fields = '__all__'


class CardListingDetailsViewSet(mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    permission_classes = [IsOwnerOrAdminOnly]
    queryset = CardListingDetails.objects.all()
    serializer_class = CardListingDetailsSerializer

    def retrieve(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('listing-detail', args=(kwargs.get('pk'),)))

    def perform_destroy(self, instance):
        ImageUpload.objects.filter(listing_details=instance).delete()
        instance.delete()
        return Response({'message': 'successfully deleted'}, status=200)
