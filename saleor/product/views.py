import datetime
import json

from django.conf import settings
from django.http import HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from ..cart.utils import set_cart_cookie
from ..core.utils import get_paginator_items, serialize_decimal
from ..core.utils.filters import get_now_sorted_by, get_sort_by_choices
from .filters import ProductFilter, SORT_BY_FIELDS
from .models import (
    Category, PackageOffer, PackageOfferImage,
    ProductClass, Product, ProductAttribute, ProductVariant,
    AttributeChoiceValue)
from .utils import (
    get_availability, get_product_attributes_data, get_product_images,
    get_variant_picker_data, handle_cart_form, product_json_ld,
    products_for_cart, products_with_availability, products_with_details,
    get_ejuice_variant_picker_data)
from ..product.models import ProductVariant


def product_details(request, slug, product_id, form=None):
    """Product details page

    The following variables are available to the template:

    product:
        The Product instance itself.

    is_visible:
        Whether the product is visible to regular users (for cases when an
        admin is previewing a product before publishing).

    form:
        The add-to-cart form.

    price_range:
        The PriceRange for the product including all discounts.

    undiscounted_price_range:
        The PriceRange excluding all discounts.

    discount:
        Either a Price instance equal to the discount value or None if no
        discount was available.

    local_price_range:
        The same PriceRange from price_range represented in user's local
        currency. The value will be None if exchange rate is not available or
        the local currency is the same as site's default currency.
    """
    products = products_with_details(user=request.user)
    product = get_object_or_404(products, id=product_id)
    if product.get_slug() != slug:
        return HttpResponsePermanentRedirect(product.get_absolute_url())
    today = datetime.date.today()
    is_visible = (
        product.available_on is None or product.available_on <= today)
    if form is None:
        form = handle_cart_form(request, product, create_cart=False)[0]
    availability = get_availability(product, discounts=request.discounts,
                                    local_currency=request.currency)
    product_images = get_product_images(product)
    variant_picker_data = get_variant_picker_data(
        product, request.discounts, request.currency)
    product_attributes = get_product_attributes_data(product)
    show_variant_picker = all([v.attributes for v in product.variants.all()])
    json_ld_data = product_json_ld(product, availability, product_attributes)
    return TemplateResponse(
        request, 'product/details.html',
        {'is_visible': is_visible,
         'form': form,
         'availability': availability,
         'product': product,
         'product_attributes': product_attributes,
         'product_images': product_images,
         'show_variant_picker': show_variant_picker,
         'variant_picker_data': json.dumps(
             variant_picker_data, default=serialize_decimal),
         'json_ld_product_data': json.dumps(
             json_ld_data, default=serialize_decimal)})


