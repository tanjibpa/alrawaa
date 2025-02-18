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
from .filters import (
    ProductFilter, ProductAttributeFilter, ProductClassFilter,
    StockLocationFilter)
from . import forms


# @staff_member_required
# @permission_required('product.bannered_products')
# def product_bannered_list(request):
#     products = Product.objects.prefetch_related('images')
#     products = products.order_by('name')
#     product_classes = ProductClass.objects.all()
#     product_filter = ProductFilter(request.GET, queryset=products)
#     products = get_paginator_items(
#         product_filter.qs, settings.DASHBOARD_PAGINATE_BY,
#         request.GET.get('page'))
#     ctx = {
#         'bulk_action_form': forms.ProductBulkUpdate(),
#         'products': products, 'product_classes': product_classes,
#         'filter_set': product_filter,
#         'is_empty': not product_filter.queryset.exists()}
#     return TemplateResponse(request, 'dashboard/product/list.html', ctx)


@staff_member_required
@permission_required('product.view_properties')
def product_class_list(request):
    classes = ProductClass.objects.all().prefetch_related(
        'product_attributes', 'variant_attributes').order_by('name')
    class_filter = ProductClassFilter(request.GET, queryset=classes)
    form = forms.ProductClassForm(request.POST or None)
    if form.is_valid():
        return redirect('dashboard:product-class-add')
    classes = get_paginator_items(
        class_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))
    classes.object_list = [
        (pc.pk, pc.name, pc.has_variants, pc.product_attributes.all(),
         pc.variant_attributes.all())
        for pc in classes.object_list]
    ctx = {
        'form': form, 'product_classes': classes, 'filter_set': class_filter,
        'is_empty': not class_filter.queryset.exists()}
    return TemplateResponse(
        request,
        'dashboard/product/product_class/list.html',
        ctx)


@staff_member_required
@permission_required('product.edit_properties')
def product_class_create(request):
    product_class = ProductClass()
    form = forms.ProductClassForm(request.POST or None,
                                  instance=product_class)
    if form.is_valid():
        product_class = form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Added product type %s') % product_class
        messages.success(request, msg)
        return redirect('dashboard:product-class-list')
    ctx = {'form': form, 'product_class': product_class}
    return TemplateResponse(
        request,
        'dashboard/product/product_class/form.html',
        ctx)


@staff_member_required
@permission_required('product.edit_properties')
def product_class_edit(request, pk):
    product_class = get_object_or_404(
        ProductClass, pk=pk)
    form = forms.ProductClassForm(request.POST or None,
                                  instance=product_class)
    if form.is_valid():
        product_class = form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Updated product type %s') % product_class
        messages.success(request, msg)
        return redirect('dashboard:product-class-update', pk=pk)
    ctx = {'form': form, 'product_class': product_class}
    return TemplateResponse(
        request,
        'dashboard/product/product_class/form.html',
        ctx)


@staff_member_required
@permission_required('product.edit_properties')
def product_class_delete(request, pk):
    product_class = get_object_or_404(ProductClass, pk=pk)
    if request.method == 'POST':
        product_class.delete()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message',
                'Removed product type %s') % product_class)
        return redirect('dashboard:product-class-list')
    ctx = {
        'product_class': product_class,
        'products': product_class.products.all()}
    return TemplateResponse(
        request,
        'dashboard/product/product_class/modal/confirm_delete.html',
        ctx)


@staff_member_required
@permission_required('product.view_product')
def product_list(request):
    products = Product.objects.prefetch_related('images')
    products = products.order_by('name')
    product_classes = ProductClass.objects.all()
    product_filter = ProductFilter(request.GET, queryset=products)
    products = get_paginator_items(
        product_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))
    ctx = {
        'bulk_action_form': forms.ProductBulkUpdate(),
        'products': products, 'product_classes': product_classes,
        'filter_set': product_filter,
        'is_empty': not product_filter.queryset.exists()}
    return TemplateResponse(request, 'dashboard/product/list.html', ctx)


@staff_member_required
@permission_required('product.edit_product')
def product_select_classes(request):
    """View for add product modal embedded in the product list view."""
    form = forms.ProductClassSelectorForm(request.POST or None)
    status = 200
    if form.is_valid():
        redirect_url = reverse(
            'dashboard:product-add',
            kwargs={'class_pk': form.cleaned_data.get('product_cls').pk})
        return (
            JsonResponse({'redirectUrl': redirect_url})
            if request.is_ajax() else redirect(redirect_url))
    elif form.errors:
        status = 400
    ctx = {'form': form}
    template = 'dashboard/product/modal/select_class.html'
    return TemplateResponse(request, template, ctx, status=status)


