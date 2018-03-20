from django.template.response import TemplateResponse
from django.contrib import messages
from django.utils.translation import pgettext_lazy
from impersonate.views import impersonate as orig_impersonate, stop_impersonate

from ..dashboard.views import staff_member_required
from ..product.utils import products_with_availability, products_for_homepage, products_for_homepage_banner
from ..userprofile.models import User


def home(request):
    products_main = products_for_homepage()
    # TODO: Do something better here rather than querying twice
    banner_products = products_for_homepage_banner()
    products = products_with_availability(
        products_main[6:14], discounts=request.discounts, local_currency=request.currency)
    # products_first_row = products_with_availability(
    #     products_main[0:3], discounts=request.discounts, local_currency=request.currency)
    # products_second_row = products_with_availability(
    #     products_main[3:6], discounts=request.discounts, local_currency=request.currency)
    products_first_row = products_with_availability(
        banner_products[0:3], discounts=request.discounts, local_currency=request.currency)
    products_second_row = products_with_availability(
        banner_products[3:6], discounts=request.discounts, local_currency=request.currency)
    return TemplateResponse(
        request, 'home.html',
        {'products': products,
         'parent': None,
         'products_first_row': products_first_row,
         'products_second_row': products_second_row})


def package_offer(request):
    pass


@staff_member_required
def styleguide(request):
    return TemplateResponse(request, 'styleguide.html')


def impersonate(request, uid):
    response = orig_impersonate(request, uid)
    if request.session.modified:
        msg = pgettext_lazy(
            'Impersonation message',
            'You are now logged as {}'.format(User.objects.get(pk=uid)))
        messages.success(request, msg)
    return response
