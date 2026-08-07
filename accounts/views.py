from django.shortcuts import render, redirect
from .forms import RegisterForm, EditProfileForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from books.models import Order, Review
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib import messages


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
        
    else:
        form=RegisterForm()

    return render(request, "accounts/register.html", {
        "form": form
    })

class CustomLoginView(LoginView):
    template_name = "accounts/auth.html"

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("home")

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).count()
    reviews = Review.objects.filter(user=request.user).count()

    return render(request, "accounts/profile.html",
                  {
                      "user": request.user,
                      "orders": orders,
                      "reviews": reviews,
                  })

@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, "accounts/edit_profile.html", {"form": form})

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed sucessfully!")
            return redirect("profile")

    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/change_password.html", {"form": form})

def auth_view(request):
    login_form = AuthenticationForm()
    register_form = RegisterForm()

    active_form = "login"
    if request.method == "POST":
        if "register" in request.POST:
            active_form = "register"
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect("home")
            
        elif "login" in request.POST:
            active_form = "login"
            login_form = AuthenticationForm(request,data=request.POST,)
            if login_form.is_valid():
                login(request,login_form.get_user())
                return redirect("home")

    return render(
        request, "accounts/auth.html",
        {
            "login_form": login_form,
            "register_form": register_form,
            "active_form": active_form,
        },
    )