@staff_member_required
@permission_required('product.edit_product')
def product_create(request, class_pk):
    product_class = get_object_or_404(ProductClass, pk=class_pk)
    create_variant = not product_class.has_variants
    product = Product()
    product.product_class = product_class
    product_form = forms.ProductForm(request.POST or None, instance=product)
    if create_variant:
        variant = ProductVariant(product=product)
        variant_form = forms.ProductVariantForm(
            request.POST or None, instance=variant, prefix='variant')
        variant_errors = not variant_form.is_valid()
    else:
        variant_form = None
        variant_errors = False

    if product_form.is_valid() and not variant_errors:
        product = product_form.save()
        if product.package_offer:
            p = PackageOffer(device=product)
            p.save()
        if create_variant:
            variant.product = product
            variant_form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Added product %s') % product
        messages.success(request, msg)
        return redirect('dashboard:product-detail', pk=product.pk)
    ctx = {
        'product_form': product_form, 'variant_form': variant_form,
        'product': product}
    return TemplateResponse(request, 'dashboard/product/form.html', ctx)


@staff_member_required
@permission_required('product.view_product')
def product_detail(request, pk):
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
    return TemplateResponse(request, 'dashboard/product/detail.html', ctx)


@require_POST
@staff_member_required
@permission_required('product.edit_product')
def product_toggle_is_published(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_published = not product.is_published
    product.save(update_fields=['is_published'])
    return JsonResponse(
        {'success': True, 'is_published': product.is_published})


@staff_member_required
@permission_required('product.edit_product')
def product_edit(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related('variants'), pk=pk)

    edit_variant = not product.product_class.has_variants
    form = forms.ProductForm(request.POST or None, instance=product)

    if edit_variant:
        variant = product.variants.first()
        variant_form = forms.ProductVariantForm(
            request.POST or None, instance=variant, prefix='variant')
        variant_errors = not variant_form.is_valid()
    else:
        variant_form = None
        variant_errors = False

    if form.is_valid() and not variant_errors:
        # check for banner position of other products
        # if there exists another product with same position
        # make that position null
        if product.banner_position:
            _product = Product.objects.filter(banner_position=product.banner_position)
            for p in _product:
                p.banner_position = None
                p.save()
        if product.package_offer:
            # p = PackageOffer(device=product)
            try:
                p = PackageOffer.objects.get(device=product)
            except PackageOffer.DoesNotExist:
                p = PackageOffer(device=product)
                p.save()

        product = form.save()
        if edit_variant:
            variant_form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Updated product %s') % product
        messages.success(request, msg)
        return redirect('dashboard:product-detail', pk=product.pk)
    ctx = {'product': product, 'product_form': form,
           'variant_form': variant_form}
    return TemplateResponse(request, 'dashboard/product/form.html', ctx)


@staff_member_required
@permission_required('product.edit_product')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(
            request,
            pgettext_lazy('Dashboard message', 'Removed product %s') % product)
        return redirect('dashboard:product-list')
    return TemplateResponse(
        request,
        'dashboard/product/modal/confirm_delete.html',
        {'product': product})


@staff_member_required
@permission_required('product.view_stock_location')
def stock_details(request, product_pk, variant_pk, stock_pk):
    product = get_object_or_404(Product, pk=product_pk)
    variant = get_object_or_404(product.variants, pk=variant_pk)
    stock = get_object_or_404(variant.stock, pk=stock_pk)
    ctx = {'stock': stock, 'product': product, 'variant': variant}
    return TemplateResponse(
        request,
        'dashboard/product/stock/detail.html',
        ctx)


@staff_member_required
@permission_required('product.edit_stock_location')
def stock_edit(request, product_pk, variant_pk, stock_pk=None):
    product = get_object_or_404(Product, pk=product_pk)
    variant = get_object_or_404(product.variants, pk=variant_pk)
    if stock_pk:
        stock = get_object_or_404(variant.stock, pk=stock_pk)
    else:
        stock = Stock()
    form = forms.StockForm(
        request.POST or None, instance=stock, variant=variant)
    if form.is_valid():
        form.save()
        messages.success(
            request, pgettext_lazy('Dashboard message', 'Saved stock'))
        return redirect(
            'dashboard:variant-details', product_pk=product.pk,
            variant_pk=variant.pk)
    ctx = {'form': form, 'product': product,
           'variant': variant, 'stock': stock}
    return TemplateResponse(
        request,
        'dashboard/product/stock/form.html',
        ctx)


@staff_member_required
@permission_required('product.edit_stock_location')
def stock_delete(request, product_pk, variant_pk, stock_pk):
    product = get_object_or_404(Product, pk=product_pk)
    variant = get_object_or_404(product.variants, pk=variant_pk)
    stock = get_object_or_404(Stock, pk=stock_pk)
    if request.method == 'POST':
        stock.delete()
        messages.success(
            request, pgettext_lazy('Dashboard message', 'Removed stock'))
        return redirect(
            'dashboard:variant-details', product_pk=product.pk,
            variant_pk=variant.pk)
    ctx = {'product': product, 'stock': stock, 'variant': variant}
    return TemplateResponse(
        request,
        'dashboard/product/stock/modal/confirm_delete.html',
        ctx)


@staff_member_required
@permission_required('product.view_product')
def product_images(request, product_pk):
    product = get_object_or_404(
        Product.objects.prefetch_related('images'), pk=product_pk)
    images = product.images.all()
    ctx = {
        'product': product, 'images': images, 'is_empty': not images.exists()}
    return TemplateResponse(
        request, 'dashboard/product/product_image/list.html', ctx)


@staff_member_required
@permission_required('product.edit_product')
def product_image_edit(request, product_pk, img_pk=None):
    product = get_object_or_404(Product, pk=product_pk)
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
        return redirect('dashboard:product-image-list', product_pk=product.pk)
    ctx = {'form': form, 'product': product, 'product_image': product_image}
    return TemplateResponse(
        request,
        'dashboard/product/product_image/form.html',
        ctx)


@staff_member_required
@permission_required('product.edit_product')
def product_image_delete(request, product_pk, img_pk):
    product = get_object_or_404(Product, pk=product_pk)
    image = get_object_or_404(product.images, pk=img_pk)
    if request.method == 'POST':
        image.delete()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message',
                'Removed image %s') % image.image.name)
        return redirect('dashboard:product-image-list', product_pk=product.pk)
    return TemplateResponse(
        request,
        'dashboard/product/product_image/modal/confirm_delete.html',
        {'product': product, 'image': image})


