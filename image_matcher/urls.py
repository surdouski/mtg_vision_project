from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CardListingDetailsViewSet


#router = DefaultRouter()
#router.register(r'card_listing_details', CardListingDetailsViewSet)
#urlpatterns = []
#urlpatterns += router.urls

urlpatterns = [
    path('api/card_listing_details/<pk>', CardListingDetailsViewSet.as_view(
        {'delete': 'destroy'}), name='card_listing_details-destroy'),
]
