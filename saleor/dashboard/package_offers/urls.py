from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.package_offers_list, name='package-offers-list'),
    # url(r'')
]
