import requests
from celery import shared_task
from django.conf import settings
from django.contrib.sites.models import Site
from templated_email import send_templated_mail, get_templated_mail
from django.core.mail import EmailMultiAlternatives

# CONFIRM_ORDER_TEMPLATE = 'order/confirm_order'
CONFIRM_ORDER_TEMPLATE = 'order/confirm_order_mail'
CONFIRM_PAYMENT_TEMPLATE = 'order/payment/confirm_payment'
CONFIRM_SHIPPED_TEMPLATE = 'order/confirm_shipped_mail'
CONFIRM_CANCEL_SHIPMENT_TEMPLATE = 'order/cancel_shipment_mail'
ORDER_DETAILS_TEMPLATE = 'order/order_details'
ORDER_DETAILS_TEMPLATE_STAFF = 'order/order_details_staff'


def _send_confirmation(address, url, template):
    site = Site.objects.get_current()
    send_templated_mail(
        from_email=settings.ORDER_FROM_EMAIL,
        recipient_list=[address],
        context={'site_name': site.name,
                 'url': url},
        template_name=template)


def send_simple_message(address, url, template, order=None):
    site = Site.objects.get_current()

    if order:
        orders = [order for order in order.get_lines()]
        t = get_templated_mail(
            template_name=template,
            from_email=settings.ORDER_FROM_EMAIL,
            to=[address],
            context={'site_name': site.name,
                     'url': url,
                     'orders': orders,
                     'order': order,
                     'address': order.shipping_address})
    else:
        t = get_templated_mail(
            template_name=template,
            from_email=settings.ORDER_FROM_EMAIL,
            to=[address],
            context={'site_name': site.name,
                     'url': url})

    response = requests.post(
        "https://api.mailgun.net/v3/{}/messages".format(settings.MAILGUN_DOMAIN_NAME),
        auth=("api", settings.MAILGUN_API_KEY),
        data={"from": "Al Rawaa Vape Sales {}".format(t.from_email),
              "to": [address],
              "subject": t.subject,
              "html": t.body})
    return response


@shared_task
def send_order_confirmation(address, url, order=None):
    # _send_confirmation(address, url, CONFIRM_ORDER_TEMPLATE)
    if order:
        send_simple_message(address, url, ORDER_DETAILS_TEMPLATE, order=order)
        # Fixme: send mails to the staffs
        send_simple_message(settings.STAFF_MAIL1, url, ORDER_DETAILS_TEMPLATE_STAFF, order=order)
        send_simple_message(settings.STAFF_MAIL2, url, ORDER_DETAILS_TEMPLATE_STAFF, order=order)
    else:
        send_simple_message(address, url, CONFIRM_ORDER_TEMPLATE)


# @shared_task
# def send_order_details(address, url, order):
#     send_simple_message(address, url, ORDER_DETAILS_TEMPLATE, order=order)


@shared_task
def send_shipped_confirmation(address, url):
    # _send_confirmation(address, url, CONFIRM_ORDER_TEMPLATE)
    send_simple_message(address, url, CONFIRM_SHIPPED_TEMPLATE)


@shared_task
def send_shipment_cancelled(address, url):
    # _send_confirmation(address, url, CONFIRM_ORDER_TEMPLATE)
    send_simple_message(address, url, CONFIRM_CANCEL_SHIPMENT_TEMPLATE)


@shared_task
def send_payment_confirmation(address, url):
    _send_confirmation(address, url, CONFIRM_PAYMENT_TEMPLATE)
