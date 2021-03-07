from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CardListingDetailsViewSet


#app_name = 'image_matcher'

"""
router = DefaultRouter()
router.register(r'card_listing_details', CardListingDetailsViewSet)
urlpatterns = []
urlpatterns += router.urls
"""
urlpatterns = [
    #  Available Methods: GET => Detail, DELETE => Destroy,
    path('api/card_listing_details/<pk>', CardListingDetailsViewSet.as_view(
        {'get': 'retrieve', 'delete': 'destroy'}), name='card_listing_details'),

    #  Available Methods: GET => List,
    path('api/card_listing_details/', CardListingDetailsViewSet.as_view(
        {'get': 'list'}), name='card_listing_details'),
]
