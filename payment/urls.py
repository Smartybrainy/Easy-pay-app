from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('epay.urls', namespace="epay")),
    path('accounts/', include('accounts.urls', namespace="accounts")),
    path('favicon/', RedirectView.as_view(url=staticfiles_storage.url('fav/naira-sign2.ico'))),
    re_path(r"^api/", include('accounts.urls', namespace="account")),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