def product_add_to_cart(request, slug, product_id):
    # types: (int, str, dict) -> None

    if not request.method == 'POST':
        return redirect(reverse(
            'product:details',
            kwargs={'product_id': product_id, 'slug': slug}))
    # TODO: remove these
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(request.POST)

    # products = products_for_cart(user=request.user)
    # if b'type=package' in request.body:
    #     params = request.POST
    #     package_offer = PackageOffer.objects.filter(id=params['package_offer_id'])[0]
    #     variants = ProductVariant.objects.all()
    #     variant_device = get_object_or_404(variants, pk=params['variant'])
    #     device = variant_device.product
    #     print(device)
    #     variant_ejuice60 = get_object_or_404(variants, pk=params['ejuiceSixty'])
    #     ejuice60 = variant_ejuice60.product
    #     print(ejuice60)
    #     variant_ejuice100 = get_object_or_404(variants, pk=params['ejuiceHundred'])
    #     ejuice100 = variant_ejuice100.product
    #     print(ejuice100)
    #     form1, cart = handle_cart_form(request, device, create_cart=True)
    #     form2, cart = handle_cart_form(request, ejuice60)
    #     form3, cart = handle_cart_form(request, ejuice100)
    #     form4, cart = handle_cart_form(request, package_offer.coil)
    #     form5, cart = handle_cart_form(request, package_offer.battery)
    #     forms = [form1, form2, form3, form4, form5]
    #     for form in forms:
    #         if form.is_valid():
    #             print('form!!')
    #             form.save()
    #             if request.is_ajax():
    #                 response = JsonResponse({'next': reverse('cart:index')}, status=200)
    #             else:
    #                 response = redirect('cart:index')
    #         else:
    #             if request.is_ajax():
    #                 response = JsonResponse({'error': form.errors}, status=400)
    #             else:
    #                 response = product_details(request, slug, device.id, form)
    #
    # else:
    #     product = get_object_or_404(products, pk=product_id)

    package_offer = {}
    if request.POST.get('type') == 'package':
        coil_variant = ProductVariant.objects.get(id=request.POST.get('coil_variant'))
        battery_variant = ProductVariant.objects.get(id=request.POST.get('battery_variant'))
        ejuice60_variant = ProductVariant.objects.get(id=request.POST.get('ejuice60_variant'))
        ejuice100_variant = ProductVariant.objects.get(id=request.POST.get('ejuice100_variant'))

        package_offer.update({'package_offer_id': request.POST['package_offer_id'],
                              'coil': coil_variant.as_data(),
                              'battery': battery_variant.as_data(),
                              'ejuice60': ejuice60_variant.as_data(),
                              'ejuice100': ejuice100_variant.as_data()})

    products = products_for_cart(user=request.user)
    product = get_object_or_404(products, pk=product_id)
    form, cart = handle_cart_form(request, product, create_cart=True, package_offer=package_offer or None)
    if form.is_valid():
        form.save()
        if request.is_ajax():
            response = JsonResponse({'next': reverse('cart:index')}, status=200)
        else:
            response = redirect('cart:index')
    else:
        if request.is_ajax():
            response = JsonResponse({'error': form.errors}, status=400)
        else:
            response = product_details(request, slug, product_id, form)

    if not request.user.is_authenticated:
        set_cart_cookie(cart, response)
    return response


def category_index(request, path, category_id):
    category = get_object_or_404(Category, id=category_id)
    actual_path = category.get_full_path()
    if actual_path != path:
        return redirect('product:category', permanent=True, path=actual_path,
                        category_id=category_id)
    products = (products_with_details(user=request.user)
                .filter(categories__id=category.id)
                .order_by('name'))
    product_filter = ProductFilter(
        request.GET, queryset=products, category=category)
    products_paginated = get_paginator_items(
        product_filter.qs, settings.PAGINATE_BY, request.GET.get('page'))
    products_and_availability = list(products_with_availability(
        products_paginated, request.discounts, request.currency))
    now_sorted_by = get_now_sorted_by(product_filter)
    arg_sort_by = request.GET.get('sort_by')
    is_descending = arg_sort_by.startswith('-') if arg_sort_by else False
    ctx = {'category': category, 'filter_set': product_filter,
           'products': products_and_availability,
           'products_paginated': products_paginated,
           'sort_by_choices': get_sort_by_choices(product_filter),
           'now_sorted_by': now_sorted_by,
           'is_descending': is_descending}
    if category.name.lower() == "package offers":
        return TemplateResponse(request, 'package_offer/index.html', ctx)
    return TemplateResponse(request, 'category/index.html', ctx)

