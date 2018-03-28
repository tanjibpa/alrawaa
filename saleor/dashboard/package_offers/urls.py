from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.package_offers_list, name='package-offers-list'),
    url(r'^(?P<pk>[0-9]+)/$',
        views.package_offer_detail, name='package-offer-detail'),
    url(r'^(?P<pk>[0-9]+)/update/$',
        views.package_offer_edit, name='package-offer-update'),
    url(r'^(?P<pk>[0-9]+)/delete/$',
        views.package_offer_delete, name='package-offer-delete'),
]
