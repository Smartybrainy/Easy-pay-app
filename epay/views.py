from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "epay/epay_home.html"


def customer_info(request):
    return render(request, "epay/payment.html",)
