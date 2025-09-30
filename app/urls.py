from django.urls import path
from .views import register_user, login_user, tickets_view, transactions_view, get_user_profile

urlpatterns = [
    path("register/", register_user, name="register"),
    path("login/", login_user, name="login"),
    path("profile/", get_user_profile, name="get_user_profile"),
    path("tickets/", tickets_view, name="tickets_view"),
    path("transactions/", transactions_view, name="transactions_view"),
]

