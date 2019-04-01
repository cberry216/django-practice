from django.urls import path

from .views import (
    user_login,
)

app_name = 'account'

urlpatterns = [
    # Post Views
    path('login/', user_login, name='login'),
]
