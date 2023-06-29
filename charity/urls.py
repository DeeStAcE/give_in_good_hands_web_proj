from django.urls import path
from charity.views import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('add-donation/', AddDonationView.as_view(), name='add-donation'),
    path('user/', UserView.as_view(), name='user-page'),
]
