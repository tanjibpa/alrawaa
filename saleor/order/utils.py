from functools import wraps

from django.conf import settings
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import pgettext_lazy
from prices import Price
from satchless.item import InsufficientStock

from ..product.models import Stock
from ..userprofile.utils import store_user_address
from .models import Order, OrderLine
from . import GroupStatus
from ..product.models import ProductVariant
from ..discount.models import Voucher


def check_order_status(func):
    """Preserves execution of function if order is fully paid by redirecting
    to order's details page."""

    @wraps(func)
    def decorator(*args, **kwargs):
        token = kwargs.pop('token')
        order = get_object_or_404(Order, token=token)
        if order.is_fully_paid():
            return redirect('order:details', token=order.token)
        kwargs['order'] = order
        return func(*args, **kwargs)

    return decorator


def cancel_order(order):
    """Cancells order by cancelling all associated shipment groups."""
    for group in order.groups.all():
        cancel_delivery_group(group)


def recalculate_order(order):
    """Recalculates and assigns total price of order.
    Total price is a sum of items and shippings in order shipment groups."""
    prices = [
        group.get_total() for group in order
        if group.status != GroupStatus.CANCELLED]
    total_net = sum(p.net for p in prices)
    total_gross = sum(p.gross for p in prices)
    total = Price(
        net=total_net, gross=total_gross, currency=settings.DEFAULT_CURRENCY)
    total += order.shipping_price
    order.total = total
    order.save()


def attach_order_to_user(order, user):
    """Associates existing order with user account."""
    order.user = user
    store_user_address(user, order.billing_address, billing=True)
    if order.shipping_address:
        store_user_address(user, order.shipping_address, shipping=True)
    order.save(update_fields=['user'])


def fill_group_with_partition(group, partition, discounts=None):
    """Fills shipment group with order lines created from partition items."""
    for item in partition:
        add_variant_to_delivery_group(
            group, item.variant, item.get_quantity(), discounts,
            add_to_existing=False)
        if item.data and item.data.get('package_offer_id'):
            coil_variant = ProductVariant.objects.get(id=item.data['coil']['variant_id'])
            battery_variant = ProductVariant.objects.get(id=item.data['battery']['variant_id'])
            ejuice60_variant = ProductVariant.objects.get(id=item.data['ejuice60']['variant_id'])
            ejuice100_variant = ProductVariant.objects.get(id=item.data['ejuice100']['variant_id'])

            add_variant_to_delivery_group(
                group, coil_variant, item.get_quantity(), discounts,
                add_to_existing=True, package_offer=True)
            add_variant_to_delivery_group(
                group, battery_variant, item.get_quantity(), discounts,
                add_to_existing=False, package_offer=True)
            add_variant_to_delivery_group(
                group, ejuice60_variant, item.get_quantity(), discounts,
                add_to_existing=False, package_offer=True)
            add_variant_to_delivery_group(
                group, ejuice100_variant, item.get_quantity(), discounts,
                add_to_existing=False, package_offer=True)


def add_variant_to_delivery_group(
    group, variant, total_quantity, discounts=None, add_to_existing=True, package_offer=False):
    """Adds total_quantity of variant to group.
    Raises InsufficientStock exception if quantity could not be fulfilled.

    By default, first adds variant to existing lines with same variant.
    It can be disabled with setting add_to_existing to False.

    Order lines are created by increasing quantity of lines,
    as long as total_quantity of variant will be added.
    """
    quantity_left = (
        add_variant_to_existing_lines(
            group, variant, total_quantity) if add_to_existing
        else total_quantity)
    # if package_offer:
    price = variant.get_price_per_item(discounts)
    while quantity_left > 0:
        stock = variant.select_stockrecord()
        if not stock:
            raise InsufficientStock(variant)
        quantity = (
            stock.quantity_available
            if quantity_left > stock.quantity_available
            else quantity_left
        )

        if package_offer:
            unit_price_net = 0.00
            unit_price_gross = 0.00
        else:
            unit_price_net = price.net
            unit_price_gross = price.gross

        group.lines.create(
            product=variant.product,
            product_name=variant.display_product()[0:128],  # TODO: do something about it
            product_sku=variant.sku,
            quantity=quantity,
            unit_price_net=unit_price_net,
            unit_price_gross=unit_price_gross,
            stock=stock,
            stock_location=stock.location.name)
        Stock.objects.allocate_stock(stock, quantity)
        # refresh stock for accessing quantity_allocated
        stock.refresh_from_db()
        quantity_left -= quantity