@staff_member_required
@permission_required('product.edit_product')
def variant_edit(request, product_pk, variant_pk=None):
    product = get_object_or_404(
        Product.objects.all(), pk=product_pk)
    if variant_pk:
        variant = get_object_or_404(product.variants.all(), pk=variant_pk)
    else:
        variant = ProductVariant(product=product)
    form = forms.ProductVariantForm(request.POST or None, instance=variant)
    attribute_form = forms.VariantAttributeForm(
        request.POST or None, instance=variant)
    if all([form.is_valid(), attribute_form.is_valid()]):
        form.save()
        attribute_form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Saved variant %s') % variant.name
        messages.success(request, msg)
        return redirect(
            'dashboard:variant-details', product_pk=product.pk,
            variant_pk=variant.pk)
    ctx = {'attribute_form': attribute_form, 'form': form, 'product': product,
           'variant': variant}
    return TemplateResponse(
        request,
        'dashboard/product/product_variant/form.html',
        ctx)


@staff_member_required
@permission_required('product.view_product')
def variant_details(request, product_pk, variant_pk):
    product = get_object_or_404(Product, pk=product_pk)
    qs = product.variants.prefetch_related(
        'stock__location',
        'product__product_class__variant_attributes__values')
    variant = get_object_or_404(qs, pk=variant_pk)

    # If the product class of this product assumes no variants, redirect to
    # product details page that has special UI for products without variants.

    if not product.product_class.has_variants:
        return redirect('dashboard:product-detail', pk=product.pk)

    stock = variant.stock.all()
    images = variant.images.all()
    costs_data = get_variant_costs_data(variant)
    ctx = {'images': images, 'product': product, 'stock': stock,
           'variant': variant, 'costs': costs_data['costs'],
           'margins': costs_data['margins'],
           'is_empty': not stock.exists()}
    return TemplateResponse(
        request,
        'dashboard/product/product_variant/detail.html',
        ctx)


