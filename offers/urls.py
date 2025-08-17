from django.urls import path
from .views import OfferCreateView, OfferListView, offers_list

app_name = 'offers'

urlpatterns = [
    path('', offers_list, name='offers_list'),  # أو استخدم OfferListView.as_view() كمسار رئيسي
    path('list/', OfferListView.as_view(), name='list'),
    path('add/', OfferCreateView.as_view(), name='add'),
]