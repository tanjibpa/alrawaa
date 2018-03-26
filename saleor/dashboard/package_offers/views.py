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
# from .filters import (
#     ProductFilter, ProductAttributeFilter, ProductClassFilter,
#     StockLocationFilter)
# from . import forms


@staff_member_required
@permission_required('product.view_properties')
def package_offers_list(request):
    classes = ProductClass.objects.all().prefetch_related(
        'product_attributes', 'variant_attributes').order_by('name')
    # class_filter = ProductClassFilter(request.GET, queryset=classes)
    # form = forms.ProductClassForm(request.POST or None)
    # if form.is_valid():
    #     return redirect('dashboard:product-class-add')
    # classes = get_paginator_items(
    #     class_filter.qs, settings.DASHBOARD_PAGINATE_BY,
    #     request.GET.get('page'))
    # classes.object_list = [
    #     (pc.pk, pc.name, pc.has_variants, pc.product_attributes.all(),
    #      pc.variant_attributes.all())
    #     for pc in classes.object_list]
    # ctx = {
    #     'form': form, 'product_classes': classes, 'filter_set': class_filter,
    #     'is_empty': not class_filter.queryset.exists()}
    return TemplateResponse(
        request,
        'dashboard/package_offers/list.html')
