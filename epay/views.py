from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.sites.shortcuts import get_current_site

from accounts.models import Profile
    
def main_view(request, *args, **kwargs):
    current_site = get_current_site(request)
    domain = current_site.domain
    code = str(kwargs.get('ref_code'))
    if code:
        try:
            profile = Profile.objects.get(code=code)
            request.session['ref_profile'] = profile.id
            print('id', profile.id)
        except:
            pass

    print(request.session.get_expiry_age())
    return render(request, 'epay/epay_home.html', {'host': domain})


def customer_info(request):
    return render(request, "epay/payment.html",)
