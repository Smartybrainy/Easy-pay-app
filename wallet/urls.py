from django.urls import path
from .views import AddFund

app_name = 'wallet'

urlpatterns = [
    path('add-fund/', AddFund.as_view(), name="add-fund"),
]