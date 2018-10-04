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
    # TODO: check for coils, eliquids and batteries are in db
    product = get_object_or_404(
        PackageOffer, pk=pk)
    if request.method == 'POST':
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

    form = forms.PackageOfferForm2(request.POST or None,
                                   initial={'device': product.device.name,
                                            'price': product.price[0] if product.price else 0})
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


@staff_member_required
@permission_required('product.view_product')
def package_offer_images(request, product_pk):
    product = get_object_or_404(
        PackageOffer.objects.prefetch_related('images'), pk=product_pk)
    images = product.images.all()
    ctx = {
        'product': product, 'images': images, 'is_empty': not images.exists()}
    return TemplateResponse(
        request, 'dashboard/package_offers/product_image/list.html', ctx)


@staff_member_required
@permission_required('product.edit_product')
def package_offer_image_edit(request, product_pk, img_pk=None):
    product = get_object_or_404(PackageOffer, pk=product_pk)
    if img_pk:
        product_image = get_object_or_404(product.images, pk=img_pk)
    else:
        product_image = ProductImage(product=product)
    form = forms.ProductImageForm(
        request.POST or None, request.FILES or None, instance=product_image)
    if form.is_valid():
        product_image = form.save()
        if img_pk:
            msg = pgettext_lazy(
                'Dashboard message',
                'Updated image %s') % product_image.image.name
        else:
            msg = pgettext_lazy(
                'Dashboard message',
                'Added image %s') % product_image.image.name
        messages.success(request, msg)
        return redirect('dashboard:package-offer-image-list', product_pk=product.pk)
    ctx = {'form': form, 'product': product, 'product_image': product_image}
    return TemplateResponse(
        request,
        'dashboard/package_offers/product_image/form.html',
        ctx)


@staff_member_required
@permission_required('product.edit_product')
def package_offer_image_delete(request, product_pk, img_pk):
    product = get_object_or_404(PackageOffer, pk=product_pk)
    image = get_object_or_404(product.images, pk=img_pk)
    if request.method == 'POST':
        image.delete()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message',
                'Removed image %s') % image.image.name)
        return redirect('dashboard:package-offer-image-list', product_pk=product.pk)
    return TemplateResponse(
        request,
        'dashboard/package_offers/product_image/confirm_delete.html',
        {'product': product, 'image': image})


@require_POST
@staff_member_required
def ajax_upload_package_offer_image(request, product_pk):
    product = get_object_or_404(PackageOffer, pk=product_pk)
    form = forms.UploadImageForm(
        request.POST or None, request.FILES or None, product=product)
    status = 200
    if form.is_valid():
        image = form.save()
        ctx = {'id': image.pk, 'image': None, 'order': image.order}
    elif form.errors:
        status = 400
        ctx = {'error': form.errors}
    return JsonResponse(ctx, status=status)
