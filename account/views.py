from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages


class LoginView(View):

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not (email and password):
            messages.error(request, 'Wprowadź dane')
            return redirect('login')

        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Błędny email lub hasło')
            return redirect('login')


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('index')


class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not (name and surname and email and password):
            messages.error(request, 'Wprowadź dane')
            return redirect('register')

        if password != password2:
            messages.error(request, 'Hasła muszą być takie same. Spróbuj ponownie')
            return redirect('register')

        user = User.objects.create_user(first_name=name, last_name=surname, password=password, email=email,
                                        username=email)
        login(request, user)
        return redirect('index')


class EditUserView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        return render(request, 'user-edit.html')

    def post(self, request):
        user = request.user
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        old_password = request.POST.get('old-password')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if 'change-user' in request.POST:
            user = authenticate(username=user.email, password=password)
            if user is not None:
                user.first_name = name
                user.last_name = surname
                user.email = email
                user.save()
                return redirect('user-page')
            else:
                messages.error(request, 'Błędne hasło')
                return redirect('user-edit')
        elif 'change-password' in request.POST:
            user = authenticate(username=user.email, password=old_password)
            if user is None:
                messages.error(request, 'Błędne hasło')
                return redirect('user-edit')
            if password1 != password2:
                messages.error(request, 'Hasła nie pasują')
                return redirect('user-edit')
            user.set_password(password1)
            user.save()
            login(request, user)
            return redirect('user-page')
