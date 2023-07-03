from django.urls import path
from account.views import *

urlpatterns = [
	path('login/', LoginView.as_view(), name='login'),
	path('logout/', LogoutView.as_view(), name='logout'),
	path('register/', RegisterView.as_view(), name='register'),
	path('user/edit', EditUserView.as_view(), name='user-edit'),
	path('activate/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate'),
]