def add_variant_to_existing_lines(group, variant, total_quantity):
    """Adds variant to existing lines with same variant.

    Variant is added by increasing quantity of lines with same variant,
    as long as total_quantity of variant will be added
    or there is no more lines with same variant.

    Returns quantity that could not be fulfilled with existing lines.
    """
    # order descending by lines' stock available quantity
    lines = group.lines.filter(
        product=variant.product, product_sku=variant.sku,
        stock__isnull=False).order_by(
        F('stock__quantity_allocated') - F('stock__quantity'))

    quantity_left = total_quantity
    for line in lines:
        quantity = (
            line.stock.quantity_available
            if quantity_left > line.stock.quantity_available
            else quantity_left)
        line.quantity += quantity
        line.save()
        Stock.objects.allocate_stock(line.stock, quantity)
        quantity_left -= quantity
        if quantity_left == 0:
            break
    return quantity_left


def cancel_delivery_group(group):
    """Cancells shipment group and (optionally) it's order if necessary."""
    for line in group:
        Stock.objects.deallocate_stock(line.stock, line.quantity)
    group.status = GroupStatus.CANCELLED
    group.save()


def merge_duplicates_into_order_line(line):
    """Merges duplicated lines in shipment group into one (given) line.
    If there are no duplicates, nothing will happen.
    """
    lines = line.delivery_group.lines.filter(
        product=line.product, product_name=line.product_name,
        product_sku=line.product_sku, stock=line.stock)
    if lines.count() > 1:
        line.quantity = sum([line.quantity for line in lines])
        line.save()
        lines.exclude(pk=line.pk).delete()


def change_order_line_quantity(line, new_quantity):
    """Change the quantity of ordered items in a order line."""
    line.quantity = new_quantity
    line.save()

    if not line.delivery_group.get_total_quantity():
        line.delivery_group.delete()
        order = line.delivery_group.order
        if not order.get_lines():
            order.create_history_entry(
                status=order.status, comment=pgettext_lazy(
                    'Order status history entry',
                    'Order cancelled. No items in order'))


def remove_empty_groups(line, force=False):
    """Removes order line and associated shipment group and order.
    Remove is done only if quantity of order line or items in group or in order
    is equal to 0."""
    source_group = line.delivery_group
    order = source_group.order
    if line.quantity:
        line.save()
    else:
        line.delete()
    if not source_group.get_total_quantity() or force:
        source_group.delete()
    if not order.get_lines():
        order.create_history_entry(
            status=order.status, comment=pgettext_lazy(
                'Order status history entry',
                'Order cancelled. No items in order'))


def move_order_line_to_group(line, target_group, quantity):
    """Moves given quantity of order line to another shipment group."""
    try:
        target_line = target_group.lines.get(
            product=line.product, product_name=line.product_name,
            product_sku=line.product_sku, stock=line.stock)
    except OrderLine.DoesNotExist:
        target_group.lines.create(
            delivery_group=target_group, product=line.product,
            product_name=line.product_name, product_sku=line.product_sku,
            quantity=quantity, unit_price_net=line.unit_price_net,
            stock=line.stock,
            stock_location=line.stock_location,
            unit_price_gross=line.unit_price_gross)
    else:
        target_line.quantity += quantity
        target_line.save()
    line.quantity -= quantity
    remove_empty_groups(line)
