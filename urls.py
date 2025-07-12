from django.urls import path
from .views import confirmation_view  # Import the view

urlpatterns = [
    path('confirmation/', confirmation_view, name='confirmation'),  # URL for the confirmation page
]