@staff_member_required
@permission_required('product.view_product')
def variant_images(request, product_pk, variant_pk):
    product = get_object_or_404(Product, pk=product_pk)
    qs = product.variants.prefetch_related('images')
    variant = get_object_or_404(qs, pk=variant_pk)
    form = forms.VariantImagesSelectForm(request.POST or None, variant=variant)
    if form.is_valid():
        form.save()
        return redirect(
            'dashboard:variant-details', product_pk=product.pk,
            variant_pk=variant.pk)
    ctx = {'form': form, 'product': product, 'variant': variant}
    return TemplateResponse(
        request,
        'dashboard/product/product_variant/modal/select_images.html',
        ctx)


@staff_member_required
@permission_required('product.edit_product')
def variant_delete(request, product_pk, variant_pk):
    product = get_object_or_404(Product, pk=product_pk)
    variant = get_object_or_404(product.variants, pk=variant_pk)
    if request.method == 'POST':
        variant.delete()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message', 'Removed variant %s') % variant.name)
        return redirect('dashboard:product-detail', pk=product.pk)

    ctx = {'is_only_variant': product.variants.count() == 1,
           'product': product,
           'variant': variant}
    return TemplateResponse(
        request,
        'dashboard/product/product_variant/modal/confirm_delete.html',
        ctx)


@staff_member_required
@permission_required('product.view_properties')
def attribute_list(request):
    attributes = (ProductAttribute.objects.prefetch_related('values')
                  .order_by('name'))
    attribute_filter = ProductAttributeFilter(request.GET, queryset=attributes)
    attributes = [
        (attribute.pk, attribute.name, attribute.values.all())
        for attribute in attribute_filter.qs]
    attributes = get_paginator_items(
        attributes, settings.DASHBOARD_PAGINATE_BY, request.GET.get('page'))
    ctx = {
        'attributes': attributes, 'filter_set': attribute_filter,
        'is_empty': not attribute_filter.queryset.exists()}
    return TemplateResponse(
        request, 'dashboard/product/product_attribute/list.html', ctx)


@staff_member_required
@permission_required('product.view_properties')
def attribute_detail(request, pk):
    attributes = ProductAttribute.objects.prefetch_related('values').all()
    attribute = get_object_or_404(attributes, pk=pk)
    ctx = {
        'attribute': attribute,
        'is_empty': not attributes.exists()}
    return TemplateResponse(
        request, 'dashboard/product/product_attribute/detail.html', ctx)


@staff_member_required
@permission_required('product.edit_properties')
def attribute_edit(request, pk=None):
    if pk:
        attribute = get_object_or_404(ProductAttribute, pk=pk)
    else:
        attribute = ProductAttribute()
    form = forms.ProductAttributeForm(request.POST or None, instance=attribute)
    if form.is_valid():
        attribute = form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Updated attribute') if pk else pgettext_lazy(
                'Dashboard message', 'Added attribute')
        messages.success(request, msg)
        return redirect('dashboard:product-attribute-detail', pk=attribute.pk)
    ctx = {'attribute': attribute, 'form': form}
    return TemplateResponse(
        request,
        'dashboard/product/product_attribute/form.html',
        ctx)


@staff_member_required
@permission_required('product.edit_properties')
def attribute_delete(request, pk):
    attribute = get_object_or_404(ProductAttribute, pk=pk)
    if request.method == 'POST':
        attribute.delete()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message',
                'Removed attribute %s') % (attribute.name,))
        return redirect('dashboard:product-attributes')
    return TemplateResponse(
        request,
        'dashboard/product/product_attribute/modal/'
        'attribute_confirm_delete.html',
        {'attribute': attribute})


@staff_member_required
@permission_required('product.edit_properties')
def attribute_choice_value_edit(request, attribute_pk, value_pk=None):
    attribute = get_object_or_404(ProductAttribute, pk=attribute_pk)
    if value_pk:
        value = get_object_or_404(AttributeChoiceValue, pk=value_pk)
    else:
        value = AttributeChoiceValue(attribute_id=attribute_pk)
    form = forms.AttributeChoiceValueForm(
        request.POST or None, instance=value)
    if form.is_valid():
        form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Updated attribute\'s value')\
            if value_pk else pgettext_lazy(
                'Dashboard message', 'Added attribute\'s value')
        messages.success(request, msg)
        return redirect('dashboard:product-attribute-detail', pk=attribute_pk)
    ctx = {'attribute': attribute, 'value': value, 'form': form}
    return TemplateResponse(
        request,
        'dashboard/product/product_attribute/values/form.html',
        ctx)


