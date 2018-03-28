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
    ProductImage, ProductVariant, Stock, StockLocation)
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
    products = Product.objects.prefetch_related('images')
    products = products.order_by('name').filter(package_offer=True)
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
    products = Product.objects.prefetch_related(
        'variants__stock', 'images',
        'product_class__variant_attributes__values').all()
    product = get_object_or_404(products, pk=pk)
    variants = product.variants.all()
    images = product.images.all()
    availability = get_availability(product)
    sale_price = availability.price_range
    purchase_cost, gross_margin = get_product_costs_data(product)
    gross_price_range = product.get_gross_price_range()

    # no_variants is True for product classes that doesn't require variant.
    # In this case we're using the first variant under the hood to allow stock
    # management.
    no_variants = not product.product_class.has_variants
    only_variant = variants.first() if no_variants else None
    if only_variant:
        stock = only_variant.stock.all()
    else:
        stock = Stock.objects.none()
    ctx = {
        'product': product, 'sale_price': sale_price, 'variants': variants,
        'gross_price_range': gross_price_range, 'images': images,
        'no_variants': no_variants, 'only_variant': only_variant,
        'stock': stock, 'purchase_cost': purchase_cost,
        'gross_margin': gross_margin,
        'is_empty': not variants.exists()}
    return TemplateResponse(request, 'dashboard/package_offers/detail.html', ctx)


@staff_member_required
@permission_required('product.edit_product')
def package_offer_edit(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related('variants'), pk=pk)

    form = forms.PackageOfferForm(request.POST or None, instance=product)

    if form.is_valid():

        product = form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Updated product %s') % product
        messages.success(request, msg)
        return redirect('dashboard:product-detail', pk=product.pk)
    ctx = {'product': product, 'product_form': form}
    return TemplateResponse(request, 'dashboard/package_offers/form.html', ctx)

