from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth import get_user_model
CustomUser =  get_user_model()
from .models import Wallet



class AddFund(View):
    template_name = 'wallet/add_fund.html'

    def get(self, *args, **kwargs):
        return render(self.request, self.template_name)

    def post(self, *args, **kwargs):
        try:
            balance = self.request.POST.get('amount')
            added_date = timezone.now()
            wallet, created = Wallet.objects.get_or_create(
                user=self.request.user,
                balance=balance,
                added_date=added_date
                )
            if created:
                wallet.balance = balance    
                wallet.save()
            messages.info(self.request, f"{balance} successfully added to your EasyPay amount.")
            return redirect('accounts:profile-view')
        except ObjectDoesNotExist:
            messages.warning(self.request, "wallet fund failed, try again.")
            return redirect('wallet:add-fund')