@staff_member_required
@permission_required('product.edit_properties')
def attribute_choice_value_delete(request, attribute_pk, value_pk):
    value = get_object_or_404(AttributeChoiceValue, pk=value_pk)
    if request.method == 'POST':
        value.delete()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message',
                'Removed attribute\'s value %s') % (value.name,))
        return redirect('dashboard:product-attribute-detail', pk=attribute_pk)
    return TemplateResponse(
        request,
        'dashboard/product/product_attribute/values/modal/confirm_delete.html',
        {'value': value, 'attribute_pk': attribute_pk})


@staff_member_required
@permission_required('product.view_stock_location')
def stock_location_list(request):
    stock_locations = StockLocation.objects.all().order_by('name')
    stock_location_filter = StockLocationFilter(
        request.GET, queryset=stock_locations)
    stock_locations = get_paginator_items(
        stock_location_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))
    ctx = {
        'locations': stock_locations, 'filter_set': stock_location_filter,
        'is_empty': not stock_location_filter.queryset.exists()}
    return TemplateResponse(
        request,
        'dashboard/product/stock_location/list.html',
        ctx)


@staff_member_required
@permission_required('product.edit_stock_location')
def stock_location_edit(request, location_pk=None):
    if location_pk:
        location = get_object_or_404(StockLocation, pk=location_pk)
    else:
        location = StockLocation()
    form = forms.StockLocationForm(request.POST or None, instance=location)
    if form.is_valid():
        form.save()
        msg = pgettext_lazy(
            'Dashboard message for stock location',
            'Updated location') if location_pk else pgettext_lazy(
                'Dashboard message for stock location', 'Added location')
        messages.success(request, msg)
        return redirect('dashboard:product-stock-location-list')
    return TemplateResponse(
        request,
        'dashboard/product/stock_location/form.html',
        {'form': form, 'location': location})


@staff_member_required
@permission_required('product.edit_stock_location')
def stock_location_delete(request, location_pk):
    location = get_object_or_404(StockLocation, pk=location_pk)
    stock_count = location.stock_set.count()
    if request.method == 'POST':
        location.delete()
        messages.success(
            request, pgettext_lazy(
                'Dashboard message for stock location',
                'Removed location %s') % location)
        return redirect('dashboard:product-stock-location-list')
    ctx = {'location': location, 'stock_count': stock_count}
    return TemplateResponse(
        request,
        'dashboard/product/stock_location/modal/confirm_delete.html',
        ctx)


@require_POST
@staff_member_required
def ajax_reorder_product_images(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    form = forms.ReorderProductImagesForm(request.POST, instance=product)
    status = 200
    ctx = {}
    if form.is_valid():
        form.save()
    elif form.errors:
        status = 400
        ctx = {'error': form.errors}
    return JsonResponse(ctx, status=status)


@require_POST
@staff_member_required
def ajax_upload_image(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
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


@require_POST
@staff_member_required
def product_bulk_update(request):
    form = forms.ProductBulkUpdate(request.POST)
    if form.is_valid():
        form.save()
        count = len(form.cleaned_data['products'])
        msg = npgettext_lazy(
            'Dashboard message',
            '%(count)d product has been updated',
            '%(count)d products have been updated',
            number=count) % {'count': count}
        messages.success(request, msg)
    return redirect('dashboard:product-list')


@staff_member_required
def ajax_available_variants_list(request):
    """
    Returns variants list filtered by request GET parameters.
    Response format is as required by select2 field.
    """
    def get_variant_label(variant, discounts):
        return '%s, %s, %s' % (
            variant.sku, variant.display_product(),
            gross(variant.get_price_per_item(discounts)))

    available_products = Product.objects.get_available_products()
    queryset = ProductVariant.objects.filter(
        product__in=available_products).prefetch_related('product')
    search_query = request.GET.get('q', '')
    if search_query:
        queryset = queryset.filter(
            Q(sku__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(product__name__icontains=search_query))
    discounts = request.discounts
    variants = [
        {'id': variant.id, 'text': get_variant_label(variant, discounts)}
        for variant in queryset
    ]
    return JsonResponse({'results': variants})


@staff_member_required
def ajax_products_list(request):
    """
    Returns products list filtered by request GET parameters.
    Response format is as required by select2 field.
    """
    queryset = (
        Product.objects.all() if request.user.has_perm('product.view_product')
        else Product.objects.get_available_products())
    search_query = request.GET.get('q', '')
    if search_query:
        queryset = queryset.filter(Q(name__icontains=search_query))
    products = [
        {'id': product.id, 'text': str(product)} for product in queryset
    ]
    return JsonResponse({'results': products})
