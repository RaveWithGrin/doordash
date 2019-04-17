from __future__ import division
import requests
from pprint import pprint
from getpass import getpass

session = requests.Session()

creds = {}
creds['email'] = raw_input('Email: ')
creds['password'] = getpass()
login_url = 'https://api.doordash.com/v2/auth/web_login/'
result = session.post(login_url, data=creds)
consumer_id = result.json()['id']
orders_url = 'https://www.doordash.com/api/v2/consumer/{}/order_cart/?exclude_asap_info=true&index=1&cancelled=0'.format(
    consumer_id)
result = session.get(orders_url)

orders = result.json()['order_carts']
for order in orders:
    order_id = order['id']
    receipt = {
        'date': order['actual_delivery_time'],
        'restaurant': {
            'name': order['restaurant']['business']['name'],
            'location': order['restaurant']['address']['printable_address']
        },
        'cost': {
            'tip': '$' + str(int(order['tip_amount'])/100),
            'total': '$' + str((int(order['tip_amount']) + int(order['total']))/100)
        },
        'items': []
    }
    order_url = 'https://api.doordash.com/v2/order_carts/{}/?expand=store_order_carts&expand=store_order_carts.[delivery]&expand=store_order_carts.store.business&expand=store_order_carts.orders.order_items.[item,options]&expand=store_order_carts.orders.order_items.options.item_extra_option.item_extra&extra=subtotal,tax_amount,discount_amount,service_fee,delivery_fee,extra_sos_delivery_fee,min_order_fee,min_order_subtotal,min_age_requirement,promotions,store_order_carts,delivery_availability,tip_suggestions,cancelled_at,total_charged&extra=store_order_carts.[orders,delivery,tip_amount]&extra=store_order_carts.orders.dd4b_expense_code&extra=store_order_carts.store.business&extra=store_order_carts.store.business.id&extra=store_order_carts.store.phone_number&extra=store_order_carts.delivery.[status,delivery_address,pickup_address,dasher_approaching_customer_time,dasher_at_store_time,dasher_confirmed_time,store_confirmed_time,dasher_location_available,dasher_route_available,show_dynamic_eta,dasher,is_consumer_pickup,is_ready_for_consumer_pickup,fulfillment_type,has_external_courier_tracking,consumer_poc_number]&extra=store_order_carts.delivery.pickup_address.id&extra=store_order_carts.delivery.pickup_address.address.printable_address&extra=store_order_carts.delivery.delivery_address.address.printable_address&extra=store_order_carts.orders.order_items&extra=store_order_carts.orders.order_items.[id,unit_price,quantity,item,substitution_preference,special_instructions,options]&extra=store_order_carts.orders.order_items.options.[id,item_extra_option]&extra=store_order_carts.orders.order_items.options.item_extra_option.[name,description,id,item_extra]&extra=store_order_carts.orders.order_items.options.item_extra_option.item_extra.name&extra=store_order_carts.orders.order_items.item.[name,id,price]'.format(
        order_id)
    result = session.get(order_url)
    order_details = result.json()
    receipt['location'] = order_details['store_order_carts'][0]['delivery']['pickup_address']['address']['printable_address']
    for item in order_details['store_order_carts'][0]['orders'][0]['order_items']:
        receipt['items'].append({
            'name': item['item']['name'],
            'price': '$' + str(int(item['item']['price'])/100)
        })
    receipt['cost']['service_fee'] = '$' + \
        str(int(order_details['service_fee'])/100)
    receipt['cost']['delivery_fee'] = '$' + \
        str(int(order_details['delivery_fee'])/100)
    receipt['cost']['tax'] = '$' + str(int(order_details['tax_amount'])/100)
    receipt['cost']['subtotal'] = '$' + str(int(order_details['subtotal'])/100)
    pprint(receipt)