"""
Package offer: Package offer details page
"""
def package_offer_details(request, slug, product_id, form=None):
    """Product details page

    The following variables are available to the template:

    product:
        The Product instance itself.

    is_visible:
        Whether the product is visible to regular users (for cases when an
        admin is previewing a product before publishing).

    form:
        The add-to-cart form.

    price_range:
        The PriceRange for the product including all discounts.

    undiscounted_price_range:
        The PriceRange excluding all discounts.

    discount:
        Either a Price instance equal to the discount value or None if no
        discount was available.

    local_price_range:
        The same PriceRange from price_range represented in user's local
        currency. The value will be None if exchange rate is not available or
        the local currency is the same as site's default currency.
    """
    # Attributes: Size and Nicotine Strength
    size_attr = ProductAttribute.objects.get(name='Size').id
    nicotine_strength_attr = ProductAttribute.objects.get(name='Nicotine Strength').id

    # AttributeChoiceValue
    sixty_ml_attr_choice = AttributeChoiceValue.objects.get(name='60 ML').id
    hundred_ml_attr_choice = AttributeChoiceValue.objects.get(name='100 ML').id
    three_mg_attr_choice = AttributeChoiceValue.objects.get(name='3 MG').id

    package_offer = get_object_or_404(PackageOffer, id=product_id)
    products = products_with_details(user=request.user)
    product = package_offer.device
    # size_attribute_id = ProductAttribute.objects.filter(name='Size')[0].id
    # ejuice_id = ProductClass.objects.filter(name='Ejuice')[0].id
    # ejuices = Product.objects.filter(product_class_id=ejuice_id)

    # TODO: Implement manager
    ejuices_60 = list(ProductVariant.objects
                      .filter(attributes__contains={size_attr: sixty_ml_attr_choice})
                      .filter(attributes__contains={nicotine_strength_attr: three_mg_attr_choice}))
    ejuices_100 = list(ProductVariant.objects
                       .filter(attributes__contains={size_attr: hundred_ml_attr_choice})
                       .filter(attributes__contains={nicotine_strength_attr: three_mg_attr_choice}))

    # product = get_object_or_404(products, id=product_id)
    # if product.get_slug() != slug:
    #     return HttpResponsePermanentRedirect(product.get_absolute_url())
    today = datetime.date.today()
    is_visible = (product.available_on is None or product.available_on <= today)
    if form is None:
        form = handle_cart_form(request, product, create_cart=False)[0]
    availability = get_availability(product, discounts=request.discounts,
                                    local_currency=request.currency)

    product_images = get_product_images(product)
    coil_images = get_product_images(package_offer.coil)
    battery_images = get_product_images(package_offer.battery)

    variant_picker_data = get_variant_picker_data(
        product, request.discounts, request.currency)
    variant_picker_data.update({'product_type': 'package'})

    # TODO: remove following
    # import pprint
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(variant_picker_data)
    # pp.pprint(ejuices_60[0].product)
    product_attributes = get_product_attributes_data(product)
    show_variant_picker = all([v.attributes for v in product.variants.all()])
    # json_ld_data = product_json_ld(product, availability, product_attributes)
    # print(get_ejuice_variant_pina tcker_data(ejuices_60))
    print(json.dumps(get_ejuice_variant_picker_data(ejuices_60), default=serialize_decimal))
    return TemplateResponse(
        request, 'product/package_offer/details2.html',
        {'form': form,
         'is_visible': is_visible,
         'package_offer': package_offer,
         'product': product,
         'availability': availability,
         'product_attributes': product_attributes,
         'product_images': product_images,
         'show_variant_picker': show_variant_picker,
         'variant_picker_data': json.dumps(
             variant_picker_data, default=serialize_decimal),
         'coil_images': coil_images[0],
         'battery_images': battery_images[0],
         'ejuice_60': json.dumps(
             get_ejuice_variant_picker_data(ejuices_60), default=serialize_decimal),
         'ejuice_100': json.dumps(
             get_ejuice_variant_picker_data(ejuices_100), default=serialize_decimal),
         'coil': package_offer.coil,
         'coil_variant': package_offer.coil.variants.all()[0].id,
         'battery': package_offer.battery,
         'battery_variant': package_offer.battery.variants.all()[0].id})
    # return TemplateResponse(
    #     request, 'product/details.html',
    #     {'is_visible': is_visible,
    #      'form': form,
    #      'availability': availability,
    #      'product': product,
    #      'product_attributes': product_attributes,
    #      'product_images': product_images,
    #      'show_variant_picker': show_variant_picker,
    #      'variant_picker_data': json.dumps(
    #          variant_picker_data, default=serialize_decimal),
    #      'json_ld_product_data': json.dumps(
    #          json_ld_data, default=serialize_decimal)})
