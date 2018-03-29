from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.template.response import TemplateResponse
from django.utils.translation import npgettext_lazy, pgettext_lazy
from django.views.decorators.http import require_POST
from django_prices.templatetags.prices_i18n import gross

from ...core.utils import get_paginator_items
from ...product.models import (
    AttributeChoiceValue, Product, ProductAttribute, ProductClass,
    ProductImage, ProductVariant, Stock, StockLocation, PackageOffer)
from ...product.utils import (
    get_availability, get_product_costs_data, get_variant_costs_data)
from ..views import staff_member_required
from ..product.filters import (
    ProductFilter, ProductAttributeFilter, ProductClassFilter,
    StockLocationFilter)
from . import forms

@staff_member_required
@permission_required('product.view_properties')
def package_offers_list(request):
    products = PackageOffer.objects.all()
    # products = products.order_by('name')
    product_classes = ProductClass.objects.all()
    product_filter = ProductFilter(request.GET, queryset=products)
    products = get_paginator_items(
        product_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))
    ctx = {
        # 'bulk_action_form': forms.ProductBulkUpdate(),
        'products': products, 'product_classes': product_classes,
        'filter_set': product_filter,
        'is_empty': not product_filter.queryset.exists()}
    return TemplateResponse(
        request,
        'dashboard/package_offers/list.html', ctx)


@staff_member_required
@permission_required('product.view_product')
def package_offer_detail(request, pk):
    product = get_object_or_404(
        PackageOffer, pk=pk)
    ctx = {
        'product': product
    }
    return TemplateResponse(request, 'dashboard/package_offers/detail.html', ctx)


@staff_member_required
@permission_required('product.edit_product')
def package_offer_edit(request, pk):
    product = get_object_or_404(
        PackageOffer, pk=pk)
    form = forms.PackageOfferForm2(request.POST or None,
                                   initial={'device': product.device.name,
                                            'price': product.price[0] if product.price else 0})
    if form.is_valid():
        coil_id = form.cleaned_data['coils']
        battery_id = form.cleaned_data['batteries']
        price = form.cleaned_data['price']
        product.coil = Product.objects.get(id=coil_id)
        product.battery = Product.objects.get(id=battery_id)
        product.price = price
        product.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Updated product %s') % product
        messages.success(request, msg)
        return redirect('dashboard:package-offer-detail', pk=product.pk)
    ctx = {'product': product, 'product_form': form}
    return TemplateResponse(request, 'dashboard/package_offers/form.html', ctx)


@staff_member_required
@permission_required('product.edit_product')
def package_offer_delete(request, pk):
    product = get_object_or_404(PackageOffer, pk=pk)
    if request.method == 'POST':
        p = Product.objects.get(id=product.device.id)
        p.package_offer = False
        p.save()
        product.delete()
        messages.success(
            request,
            pgettext_lazy('Dashboard message', 'Removed package offer %s') % product)
        return redirect('dashboard:package-offers-list')
    return TemplateResponse(
        request,
        'dashboard/package_offers/confirm_delete.html',
        {'product': product})
