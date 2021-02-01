from django.urls import path
from .views import main_view, customer_info

app_name = 'epay'

urlpatterns = [
    path('', main_view, name="home"),
    path('make-payment/', customer_info, name="make-payment"),
    path('<str:ref_code>/', main_view, name="home"),
]
