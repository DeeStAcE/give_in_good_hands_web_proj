from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from charity.models import *


class IndexView(View):

    def get(self, request):
        donations = Donation.objects.all()
        donations_quantity = sum([donation.quantity for donation in donations])
        institutions = Institution.objects.all()
        institutions_foundations = institutions.filter(type=Institution.Types.FOUNDATION)
        institutions_nongov_organizations = institutions.filter(type=Institution.Types.NONGOVERNMENTAL_ORGANIZATION)
        institutions_local_collections = institutions.filter(type=Institution.Types.LOCAL_COLLECTION)

        context = {
            'donations_quantity': donations_quantity,
            'supported_institutions': len(institutions),
            'foundations': institutions_foundations,
            'nongov_organizations': institutions_nongov_organizations,
            'local_collections': institutions_local_collections,
        }
        return render(request, 'index.html', context=context)


class AddDonationView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        categories = Category.objects.all()
        institutions = Institution.objects.all()

        context = {
            'categories': categories,
            'institutions': institutions,
        }
        return render(request, 'form.html', context=context)


class UserView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        return render(request, 'user-page.html')
