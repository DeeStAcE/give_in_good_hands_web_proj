from django.urls import path
from charity.views import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('add-donation/', AddDonation.as_view(), name='add-donation'),
]
