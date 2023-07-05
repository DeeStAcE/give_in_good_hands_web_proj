from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from charity.models import *


class IndexView(View):

    def get(self, request):
        donations = Donation.objects.all()
        donations_quantity = sum([donation.quantity for donation in donations])
        institutions = Institution.objects.all()
        foundations = institutions.filter(type=Institution.Types.FOUNDATION)
        nongov_organizations = institutions.filter(type=Institution.Types.NONGOVERNMENTAL_ORGANIZATION)
        local_collections = institutions.filter(type=Institution.Types.LOCAL_COLLECTION)

        context = {
            'donations_quantity': donations_quantity,
            'supported_institutions': len(institutions),
            'foundations': foundations,
            'nongov_organizations': nongov_organizations,
            'local_collections': local_collections,
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

    def post(self, request):
        quantity = request.POST.get('bags')
        categories = request.POST.getlist('categories')
        institution = request.POST.get('organization')
        address = request.POST.get('address')
        city = request.POST.get('city')
        zip_code = request.POST.get('postcode')
        phone_number = request.POST.get('phone')
        pick_up_date = request.POST.get('date')
        pick_up_time = request.POST.get('time')
        pick_up_comment = request.POST.get('more_info')

        # check if all the fields are filled
        if not (quantity and categories and institution and address and city and zip_code and phone_number and
                pick_up_date and pick_up_time):
            return redirect('add-donation')

        user = request.user
        donation = Donation.objects.create(quantity=quantity, institution_id=int(institution), address=address,
                                           phone_number=phone_number,
                                           city=city, zip_code=zip_code, pick_up_date=pick_up_date,
                                           pick_up_time=pick_up_time,
                                           pick_up_comment=pick_up_comment, user=user)
        donation.categories.set(categories)
        donation.save()
        return render(request, 'form-confirmation.html')


class UserView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        user = request.user
        donations = Donation.objects.filter(user=user)
        context = {
            'donations': donations.order_by('is_taken', 'pick_up_date'),
        }
        return render(request, 'user-page.html', context=context)

    def post(self, request):
        if 'taken' in request.POST:
            donation_id = request.POST.get('taken')
            donation = Donation.objects.get(pk=donation_id)
            # change boolean value to the opposite
            donation.is_taken = not donation.is_taken
            donation.save()
            return redirect('user-page')
