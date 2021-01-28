from django.urls import path
from .views import HomeView, customer_info

app_name = 'epay'

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('make-payment/', customer_info, name="make-payment")
]
