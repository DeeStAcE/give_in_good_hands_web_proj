from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.contrib import messages
from django.core.mail import EmailMessage
from django.db.models.query_utils import Q

from account.tokens import account_activation_token


# email verification message
def activate_email(request, user, to_email):
    mail_subject = "Activate your user account"
    message = render_to_string("email_verification.html", {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    email = EmailMessage(mail_subject, message, to=[to_email])

    if email.send():
        messages.success(request, f"Przejdź do swojej skrzynki pocztowej w celu potwierdzenia rejestracji")
    else:
        messages.error(request, f"Problem podczas wysyłania potwierdzenia rejestracji")


# password reset email
def password_reset_email(request, user):
    mail_subject = "Password Reset request"
    message = render_to_string("reset_password.html", {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    email = EmailMessage(mail_subject, message, to=[user.email])

    if email.send():
        messages.success(request, f"Przejdź do swojej skrzynki pocztowej w celu zmiany hasła")
    else:
        messages.error(request, f"Problem podczas próby zmiany hasła")


def get_user_from_email_verification_token(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        return None

    if user is not None and account_activation_token.check_token(user, token):
        return user
    return None


# -------------------------------- class views ---------------------------------
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
            messages.error(request, 'Błędny email lub hasło / konto nie zostało aktywowane')
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
                                        username=email, is_active=False)
        activate_email(request, user, email)
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


class ActivateUserView(View):

    def get(self, request, uidb64, token):
        user = get_user_from_email_verification_token(uidb64, token)
        if user is None:
            return redirect('index')
        user.is_active = True
        user.save()
        messages.success(request, f"Konto aktywowane pomyślnie")
        return redirect('login')


class PasswordResetView(View):

    def get(self, request):
        return render(request, 'password-reset.html')

    def post(self, request):
        user_email = request.POST.get('email')
        associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
        if associated_user:
            password_reset_email(request, associated_user)
        else:
            messages.error(request, f"W bazie nie ma podanego maila")
        return redirect('index')


def password_reset_confirm(request, uidb64, token):
    user = get_user_from_email_verification_token(uidb64, token)
    if user is None:
        return redirect('index')
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not (password1 and password2):
            messages.error(request, 'Hasło nie zostało zmienione. Brak danych')
            return redirect('login')

        if password1 != password2:
            messages.error(request, 'Hasła muszą być takie same. Spróbuj ponownie')
            return redirect('login')

        user.set_password(password1)
        user.save()
        messages.success(request, 'Hasło zostało zmienione')
        return redirect('login')

    return render(request, 'password-reset-confirm.html')


# sending email to all superusers via contact form
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        if not (name and email and message):
            messages.error(request, f"Nie wprowadzono wszystkich danych. Mail nie został wysłany")
            return redirect('index')
        to_email = [user.email for user in User.objects.filter(is_superuser=True)]
        mail_subject = f"Contact from {name}"
        message = render_to_string('contact_form.html', {
            'email': email,
            'message': message,
        })
        email = EmailMessage(mail_subject, message, to=to_email)

        if email.send():
            messages.success(request, f"Mail wysłany do administratorów")
        else:
            messages.error(request, f"Problem podczas wysyłania maila")

    return redirect('index')
