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

    url(r'^(?P<product_pk>[0-9]+)/images/$', views.package_offer_images,
        name='package-offer-image-list'),
    url(r'^(?P<product_pk>[0-9]+)/images/(?P<img_pk>[0-9]+)/$',
        views.package_offer_image_edit, name='package-offer-image-update'),
    url(r'^(?P<product_pk>[0-9]+)/images/add/$',
        views.package_offer_image_edit, name='package-offer-image-add'),
    url(r'^(?P<product_pk>[0-9]+)/images/(?P<img_pk>[0-9]+)/delete/$',
        views.package_offer_image_delete, name='package-offer-image-delete'),

    url(r'^(?P<product_pk>[0-9]+)/images/upload/$',
        views.ajax_upload_package_offer_image, name='package-offer-images-upload'),
]
