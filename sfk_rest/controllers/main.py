# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Anoop Jayaprakash
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

import json
import inspect
import logging
import traceback
from werkzeug import exceptions
import odoo
from odoo import api
from odoo import http
from odoo import models
from odoo import release
from odoo.http import request
from odoo.http import Response

_logger = logging.getLogger(__name__)

REST_VERSION = {
    'server_version': release.version,
    'server_version_info': release.version_info,
    'server_serie': release.serie,
    'api_version': 2,
}

NOT_FOUND = {
    'error': 'unknown_command',
}

DB_INVALID = {
    'error': 'invalid_db',
}

FORBIDDEN = {
    'error': 'token_invalid',
}

NO_API = {
    'error': 'rest_api_not_supported',
}

LOGIN_INVALID = {
    'error': 'invalid_login',
}

DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'

Auth_key = 'key=AAAAqml-PGE:APA91bEPKqBbGHannr2U6TNNlpcLtdhowFdfU0F8fuUlieyPodQwGKCn8YFTqBTvPzJAVqXI' \
           '-7V1ARflugl4V_kpGQFXsV8-Rxyf1UjmEDqc1bI1oWt6wDoNQMAC_DegrL74DiOVRlFG '


def abort(message, rollback=False, status=403):
    response = Response(json.dumps(message, sort_keys=True, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=status)
    if request._cr and rollback:
        request._cr.rollback()
    exceptions.abort(response)


def check_token():
    token = request.params.get('token') and request.params.get('token').strip()
    print(token)
    if not token:
        abort(FORBIDDEN)
    env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
    uid = env['sfk_rest.token'].check_token(token)
    if not uid:
        abort(FORBIDDEN)
    request._uid = uid
    request._env = api.Environment(request.cr, uid, request.session.context or {})


def ensure_db():
    db = request.params.get('db') and request.params.get('db').strip()
    if db and db not in http.db_filter([db]):
        db = None
    if not db and request.session.db and http.db_filter([request.session.db]):
        db = request.session.db
    if not db:
        db = http.db_monodb(request.httprequest)
    if not db:
        abort(DB_INVALID, status=404)
    if db != request.session.db:
        request.session.logout()
    request.session.db = db
    try:
        env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
        module = env['ir.module.module'].search([['name', '=', "sfk_rest"]], limit=1)
        if module.state != 'installed':
            abort(NO_API, status=500)
    except Exception as error:
        _logger.error(error)
        abort(DB_INVALID, status=404)


def check_params(params):
    missing = []
    for key, value in params.items():
        if not value:
            missing.append(key)
    if missing:
        abort({'error': "arguments_missing %s" % str(missing)}, status=400)


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj, item=None):
        def encode(item):
            if isinstance(item, models.BaseModel):
                vals = {}
                for name, field in item._fields.items():
                    if name in item:
                        if isinstance(item[name], models.BaseModel):
                            records = item[name]
                            if len(records) == 1:
                                vals[name] = (records.id, records.sudo().display_name)
                            else:
                                val = []
                                for record in records:
                                    val.append((record.id, record.sudo().display_name))
                                vals[name] = val
                        else:
                            try:
                                vals[name] = item[name].decode()
                            except UnicodeDecodeError:
                                vals[name] = item[name].decode('latin-1')
                            except AttributeError:
                                vals[name] = item[name]
                    else:
                        vals[name] = None
                return vals
            if inspect.isclass(item):
                return item.__dict__
            try:
                return json.JSONEncoder.default(self, item)
            except TypeError:
                return "error"

        try:
            try:
                result = {}
                for key, value in obj.items():
                    result[key] = encode(item)
                return result
            except AttributeError:
                result = []
                for item in obj:
                    result.append(encode(item))
                return result
        except TypeError:
            return encode(item)


class RESTController(http.Controller):

    # ----------------------------------------------------------
    # Login
    # ----------------------------------------------------------

    # merlin changed
    @http.route('/api/authenticate', auth="none", type='json', csrf=False)
    def api_authenticate(self, db=None, login=None, password=None, **kw):
        ensure_db()
        try:
            data = json.loads(request.httprequest.data)
            uid = request.session.authenticate(data['db'], data['login'], data['password'])
            if uid:
                env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
                user = request.env['res.users'].sudo().search([('id', '=', uid)])
                token = env['sfk_rest.token'].generate_token(uid)
                return {'status': 200, 'msg': "Success", 'token': token.token, 'user_id': uid,
                        'partner_id': user.partner_id, 'name': user.name,
                        'shop': user.branch_w_id.id,
                        'store': user.branch_l_id.id}
            else:
                return {'status': 201, 'msg': "Username or Password Incorrect"}
        except Exception as error:
            return {'status': 400, 'msg': "Technical Issue Please Contact Your Admin!"}

    # ----------------------------------------------------------
    # login refresh
    # -------------------------------------------------------
    @http.route('/api/authenticate/refresh', auth="none", type='json', csrf=False)
    def api_authenticate_refresh(self, **kw):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].refresh_token(data['token'])
            if uid:
                return {'status': 200, 'message': "Success ", 'body': uid}
            else:
                return {'status': 201, 'message': "Token authentication failed"}
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

        # ----------------------------------------------------------
        # customer creation
        # ----------------------------------------------------------

    @http.route(['/api/create/new/customer'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def create_new_customer(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                user = request.env['res.users'].sudo().search([('id', '=', uid)])
                customer = request.env['res.partner'].sudo().create({
                    'name': data['name'],
                    'phone': int(data['mobile']),
                    'street': data['street'],
                    'city': data['city'],
                    'state_id': int(data['state_id']),
                    'country_id': int(data['country_id']),
                    'zip': data['zip'],
                    'user_id': user.id,
                    "branch_id": user.branch_id.id,
                    'id_card': data['id_card'],
                    'cr_no': data['cr_no'],
                    'customer_true': True,
                    'is_shop_customer': True,
                })
                print("customer", customer)
                if customer:
                    return {'status': 200, 'message': 'Customer Created successfully'}
                else:
                    return {'status': 400, 'message': 'Issue in Creating customer'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}

        except Exception as error:
            _logger.error(error)
            return {'status': 400, 'message': 'An error occurred during Customer creation.'}

    # ----------------------------------------------------------
    # all customers
    # ----------------------------------------------------------
    @http.route(['/api/search/all/customer'], auth="public", type='http', csrf=False)
    def search_all_customer(self, **kw):
        try:
            customer_list = []
            for rec in request.env['res.partner'].sudo().search(
                    [('customer_true', '=', True), ('state', '=', 'done')]):
                dic = {
                    'id': rec.id if rec.id else None,
                    'name': rec.name if rec.name else None,
                    'mobile': rec.mobile if rec.mobile else None,
                    'street': rec.street if rec.street else None,
                    'city': rec.city if rec.city else None,
                    'state_id': rec.state_id.name if rec.state_id else None,
                    'country_id': rec.country_id.name if rec.country_id else None,
                    'zip': rec.zip if rec.zip else None,
                    'user_id': rec.user_id.id if rec.user_id else None,
                    'customer_credit': rec.customer_credit_limit,
                    "branch_id": rec.branch_id.id if rec.branch_id else None,
                }
                customer_list.append(dic)
            return Response(
                json.dumps({"data": customer_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ##################################CREATE NEW SALESMAN ###############################################
    @http.route(['/api/create/new/salesman'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def create_new_salesman(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                user = request.env['res.users'].sudo().search([('id', '=', uid)])
                customer = request.env['res.partner'].sudo().create({
                    'name': data['name'],
                    'mobile': int(data['mobile']),
                    'street': data['street'],
                    'city': data['city'],
                    'state_id': int(data['state_id']),
                    'country_id': int(data['country_id']),
                    'zip': data['zip'],
                    'sales_man_true': True,
                })
                if customer:
                    return {'status': 200, 'message': 'Salesman Created successfully'}
                else:
                    return {'status': 400, 'message': 'Issue in Creating Salesman'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}

        except Exception as error:
            _logger.error(error)
            return {'status': 400, 'message': 'An error occurred during Salesman creation.'}

    ######################### SEARCH ALL SALESMAN#####################################
    @http.route(['/api/search/all/salesman'], auth="public", type='http', csrf=False)
    def search_all_salesman(self, **kw):
        try:
            customer_list = []
            for rec in request.env['res.partner'].sudo().search([('sales_man_true', '=', True)]):
                dic = {
                    'id': rec.id if rec.id else None,
                    'name': rec.name if rec.name else None,
                    'mobile': rec.mobile if rec.mobile else None,
                    'street': rec.street if rec.street else None,
                    'city': rec.city if rec.city else None,
                    'state_id': rec.state_id.name if rec.state_id else None,
                    'country_id': rec.country_id.name if rec.country_id else None,
                    'zip': rec.zip if rec.zip else None,
                    'incentive_amount': rec.incentive_amount,
                    'user_id': rec.user_id.id if rec.user_id else None,
                    'branch_id': rec.branch_id.id if rec.branch_id else None,
                }
                customer_list.append(dic)
            return Response(
                json.dumps({"data": customer_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ###############################################Create Walkin Customer#######################################################################
    @http.route(['/api/create/walk_in_customer'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def create_walkin_customer(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                walkin_customer = request.env['walkin.customer.line'].sudo().create({
                    'name': data['name'],
                    'phone': int(data['phone']),
                    'address': data['address'],
                    'vat_no': data['vat']

                })
                if walkin_customer:
                    return {'status': 200, 'message': 'Walkin Customer Created successfully',
                            'walkin_customer_id': walkin_customer.id}
                else:
                    return {'status': 400, 'message': 'Issue in Creating customer'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}

        except Exception as error:
            _logger.error(error)
            return {'status': 400, 'message': 'An error occurred during Customer creation.'}

    #################################################Get Walkin Customer Details################################################33
    @http.route(['/api/search/walk_in_customer'], auth="public", type='http', csrf=False)
    def search_walkin_customer(self, **kw):
        try:
            walkin_customer_list = []
            for rec in request.env['walkin.customer.line'].sudo().search([]):
                dic = {
                    'id': rec.id if rec.id else None,
                    'name': rec.name if rec.name else None,
                    'phone': rec.phone if rec.phone else None,
                    'address': rec.address if rec.address else None,
                    'vat': rec.vat_no if rec.vat_no else None,
                    # 'contact_type': rec.contact_type if rec.contact_type == 'customer' else None,
                }
                walkin_customer_list.append(dic)
            return Response(
                json.dumps({"data": walkin_customer_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ###########################################Sales Person List###################################################

    # ----------------------------------------------------------
    # create product
    # ----------------------------------------------------------

    @http.route(['/api/create/new/product'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def create_new_product(self, **kwargs):
        list_data = []
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                product = request.env['product.product'].sudo().create({
                    'name': data['name'],
                    'default_code': data['product_code'],
                    'cntr_max_price': data['cntr_max_price'],
                    'cntr_min_price': data['cntr_min_price'],
                    'list_price': data['selling_price'],
                    'traders_price': data['internal_do_price'],
                    'project_price': data['project_do_price'],
                    'cash_sale_price': data['cash_sale_price'],
                    'cash_sale_count': data['cash_sale_count'],
                    'invoice_policy': 'order',
                    'detailed_type': 'product',
                    'product_type': str(data['product_type']),
                })
                if product:
                    return {'status': 200, 'message': 'Product created successfully',
                            'product_id': product.id}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
            return {'status': 400, 'message': 'An error occurred during product creation.'}

    # ----------------------------------------------------------
    # all product
    # ----------------------------------------------------------
    @http.route(['/api/search/all/product'], auth="public", type='http', csrf=False)
    def search_all_product(self, **kw):
        try:
            product_list = []
            for rec in request.env['product.product'].sudo().search([('state', '=', 'done')]):
                dic = {
                    'id': rec.id if rec.id else None,
                    'product_code': rec.default_code if rec.default_code else None,
                    'name': rec.name if rec.name else None,
                    'cost': rec.standard_price if rec.standard_price else None,
                    'cntr_min_price': rec.cntr_min_price,
                    'cntr_max_price': rec.cntr_max_price,
                    'internal_do_price': rec.traders_price,
                    'project_do_price': rec.project_price,
                    'cash_sale_price': rec.cash_sale_price,
                    'cash_sale_count': rec.cash_sale_count,
                    'branch_id': rec.branch_id.id if rec.branch_id else None,
                    'categ_id': rec.categ_id.id if rec.categ_id.id else None,
                    'units': [{
                        'unit': data.unit if data.unit else None,
                        'conversion': data.conversion if data.conversion else None
                    } for data in rec.related_units_ids]
                }
                product_list.append(dic)
            if product_list:

                return Response(
                    json.dumps({"data": product_list, 'message': 'Success', 'success': True},
                               sort_keys=True, indent=4, cls=ObjectEncoder),
                    content_type='application/json;charset=utf-8', status=200)
            else:
                return Response(json.dumps({'message': 'Product Not Found', 'success': True},
                                           sort_keys=True, indent=4, cls=ObjectEncoder),
                                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ####################################Shop Api##############################################################

    @http.route(['/api/search/shop'], auth="public", type='http', csrf=False)
    def search_shop(self, **kw):
        try:
            shop_list = []
            for rec in request.env['stock.location'].sudo().search([('shop_location', '=', True)]):
                dic = {
                    'id': rec.id if rec.id else None,
                    'name': rec.name if rec.name else None,
                    'company_id': rec.company_id.id if rec.company_id.id else None,
                    'branch_id': rec.branch_id.id if rec.branch_id.id else None,
                }
                shop_list.append(dic)
            return Response(json.dumps({"data": shop_list, 'message': 'Success', 'success': True},
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ##################################Create Product Cateory############################################################
    @http.route(['/api/create/product/category'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def create_product_category(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                category = request.env['product.category'].sudo().create({
                    'name': data['name']
                })
                if category:
                    return {'status': 200, 'message': 'Product Category Created successfully',
                            'categ_id': category.id}
                else:
                    return {'status': 400, 'message': 'Issue in Creating Product Category'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}

        except Exception as error:
            _logger.error(error)
            return {'status': 400, 'message': 'An error occurred during Customer creation.'}

    #############################################Product Category Api####################################################

    @http.route(['/api/product/category'], auth="public", type='http', csrf=False)
    def search_product_category(self, **kw):
        try:
            category_list = []
            for rec in request.env['product.category'].sudo().search([]):
                dic = {
                    'id': rec.id if rec.id else None,
                    'name': rec.name if rec.name else None,
                    # 'contact_type': rec.contact_type if rec.contact_type == 'customer' else None,
                }
                category_list.append(dic)
            return Response(
                json.dumps({"data": category_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ################################create delivery orders#############################
    @http.route(['/api/create/delivery/order'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def create_delivery_order(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                user = request.env['res.users'].sudo().search([('id', '=', uid)])
                partner = request.env['res.partner'].sudo().search(
                    [('id', '=', int(data['partner_id'])), ('state', '=', 'done')])
                delivery_order = request.env['sale.order'].sudo().create({
                    'do_customer_id': partner.id,
                    'partner_id': partner.id,
                    'state': 'draft',
                    'sale_types': 'do',
                    'normal_do': True,
                    'available_balance': partner.customer_credit_limit,
                    # 'over_due_amt': float(data['over_due_amt']),
                    'salesman_id': int(data['salesman_id']),
                    "narration": data['narration'],
                })
                for rec in data['lines']:
                    product = request.env['product.product'].sudo().search(
                        [('id', '=', int(rec['product_id'])), ('state', '=', 'done')])
                    if product:
                        lines = request.env['sale.order.line'].sudo().create(
                            {'product_id': product.id, 'product_uom_qty': float(rec['qty']),
                             'rate': float(rec['rate']), 'order_id': delivery_order.id})
                if delivery_order:
                    delivery_order.sudo()._onchange_do_customer()
                    delivery_order.sudo()._onchange_line_id()
                    delivery_order.sudo()._onchange_line_ids()
                    return {'status': 200, 'message': 'Delivery order created successfully',
                            'delivery_order_id': delivery_order.id}
                else:
                    return {'status': 202, 'message': 'Delivery Order created failed'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
            return {'status': 400, 'message': 'An error occurred during Delivery Order creation.'}

    ###########################Search all Delivery Orders ########################################################################

    @http.route(['/api/search/delivery/order'], auth="public", type='http', csrf=False)
    def search_delivery_order(self, **kw):
        try:
            delivery_list = []
            order_lines = []
            sale = request.env['sale.order'].sudo().search(
                [('sale_types', '=', 'do'), ('normal_do', '=', True), ('state', '=', 'sale')])
            if sale:
                for rec in sale:
                    for res in rec.order_line:
                        list = {
                            'product_id': res.product_id.id if res.product_id.id else None,
                            'qty': res.product_uom_qty if res.product_uom_qty else None,
                            'rate': res.rate if res.rate else None,
                            'bottom_price': res.bottom_price if res.bottom_price else None,
                            'gross': res.gross if res.gross else None,
                            'sale_type': res.sale_type if res.sale_type else None,
                            'discount_on_foc': res.discount_on_foc if res.discount_on_foc else None,
                            'discounts': res.discounts if res.discounts else None,
                            'net_value': res.net_value if res.net_value else None, }
                        order_lines.append(list)
                    dic = {
                        'name': rec.partner_id.id if rec.partner_id else None,
                        'salesman': rec.salesman_id.id if rec.salesman_id else None,
                        'order_date': str(rec.date_order),
                        'total_net': rec.total_net,
                        'total_qty': rec.total_qty,
                        'total_bottom_price': rec.total_bottom_price,
                        'total_gross': rec.total_gross,
                        'total_disc_on_foc': rec.total_disc_on_foc,
                        'total_discount_amount': rec.discount_amount,
                        'total_vat': rec.total_vat,
                        'total_net_value': rec.total_net_value,
                        'state': rec.state,
                        'order_id': rec.id if rec.id else None,
                        'branch_id': rec.branch_id.id if rec.branch_id else None,
                        'gsm_no': rec.gsm_no if rec.gsm_no else None,
                        'sequence_no': rec.sequence_number if rec.sequence_number else None,
                        'available_balance': rec.available_balance if rec.available_balance else None,
                        'customer_no': rec.customer_no if rec.customer_no else None,
                        'order_lines': order_lines,
                    }
                    delivery_list.append(dic)
            return Response(
                json.dumps({"data": delivery_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ############################################# specific delivery order info#################################33
    # ----------------------------------------------------------
    @http.route(['/api/search/each/delivery/order'], auth="public", type='http', csrf=False)
    def search_each_delivery_order(self, **kw):
        try:
            data = json.loads(request.httprequest.data)
            cash_memo_list = []
            for rec in request.env['sale.order'].sudo().search([('id', '=', data['order_id'])]):
                dic = {
                    'name': rec.name if rec.name else None,
                    'customer': rec.partner_id.name,
                    'state': dict(request.env['sale.order']._fields['state'].selection).get(
                        rec.state) if rec.state else None,
                    # 'cash_memo_id': rec.id if rec.id else None,
                    'payment_term_id': rec.payment_term_id.id if rec.payment_term_id else None,
                    'commitment_date': str(rec.commitment_date) if rec.commitment_date else None,
                    'order_line': []
                }
                for line in rec.order_line:
                    line_data = {
                        "product_id": line.product_id.name if line.product_id.name else None,
                        "description": line.name if line.name else None,
                        # "price_unit": line.price_unit if line.price_unit else None,
                        "qty": line.qty if line.qty else None,
                        "rate": line.rate if line.rate else None,
                    }
                    dic['order_line'].append(line_data)
                cash_memo_list.append(dic)
                print(cash_memo_list)
            return Response(
                json.dumps({"data": cash_memo_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ###################################Delivery order Confirmation#########################################################

    @http.route(['/api/delivery/order/confirm'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def confirm_delivery_order(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                orders = request.env['sale.order'].sudo().search(
                    [('state', '=', 'draft'), ('id', '=', int(data['delivery_order_id'])),
                     ('sale_types', '=', 'do')])
                if orders:
                    orders.action_confirm()
                    return {'status': 200, 'message': 'Delivery Order Confirmed successfully.',
                            'order_id': orders.id}
                else:
                    return Response(
                        json.dumps({"data": None, 'message': "Failed", 'success': False},
                                   sort_keys=True, indent=4, cls=ObjectEncoder),
                        content_type='application/json;charset=utf-8', status=202)
            else:
                return {'status': 202, 'message': 'Token authentication failed'}

        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}

        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    # ----------------------------------------------------------
    # Get All Payment Terms
    # -------------------------------------------------------

    @http.route(['/api/get/payment/terms'], auth="public", type='http', csrf=False)
    def get_payment_terms(self, **kwargs):
        try:
            payment_terms = []
            for rec in request.env['account.payment.term'].sudo().search([]):
                dic = {
                    'name': rec.name if rec.name else None,
                    'payment_term_id': rec.id if rec.id else None
                }
                payment_terms.append(dic)
            return Response(
                json.dumps({"data": payment_terms, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    # ----------------------------------------------------------
    # CREATE CASH MEMO
    # -------------------------------------------------------

    @http.route(['/api/create/cash/memo'], auth="public", methods=['POST'], type='json', csrf=False)
    def create_cash_memo(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                order_lines = []
                for prod in data['lines']:
                    product = request.env['product.product'].sudo().search(
                        [('id', '=', int(prod['product_id']))])
                    if product:
                        order_lines.append((0, 0, {
                            'product_id': prod['product_id'],
                            'price_unit': float(prod['price_unit']),
                            'product_uom_qty': float(prod['quantity']),
                            'rate': float(prod['rate'])
                        }))
                user = request.env['res.users'].sudo().search([('id', '=', uid)])
                walk_customer = request.env['res.partner'].sudo().search(
                    [('shop_id', '=', user.branch_l_id.id)], limit=1, )
                cash_memo = request.env['sale.order'].sudo().create({
                    'partner_id': walk_customer.id,
                    'customer': data['customer'],
                    'gsm_no': data['gsm_no'],
                    'address': data['address'],
                    'vat_no': data['vat_no'],
                    'branch_id': user.branch_id.id,
                    'salesmen': int(data['sales_man_id']),
                    'sales_account': int(data['sales_account']),
                    'sequence_number': data['sequence_number'],
                    'narration': data['narration'],
                    'order_line': order_lines,
                    'sale_types': 'cm',
                    'cash_memo': True,
                })
                if cash_memo:
                    cash_memo.sudo()._onchange_line_id()
                    cash_memo.sudo()._onchange_line_ids()
                    return {'status': 200, 'message': 'Cash memo created successfully',
                            'cash_memo_id': cash_memo.id}
                else:
                    return {'status': 202, 'message': 'Cash memo created failed'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
            return {'status': 400, 'message': 'An error occurred during cash memo creation.'}

    # ----------------------------------------------------------
    # CONFIRM CASH MEMO
    # -------------------------------------------------------

    @http.route(['/api/confirm/cash/memo'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def confirm_cash_memo(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                cash_memo = request.env['sale.order'].sudo().search(
                    [('id', '=', data['cash_memo_id']), ('state', '=', 'draft')])
                if cash_memo:
                    cash_memo.sudo().action_confirm_cash_memo()
                    return {'status': 200, 'message': 'Cash memo confirm successfully'}
                else:
                    return {'status': 202, 'message': 'Cash memo not found in the system'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
            return {'status': 400, 'message': 'An error occurred during cash memo confirmation.'}

    # ----------------------------------------------------------
    # GET ALL CASH MEMO
    # -------------------------------------------------------

    @http.route(['/api/get/cash/memo'], auth="public", type='http', csrf=False)
    def get_cash_memo(self, **kw):
        try:
            cash_memo_list = []
            order_lines = []
            cash_memo = request.env['sale.order'].sudo().search(
                [('state', '=', 'sale'), ('sale_types', '=', 'cm')])
            for rec in cash_memo:
                for res in rec.order_line:
                    list = {
                        'product_id': res.product_id.id if res.product_id.id else None,
                        'qty': res.product_uom_qty if res.product_uom_qty else None,
                        'rate': res.rate if res.rate else None,
                        'bottom_price': res.bottom_price if res.bottom_price else None,
                        'gross': res.gross if res.gross else None,
                        'sale_type': res.sale_type if res.sale_type else None,
                        'discount_on_foc': res.discount_on_foc if res.discount_on_foc else None,
                        'discounts': res.discounts if res.discounts else None,
                        'net_value': res.net_value if res.net_value else None, }
                    order_lines.append(list)
                dic = {
                    'cash_memo_name': rec.name if rec.name else None,
                    'created_date': rec.date_order.strftime('%d-%m-%y'),
                    'walking_customer': rec.partner_id.id,
                    'cash_memo_id': rec.id if rec.id else None,
                    'customer_name': rec.customer if rec.customer else None,
                    'salesman': rec.salesmen.id if rec.salesmen else None,
                    'vat_no': rec.vat_no,
                    'total_net': rec.total_net,
                    'total_qty': rec.total_qty,
                    'total_bottom_price': rec.total_bottom_price,
                    'total_gross': rec.total_gross,
                    'total_disc_on_foc': rec.total_disc_on_foc,
                    'total_discount_amount': rec.discount_amount,
                    'total_vat': rec.total_vat,
                    'total_net_value': rec.total_net_value,
                    'state': rec.state,
                    'branch_id': rec.branch_id.id if rec.branch_id else None,
                    'gsm_no': rec.gsm_no if rec.gsm_no else None,
                    'sequence_no': rec.sequence_number if rec.sequence_number else None,
                    'order_lines': order_lines,
                }
                cash_memo_list.append(dic)
            return Response(
                json.dumps({"data": cash_memo_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    # ----------------------------------------------------------
    # SPECIFIC CASH MEMO
    # -------------------------------------------------------

    @http.route(['/api/get/specific/cash/memo'], auth="public", type='http', csrf=False)
    def search_specific_cash_memo(self, **kw):
        try:
            data = json.loads(request.httprequest.data)
            cash_memo_list = []
            for rec in request.env['sale.order'].sudo().search([('id', '=', data['cash_memo_id'])]):
                dic = {
                    'cash_memo_name': rec.name if rec.name else None,
                    'walking_customer': rec.partner_id.name,
                    'customer': rec.customer if rec.customer else None,
                    'gsm_no': rec.gsm_no if rec.gsm_no else None,
                    'vat_no': rec.vat_no if rec.vat_no else None,
                    'branch': rec.branch_id.name if rec.branch_id.name else None,
                    'salesmen': rec.salesmen.name if rec.salesmen.name else None,
                    'sales_account': rec.sales_account if rec.sales_account else None,
                    'state': dict(request.env['sale.order']._fields['state'].selection).get(
                        rec.state) if rec.state else None,
                    'order_line': []
                }
                for line in rec.order_line:
                    line_data = {
                        "product_id": line.product_id.name if line.product_id.name else None,
                        "description": line.name if line.name else None,
                        "price_unit": line.price_unit if line.price_unit else None,
                        "product_uom_qty": line.product_uom_qty if line.product_uom_qty else None,
                        "rate": line.rate if line.rate else None,
                    }
                    dic['order_line'].append(line_data)
                cash_memo_list.append(dic)
            return Response(
                json.dumps({"data": cash_memo_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ############################################## Quotation##################################################################################

    @http.route(['/api/create/quotation'], auth="public", methods=['POST'], type='json', csrf=False)
    def create_quotation(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                order_lines = []
                for prod in data['lines']:
                    product = request.env['product.product'].sudo().search(
                        [('id', '=', prod['item_id'])])
                    if product:
                        order_lines.append((0, 0, {
                            'item_id': int(prod['item_id']),
                            'qty': float(prod['quantity']),
                            'rate': float(prod['rate']),
                            'units': float(prod['units'])
                        }))
                user = request.env['res.users'].sudo().search([('id', '=', uid)])
                quotation = request.env['sale.quotation'].sudo().create({
                    'partner_id': data['partner_id'],
                    'payment_term': str(data['payment_term']),
                    'delivery_terms': data['delivery_terms'],
                    'branch_id': user.branch_id.id,
                    'sales_man_id': data['sales_man_id'],
                    'line_ids': order_lines,
                })
                if quotation:
                    quotation.line_ids.sudo()._find_data()
                    quotation.line_ids.sudo()._calculate_gross()
                    quotation.line_ids.sudo()._calculate_gross_rate()
                    quotation.sudo()._onchange_line_ids()
                    return {'status': 200, 'message': 'Quotation created successfully',
                            'quotation_id': quotation.id}
                else:
                    return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
        return {'status': 400, 'message': 'An error occurred during sale quotation creation.'}

    ############################ Quotation Confirm############################

    @http.route(['/api/confirm/quotation'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def confirm_quotation(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                quotation = request.env['sale.quotation'].sudo().search(
                    [('id', '=', data['quotation_id']), ('state', '=', 'draft')])
                if quotation:
                    quotation.sudo().sale_confirm()
                    return {'status': 200, 'message': ' Sale Quotation confirm successfully'}
                else:
                    return {'status': 202, 'message': 'Sale Quotation not found in the system'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
            return {'status': 400,
                    'message': 'An error occurred during sale Quotation confirmation.'}

    ############################## Single Quotation ##########################################

    @http.route(['/api/get/specific/quotation'], auth="public", type='http', csrf=False)
    def search_specific_quotation(self, **kw):
        try:
            data = json.loads(request.httprequest.data)
            quotation_list = []
            for rec in request.env['sale.quotation'].sudo().search(
                    [('id', '=', data['quotation_id'])]):
                dic = {
                    'quotation_name': rec.name if rec.name else None,
                    'branch': rec.branch_id.name if rec.branch_id.name else None,
                    'sales_man_id': rec.sales_man_id.name if rec.sales_man_id.name else None,
                    'state': dict(request.env['sale.quotation']._fields['state'].selection).get(
                        rec.state) if rec.state else None,
                    'order_line': []
                }
                for line in rec.line_ids:
                    line_data = {
                        "item_id": line.item_id.name if line.item_id.name else None,
                        "description": line.description if line.description else None,
                        "qty": line.qty if line.qty else None,
                        "units": line.units if line.units else None,
                        "rate": line.rate if line.rate else None,
                    }
                    dic['order_line'].append(line_data)
                quotation_list.append(dic)
            return Response(
                json.dumps({"data": quotation_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    # ----------------------------------------------------------
    # GET ALL QUOTATION
    # -------------------------------------------------------

    @http.route(['/api/get/all/quotation'], auth="public", type='http', csrf=False)
    def get_all_quotation(self, **kw):
        try:
            quotation_list = []
            order_list = []
            for rec in request.env['sale.quotation'].sudo().search([]):
                for line in rec.line_ids:
                    list = {
                        "item_id": line.item_id.id if line.item_id.id else None,
                        "qty": line.qty if line.qty else None,
                        "units": line.units if line.units else None,
                        "rate": line.rate if line.rate else None,
                        "gross": line.gross if line.gross else None,
                        "sale_type":line.sale_type if line.sale_type else None,
                        "discount_on_foc":line.discount_on_foc if line.discount_on_foc else None,
                        "bottom_price":line.bottom_price if line.bottom_price else None,
                        "net_value":line.net_value if line.net_value else None,
                    }
                    order_list.append(list)
                dic = {
                    'quotation_name': rec.name if rec.name else None,
                    'created_date': rec.date.strftime('%d-%m-%y'),
                    'customer_name': rec.partner_id.name if rec.partner_id.name else None,
                    'sales_man': rec.sales_man_id.name if rec.sales_man_id.name else None,
                    'state': dict(request.env['sale.order']._fields['state'].selection).get(
                        rec.state) if rec.state else None,
                    'cash_memo_id': rec.id if rec.id else None,
                    'order_lines':order_list,
                    'gsm_no':rec.gsm_number_customer if rec.gsm_number_customer else None,
                    'total_qty':rec.total_qty if rec.total_qty else None,
                    'total_net':rec.total_net if rec.total_net else None,
                    'total_gross':rec.total_gross if rec.total_gross else None,
                    'total_bottom_price':rec.total_bottom_price if rec.total_bottom_price else None,
                    'total_net_value':rec.total_net_value if rec.total_net_value else None,
                    'total_vat':rec.total_vat if rec.total_vat else None,
                    'total_disc_on_foc':rec.total_disc_on_foc if rec.total_disc_on_foc else None,
                }
                quotation_list.append(dic)
            return Response(
                json.dumps({"data": quotation_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    #####################################Create Invoice##################################################################

    @http.route(['/api/create/invoice'], auth="public", methods=['POST'], type='json', csrf=False)
    def create_invoice(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                order_lines = []
                for prod in data['product']:
                    product = request.env['product.product'].sudo().search(
                        [('default_code', '=', 'order_id')])
                    if product:
                        order_lines.append((0, 0, {
                            'order_id': ['order_id'],
                            'partner_id': prod['partner_id'],
                        }))
                user = request.env['res.users'].sudo().search([('id', '=', uid)])
                invoice = request.env['customer.invoice'].sudo().create({
                    'partner_id': data['partner_id'],
                    'branch_id': user.branch_id.id,
                    'salesman_id': data['salesman_id'],
                    'dln_no': data['dln_no'],
                    'available_balance': data['available_balance'],
                    'customer_invoice_ids': order_lines,
                })
                if invoice:
                    return {'status': 200, 'message': 'Invoice created successfully',
                            'invoice_id': invoice.id}
                else:
                    return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
        return {'status': 400, 'message': 'An error occurred during sale invoice creation.'}

    #################################################Get All Invoice#########################################################################

    # @http.route(['/api/get/all/invoices'], auth="public", type='http', csrf=False)
    # def get_all_invoice(self, **kw):
    #     try:
    #         invoice_list = []
    #         for rec in request.env['customer.invoice'].sudo().search([]):
    #             dic = {
    #                 'invoice_no': rec.invoice_no if rec.invoice_no else None,
    #                 'customer_name': rec.partner_id.name if rec.partner_id.name else None,
    #                 'salesman_id': rec.salesman_id.name if rec.salesman_id.name else None,
    #                 # 'total': rec.state,
    #                 'state': rec.state
    #             }
    #             invoice_list.append(dic)
    #         return Response(json.dumps({"data": invoice_list, 'message': 'Success', 'success': True},
    #                                    sort_keys=True, indent=4, cls=ObjectEncoder),
    #                         content_type='application/json;charset=utf-8', status=200)
    #     except Exception as error:
    #         _logger.error(error)
    #         abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ###################################Search Each Invoices#################################################################

    # @http.route(['/api/search/each/invoice'], auth="public", type='http', csrf=False)
    # def search_each_invoice(self, **kw):
    #     try:
    #         data = json.loads(request.httprequest.data)
    #         invoice_list = []
    #         for rec in request.env['customer.invoice'].sudo().search([('id', '=', data['order_id'])]):
    #             dic = {
    #                 'invoice_no': rec.invoice_no if rec.invoice_no else None,
    #                 'customer_name': rec.partner_id.name if rec.partner_id.name else None,
    #                 'salesman_id': rec.salesman_id.name if rec.salesman_id.name else None,
    #                 # 'total': rec.state,
    #                 'state': rec.state,
    #                 # 'cash_memo_id': rec.id if rec.id else None,
    #                 'customer_invoice_ids': []
    #             }
    #             for line in rec.customer_invoice_ids:
    #                 inv_date: line.date_order
    #                 line_data = {
    #                     "order_id": line.order_id.name if line.order_id.name else None,
    #                     "current_date": line.date_order.date().isoformat() if line.date_order else None
    #
    #                 }
    #                 dic['customer_invoice_ids'].append(line_data)
    #             invoice_list.append(dic)
    #             print(invoice_list)
    #         return Response(json.dumps({"data": invoice_list, 'message': 'Success', 'success': True},
    #                                    sort_keys=True, indent=4, cls=ObjectEncoder),
    #                         content_type='application/json;charset=utf-8', status=200)
    #     except Exception as error:
    #         _logger.error(error)
    #         abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ################################################Confirm Invoice###############################################################

    # @http.route(['/api/confirm/invoices'], auth="public", methods=['POST'], type='json', csrf=False)
    # def confirm_invoices(self, **kwargs):
    #     try:
    #         data = json.loads(request.httprequest.data)
    #         env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
    #         uid = env['sfk_rest.token'].check_token(data['token'])
    #         if uid:
    #             invoices = request.env['customer.invoice'].sudo().search(
    #                 [('id', '=', data['invoice_id'])])
    #             print("ttttttttttttttttttttttttttttttttttttttt", invoices)
    #             if invoices:
    #                 print(invoices)
    #                 invoices.sudo().invoice_confirm()
    #                 return {'status': 200, 'message': ' Invoice confirmed successfully'}
    #             else:
    #                 return {'status': 202, 'message': 'Invoice not found in the system'}
    #         else:
    #             return {'status': 202, 'message': 'Token authentication failed'}
    #     except KeyError as key_error:
    #         return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
    #     except Exception as error:
    #         _logger.error(error)
    #         return {'status': 400, 'message': 'An error occurred during confirmation.'}
    #

    ############################################store list###################################################################
    @http.route(['/api/search/store'], auth="public", type='http', csrf=False)
    def search_store(self, **kw):
        try:
            shop_list = []
            for rec in request.env['stock.warehouse'].sudo().search(
                    [('store_warehouse', '=', False)]):
                dic = {
                    'id': rec.id if rec.id else None,
                    'name': rec.name if rec.name else None,
                    'company_id': rec.company_id.id if rec.company_id else None
                    # 'contact_type': rec.contact_type if rec.contact_type == 'customer' else None,
                }
                shop_list.append(dic)
            return Response(json.dumps({"data": shop_list, 'message': 'Success', 'success': True},
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ######################################################Get All Branches#######################################################################

    @http.route(['/api/get/all/branches'], auth="public", type='http', csrf=False)
    def get_all_branches(self, **kw):
        try:
            branch_list = []
            for rec in request.env['res.branch'].sudo().search([]):
                dic = {
                    'id': rec.id if rec.id else None,
                    'branch_name': rec.name if rec.name else None,
                    # 'branch': rec.branch if rec.branch else None
                }
                branch_list.append(dic)
            return Response(json.dumps({"data": branch_list, 'message': 'Success', 'success': True},
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ################################### USER ACCOUNT DETAILS ########################################

    @http.route(['/api/get/all/sales/account'], auth="public", type='http', csrf=False)
    def get_all_sales_account(self, **kw):
        try:
            account_list = []
            for rec in request.env['res.users'].sudo().search([]):
                # ('account_type', '=', 'asset_receivable')
                dic = {
                    'user_id': rec.id if rec.id else None,
                    'cash_memo_receivable_account': rec.cash_memo_receivable_acc.id,
                    'do_receivable_account': rec.do_receivable_acc.id,
                    'cash_receipt_receivable_account': rec.cash_receipt_receivable_acc.id,
                    'sale_return_payable_account': rec.sale_return_payable_acc.id
                }
                account_list.append(dic)
            return Response(
                json.dumps({"data": account_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    #######################################Create User#########################################
    @http.route(['/api/create/user'], auth="public", methods=['POST'], type='json', csrf=False)
    def create_user(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                user = request.env['res.users'].sudo().create({
                    'name': data['name'],
                    'login': data['email']
                })
                if user:
                    return {'status': 200, 'message': 'User Created successfully',
                            'user_id': user.id}
                else:
                    return {'status': 400, 'message': 'Issue in Creating User Profile'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
            return {'status': 400, 'message': 'An error occurred during Customer creation.'}

    ###########################################Get All Users###########################################################
    @http.route(['/api/get/all/users'], auth="public", type='http', csrf=False)
    def get_all_users(self, **kw):
        try:
            users_list = []
            for rec in request.env['res.users'].sudo().search([]):
                # ('account_type', '=', 'asset_receivable')
                dic = {
                    'id': rec.id if rec.id else None,
                    'name': rec.name if rec.name else None,
                    'login': rec.login if rec.login else None
                }
                users_list.append(dic)
            return Response(json.dumps({"data": users_list, 'message': 'Success', 'success': True},
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ############################ STORE ##############################

    ################################### STORE Material Request####################
    @http.route(['/api/create/store/material_request'], auth="public", methods=['POST'],
                type='json',
                csrf=False)
    def create_material_request(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                order_lines = []
                for prod in data['product']:
                    product = request.env['product.product'].sudo().search(
                        [('id', '=', prod['items_id'])])
                    if product:
                        order_lines.append((0, 0, {
                            'items_id': int(prod['items_id']),
                            'description': prod['description'],
                            'requested_to': prod['requested_to'],
                            'qty': float(prod['quantity']),
                            'state': prod['state']
                        }))
                material = request.env['material.request'].sudo().create({
                    'narration': data['narration'],
                    'branch_id': data['branch_id'],
                    'sale_order_no': data['sale_order_no'],
                    "store_materials": True,
                    'line_ids': order_lines,
                })
                if material:
                    return {'status': 200, 'message': ' Store Material created successfully',
                            'material_id': material.id}
                else:
                    return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
        return {'status': 400,
                'message': 'An error occurred during Store Material Request creation.'}

    ##################################### STORE ALL MATERIAL REQUEST##########################################

    @http.route(['/api/get/all/store/material_request'], auth="public", type='http', csrf=False)
    def get_all_material(self, **kw):
        try:
            material_list = []
            for rec in request.env['material.request'].sudo().search(
                    [('store_materials', '=', True), ('state', '=', 'requested')]):
                dic = {
                    'name': rec.name if rec.name else None,
                    'created_date': rec.date.strftime('%d-%m-%y') if rec.date else None,
                    'branch_id': rec.branch_id.name if rec.branch_id and rec.branch_id.name else None,
                }
                material_list.append(dic)
            return Response(
                json.dumps({"data": material_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ######################### STORE  MATERIAL REQUEST IN ##########################

    @http.route(['/api/create/material_request_in'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def create_material_request_in(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = request.env
            uid = env['sfk_rest.token'].check_token(data.get('token'))
            if uid:
                order_lines = []
                for prod in data.get('product', []):
                    product = env['stock.picking'].sudo().search([
                        ('id', '=', prod.get('product_id')),
                        ('state', '!=', 'draft'),
                        ('store_mat_req', '=', True)
                    ])
                    if product:
                        order_lines.append((0, 0, {
                            'product_id': product.id,
                            'name': prod.get('description'),
                            'product_uom_qty': float(prod.get('quantity', 0.0)),
                        }))

                material = env['stock.picking'].sudo().create({
                    'picking_type_id': data.get('picking_type_id'),
                    'location_dest_id': data.get('location_dest_id'),
                    'location_id': data.get('location_id'),
                    'sto_no': data.get('sto_no'),
                    'move_ids_without_package': order_lines,
                })
                if material:
                    return {'status': 200, 'message': 'Material Request IN created successfully',
                            'material_id': material.id}
                else:
                    return {'status': 400,
                            'message': 'An error occurred during Material Request creation.'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}

        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}

        except Exception as error:
            _logger.error(error)
            return {'status': 400,
                    'message': 'An error occurred during Material Request IN creation.'}

    ############################# STORE ALL MATERIAL REQUEST IN#####################
    @http.route(['/api/get/all/material_request_out'], auth="public", type='http', csrf=False)
    def get_all_material_request(self, **kw):
        try:
            material_list = []
            for rec in request.env['stock.picking'].sudo().search([('state', '!=', 'draft'),
                                                                   ('store_mat_req', '=', True)]):
                dic = {
                    'picking_type_id': rec.picking_type_id.name if rec.picking_type_id.name else None,
                    'location_dest_id': rec.location_dest_id.name if rec.location_dest_id else None,
                    'location_id': rec.location_id.name if rec.location_id else None,

                }
                material_list.append(dic)
            return Response(
                json.dumps({"data": material_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    #################################  STORE MATERIAL REQUEST OUT #########################

    @http.route(['/api/create/material_request_out'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def create_store_material_request(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = request.env
            uid = env['sfk_rest.token'].check_token(data.get('token'))

            if uid:
                order_lines = []

                for prod in data.get('product', []):
                    product = env['stock.picking'].sudo().search([
                        ('id', '=', prod.get('product_id')),
                        ('state', '=', 'draft'),
                        ('store_mat_req', '=', True)
                    ])

                    if product:
                        order_lines.append((0, 0, {
                            'product_id': product.id,
                            'name': prod.get('description'),
                            'product_uom_qty': float(prod.get('quantity', 0.0)),
                        }))

                material = env['stock.picking'].sudo().create({
                    'picking_type_id': data.get('picking_type_id'),
                    'location_dest_id': data.get('location_dest_id'),
                    'location_id': data.get('location_id'),
                    'sto_no': data.get('sto_no'),
                    'move_ids_without_package': order_lines,
                })

                if material:
                    return {'status': 200, 'message': 'Material Request OUT created successfully',
                            'material_id': material.id}
                else:
                    return {'status': 400,
                            'message': 'An error occurred during Material Request OUT creation.'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}

        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}

        except Exception as error:
            _logger.error(error)
            return {'status': 400,
                    'message': 'An error occurred during Material Request OUT creation.'}

    #############################  STORE ALL MATERIAL REQUEST OUT #####################
    # @http.route(['/api/get/all/material_request_out'], auth="public", type='http', csrf=False)
    # def get_all_material_request_out(self, **kw):
    #     try:
    #         material_list = []
    #         for rec in request.env['stock.picking'].sudo().search([('state', '=', 'draft'),
    #                                                                ('shop_mat_req', '=', True)]):
    #             dic = {
    #                 'picking_type_id': rec.picking_type_id.name if rec.picking_type_id.name else None,
    #                 'location_dest_id': rec.location_dest_id.name if rec.location_dest_id else None,
    #                 'location_id': rec.location_id.name if rec.location_id else None,
    #
    #             }
    #             material_list.append(dic)
    #         return Response(json.dumps({"data": material_list, 'message': 'Success', 'success': True},
    #                                    sort_keys=True, indent=4, cls=ObjectEncoder),
    #                         content_type='application/json;charset=utf-8', status=200)
    #     except Exception as error:
    #         _logger.error(error)
    #         abort({'error': traceback.format_exc()}, rollback=True, status=400)

    @http.route(['/api/get/all/material_request_out'], auth="public", type='http', csrf=False)
    def get_all_material_request_out(self, **kw):
        try:
            material_list = []
            for rec in request.env['stock.picking'].sudo().search([('state', '=', 'draft'),
                                                                   ('store_mat_req', '=', True)]):
                dic = {
                    'picking_type_id': rec.picking_type_id.name if rec.picking_type_id else None,
                    'location_dest_id': rec.location_dest_id.name if rec.location_dest_id else None,
                    'location_id': rec.location_id.name if rec.location_id else None,
                    'sto_no': rec.sto_no if hasattr(rec, 'sto_no') else None,
                    'order_line': [],
                }

                for line in rec.move_ids_without_package:
                    line_data = {
                        "product_id": line.product_id.name if line.product_id else None,
                        "name": line.name if line.name else None,
                        "product_uom_qty": line.product_uom_qty if line.product_uom_qty else None,
                    }
                    dic['order_line'].append(line_data)

                material_list.append(dic)

            return Response(
                json.dumps({"data": material_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ################################SHOP MATERIAL REQUEST#################################
    @http.route(['/api/create/shop_material_request'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def create_shop_material_request(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                order_lines = []
                for prod in data['product']:
                    product = request.env['product.product'].sudo().search(
                        [('id', '=', prod['items_id'])])
                    if product:
                        order_lines.append((0, 0, {
                            'items_id': int(prod['items_id']),
                            'description': prod['description'],
                            'requested_to': prod['requested_to'],
                            'qty': float(prod['quantity']),
                            'state': prod['state']
                        }))
                material = request.env['material.request'].sudo().create({
                    # 'name': data['name'],
                    'narration': data['narration'],
                    'branch_id': data['branch_id'],
                    'sale_order_no': data['sale_order_no'],
                    "shop_materials": True,
                    'line_ids': order_lines,
                })
                print("material", material)
                if material:
                    return {'status': 200, 'message': ' Shop Material created successfully',
                            'material_id': material.id}
                else:
                    return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
        return {'status': 400,
                'message': 'An error occurred during  Shop Material Request creation.'}

    ####################### ALL SHOP MATERIAL REQUEST ########################

    @http.route(['/api/get/all/shop_material_request'], auth="public", type='http', csrf=False)
    def get_all_shop_material(self, **kw):
        print("rttttttttttttttttt")
        try:
            material_list = []
            for rec in request.env['material.request'].sudo().search(
                    [('shop_materials', '=', True)]):
                dic = {
                    'name': rec.name if rec.name else None,
                    'created_date': rec.date.strftime('%d-%m-%y') if rec.date else None,
                    'branch_id': rec.branch_id.name if rec.branch_id and rec.branch_id.name else None,
                    'sale_order_no': rec.sale_order_no.id if rec.sale_order_no.id and rec.sale_order_no.id else None

                }
                material_list.append(dic)
                print(material_list, 'mateeeeeeeeeeeeeeeeee')
            return Response(
                json.dumps({"data": material_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ######################## SHOP MATERIAL REQUEST IN #############################

    @http.route(['/api/create/shop_material_request_in'], auth="public", methods=['POST'],
                type='json', csrf=False)
    def create_shop_material_request_in(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = request.env
            uid = env['sfk_rest.token'].check_token(data.get('token'))

            if uid:
                order_lines = []

                for prod in data.get('product', []):
                    product = env['stock.picking'].sudo().search([
                        ('id', '=', prod.get('product_id')),
                        ('state', '!=', 'draft'),
                        ('shop_mat_req', '=', True)
                    ])

                    if product:
                        order_lines.append((0, 0, {
                            'product_id': product.id,
                            'name': prod.get('description'),
                            'product_uom_qty': float(prod.get('quantity', 0.0)),
                        }))

                material = env['stock.picking'].sudo().create({
                    'picking_type_id': data.get('picking_type_id'),
                    'location_dest_id': data.get('location_dest_id'),
                    'location_id': data.get('location_id'),
                    'sto_no': data.get('sto_no'),
                    'move_ids_without_package': order_lines,
                })

                if material:
                    return {'status': 200,
                            'message': ' Shop Material Request IN created successfully',
                            'material_id': material.id}
                else:
                    return {'status': 400,
                            'message': 'An error occurred during Shop Material Request creation.'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}

        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}

        except Exception as error:
            _logger.error(error)
            return {'status': 400,
                    'message': 'An error occurred during  Shop Material Request IN creation.'}

    ###################################################ALL SHOP MATERIAL REQUEST IN#######################

    @http.route(['/api/get/all/shop_material_request_in'], auth="public", type='http', csrf=False)
    def get_all_shop_material_request_in(self, **kw):
        try:
            material_list = []
            for rec in request.env['stock.picking'].sudo().search([('state', '!=', 'draft'),
                                                                   ('shop_mat_req', '=', True)]):
                dic = {
                    'picking_type_id': rec.picking_type_id.name if rec.picking_type_id.name else None,
                    'location_dest_id': rec.location_dest_id.name if rec.location_dest_id else None,
                    'location_id': rec.location_id.name if rec.location_id else None,

                }
                material_list.append(dic)
            return Response(
                json.dumps({"data": material_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ############################### SHOP MATERIAL REQUEST OUT#########################

    @http.route(['/api/create/shop_material_request_out'], auth="public", methods=['POST'],
                type='json', csrf=False)
    def create_shop_material_request_in(self, **kwargs):
        print("rrrrrrrrrrrrrrrrrrr")
        try:
            data = json.loads(request.httprequest.data)
            env = request.env
            uid = env['sfk_rest.token'].check_token(data.get('token'))

            if uid:
                order_lines = []

                for prod in data.get('product', []):
                    product = env['stock.picking'].sudo().search([
                        ('id', '=', prod.get('product_id')),
                        ('state', '=', 'draft'),
                        ('shop_mat_req', '=', True)
                    ])

                    if product:
                        order_lines.append((0, 0, {
                            'product_id': product.id,
                            'name': prod.get('description'),
                            'product_uom_qty': float(prod.get('quantity', 0.0)),
                        }))

                material = env['stock.picking'].sudo().create({
                    'picking_type_id': data.get('picking_type_id'),
                    'location_dest_id': data.get('location_dest_id'),
                    'location_id': data.get('location_id'),
                    'sto_no': data.get('sto_no'),
                    'move_ids_without_package': order_lines,
                })
                print("material", material)

                if material:
                    return {'status': 200,
                            'message': ' Shop Material Request OUT created successfully',
                            'material_id': material.id}
                else:
                    return {'status': 400,
                            'message': 'An error occurred during Shop Material Request OUT creation.'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}

        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}

        except Exception as error:
            _logger.error(error)
            return {'status': 400,
                    'message': 'An error occurred during  Shop Material Request OUT creation.'}

    ################################ ALL SHOP MATERIAL REQUEST OUT #########################
    @http.route(['/api/get/all/shop_material_request_out'], auth="public", type='http', csrf=False)
    def get_all_shop_material_request_out(self, **kw):
        print("qqqqqqqqqqqqqqqqqqqqq")
        try:
            material_list = []
            for rec in request.env['stock.picking'].sudo().search([('state', '=', 'draft'),
                                                                   ('shop_mat_req', '=', True)]):
                dic = {
                    'picking_type_id': rec.picking_type_id.name if rec.picking_type_id else None,
                    'location_dest_id': rec.location_dest_id.name if rec.location_dest_id else None,
                    'location_id': rec.location_id.name if rec.location_id else None,
                    'sto_no': rec.sto_no if hasattr(rec, 'sto_no') else None,
                    'order_line': [],
                }
                print("dict", dict)

                for line in rec.move_ids_without_package:
                    line_data = {
                        "product_id": line.product_id.name if line.product_id else None,
                        "name": line.name if line.name else None,
                        "product_uom_qty": line.product_uom_qty if line.product_uom_qty else None,
                    }
                    dic['order_line'].append(line_data)

                material_list.append(dic)

            return Response(
                json.dumps({"data": material_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ##########################  Create Invoice API ######################################

    @http.route(['/api/create/customer/invoice'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def create_customer_invoice(self, **kwargs):
        print("qqqqqqqqqqqqqqqqqqqq")
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, request.uid, {})
            uid = env['sfk_rest.token'].check_token(data.get('token'))
            print("ppppppppppppppppppppppppppppp")
            order_id = data['order_id']
            print('order_id', order_id)
            order_lines = []
            if uid:

                for rec in order_id:
                    print("heloooooo")
                    sale = request.env['sale.order'].sudo().search([('id', '=', int(rec))])
                    print("kkkkkkkkkkkkkk")
                    if sale:
                        order_lines.append((0, 0, {
                            'order_id': sale.id,
                            'date_order': sale.date_order,
                            'partner_id': sale.partner_id,
                            'amount_total': sale.amount_total,
                            "check_box": True
                        }))
                user = request.env['res.users'].sudo().search([('id', '=', uid)])
                invoice_values = {
                    'account_id': int(data.get('account_id')),
                    'dln_no': data.get('dln_no'),
                    'partner_id': int(data.get('partner_id')),
                    'branch_id': user.branch_id.id,
                    'gsm_no': data.get('gsm_no'),
                    'available_balance': float(data.get('available_balance', 0.0)),
                    'customer_invoice_ids': order_lines,
                }
                print("invoice_values", invoice_values)

                invoice = request.env['customer.invoice'].sudo().create(invoice_values)

                if invoice:
                    print(f"Invoice created successfully. Invoice ID: {invoice.id}")
                    return {'status': 200, 'message': 'Invoice created successfully',
                            'invoice_id': invoice.id}
                else:
                    print("Failed to create invoice")
                    return {'status': 400, 'message': 'Failed to create invoice'}
            else:
                print("Token authentication failed")
                return {'status': 401, 'message': 'Token authentication failed'}

        except json.JSONDecodeError as json_error:
            print(f'JSON decoding error: {json_error}')
            return {'status': 400, 'message': 'Invalid JSON format in the request'}

        except KeyError as key_error:
            print(f'Missing required parameter: {key_error}')
            return {'status': 400, 'message': f"Missing required parameter: {key_error}"}

        except Exception as error:
            print(f'An error occurred during Invoice creation. Error: {error}')
            return {'status': 500, 'message': 'An error occurred during Invoice creation.'}

    ################### Confirm Invoice API ##################################

    @http.route(['/api/confirm/invoices'], auth="public", methods=['POST'], type='json', csrf=False)
    def confirm_invoices(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                invoice = request.env['sale.order'].sudo().search(
                    [('id', '=', data['invoice_id']), ('state', '=', 'draft')])
                if invoice:
                    print(invoice)
                    invoice.sudo().action_confirm_do()
                    # customer_selected_invoice
                    return {'status': 200, 'message': 'Invoice confirm successfully'}
                else:
                    return {'status': 202, 'message': 'Invoice not found in the system'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
            return {'status': 400, 'message': 'An error occurred during invoice confirmation.'}

    ########################## Get Invoice All #######################

    @http.route(['/api/get/all/invoices'], auth="public", type='http', csrf=False)
    def get_all_invoice(self, **kw):
        print("wwwwwwwwwwwwwwww")
        try:
            invoice_list = []
            for rec in request.env['customer.invoice'].sudo().search([]):
                dic = {
                    'invoice_no': rec.invoice_no if rec.invoice_no else None,
                    'partner_id': rec.partner_id.name if rec.partner_id.name else None,
                    'salesman_id': rec.salesman_id.name if rec.salesman_id.name else None,
                    'account_id': rec.account_id.name if rec.account_id.name else None,
                    'branch_id': rec.branch_id.id if rec.branch_id.id else None,
                    'state': rec.state
                }
                print("dic", dic)
                invoice_list.append(dic)
            return Response(
                json.dumps({"data": invoice_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ########################### Each Search Invoice Api############################
    @http.route(['/api/search/each/invoice'], auth="public", type='http', csrf=False)
    def search_each_invoice(self, **kw):
        print("sssssssssssssssssss")
        try:
            data = json.loads(request.httprequest.data)
            invoice_list = []
            for rec in request.env['customer.invoice'].sudo().search(
                    [('id', '=', data['order_id'])]):
                dic = {
                    'invoice_no': rec.invoice_no if rec.invoice_no else None,
                    'partner_id': rec.partner_id.name if rec.partner_id.name else None,
                    'salesman_id': rec.salesman_id.name if rec.salesman_id.name else None,
                    'account_id': rec.account_id.name if rec.account_id.name else None,
                    'branch_id': rec.branch_id.id if rec.branch_id.id else None,
                    'state': rec.state,
                    # 'cash_memo_id': rec.id if rec.id else None,
                    'customer_invoice_ids': []
                }
                print("dic", dic)
                for line in rec.customer_invoice_ids:
                    inv_date: line.date_order
                    line_data = {
                        "order_id": line.order_id.name if line.order_id.name else None,
                        "current_date": line.date_order.date().isoformat() if line.date_order else None,
                        "partner_id": line.partner_id.name if line.partner_id.name else None,
                        "amount_total": str(line.amount_total) if isinstance(line.amount_total,
                                                                             (int, float)) else None

                    }
                    dic['customer_invoice_ids'].append(line_data)
                invoice_list.append(dic)
                print(invoice_list)
            return Response(
                json.dumps({"data": invoice_list, 'message': 'Success', 'success': True},
                           sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ##################################### SALES RETURN API ##############################
    @http.route(['/api/create/sales/return'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def create_sales_return(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, request.uid, {})
            uid = env['sfk_rest.token'].check_token(data.get('token'))

            if uid:
                order_lines = []
                for prod in data.get('product', []):
                    print("")
                    product = request.env['product.product'].sudo().search(
                        [('id', '=', prod.get('product_id'))])
                    if product:
                        order_lines.append((0, 0, {
                            'product_id': int(prod['product_id']),
                            'name': prod.get('description', ''),
                            'price_unit': float(prod.get('price_unit', 0.0)),
                            'product_uom_qty': float(prod.get('quantity', 0.0)),
                            'discount': float(prod.get('rate', 0.0)),
                            'sales_type': prod.get('sales_type', ''),
                            'discount_on_foc': float(prod.get('discount_on_foc', 0.0)),
                            'price_subtotal': float(prod.get('net_value', 0.0)),
                        }))
                user = request.env['res.users'].sudo().search([('id', '=', uid)])
                sales = request.env['sale.order'].sudo().create({
                    'partner_id': data.get('partner_id'),
                    'sales_account_return': str(data.get('sales_account_return')),
                    'return_inv_no': data.get('return_inv_no'),
                    'branch_id': user.branch_id.id,
                    # 'return_branch_id': data.get('return_branch_id'),
                    'return_gsm_no': data.get('return_gsm_no'),
                    'sale_return': True,
                    'order_line': order_lines,
                })
                sales.write({'state': 'return'})
                print("sales", sales)

                if sales:
                    return {'status': 200, 'message': 'Sales Return created successfully',
                            'sales_id': sales.id}
                else:
                    return {'status': 202, 'message': 'Error creating sales return'}
            else:
                return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
            return {'status': 400, 'message': 'An error occurred during sale return creation.'}

    ################################ ALL SALES RETURN #############################
    @http.route(['/api/get/all/sales_return'], auth="public", type='http', csrf=False)
    def get_all_sales_return(self, **kw):
        try:
            return_list = []
            for rec in request.env['sale.order'].sudo().search(
                    [('sale_return', '=', True), ('state', '=', 'return')]):
                dic = {
                    'return_inv_no': rec.return_inv_no.id if rec.return_inv_no else None,
                    'sales_account_return': rec.sales_account_return if rec.sales_account_return else None,
                    'partner_id': rec.partner_id.name if rec.partner_id and rec.partner_id.name else None,
                    'branch_id': rec.return_branch_id.id if rec.return_branch_id and rec.return_branch_id.id else None,
                    'return_gsm_no': rec.return_gsm_no if rec.return_gsm_no else None,
                    'state': rec.state if rec.state else None

                }
                return_list.append(dic)
            return Response(json.dumps({"data": return_list, 'message': 'Success', 'success': True},
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    ################################# CASH RECEIPT API ###############################################

    @http.route(['/api/create/cash_receipt'], auth="public", methods=['POST'], type='json',
                csrf=False)
    def create_cash_receipt(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            uid = env['sfk_rest.token'].check_token(data['token'])
            if uid:
                line_ids = []
                for prod in data['product']:
                    line_ids.append((0, 0, {
                        'customer': int(prod['customer']),
                        'amount': prod['amount'],
                    }))
                user = request.env['res.users'].sudo().search([('id', '=', uid)])
                cash = request.env['cash.receipt'].sudo().create({
                    'manual_no': data['manual_no'],
                    'cash_bank': user.cash_receipt_receivable_acc.id,
                    'branch': user.branch_id.id,
                    'narration': data['narration'],
                    'line_ids': line_ids,
                })
                if cash:
                    return {'status': 200, 'message': '  Cash RECEIPT created successfully',
                            'cash_id': cash.id}
                else:
                    return {'status': 202, 'message': 'Token authentication failed'}
        except KeyError as key_error:
            return {'status': 202, 'message': f"Missing required parameter: {str(key_error)}"}
        except Exception as error:
            _logger.error(error)
            return {'status': 400,
                    'message': 'An error occurred during sale Cash Receipt creation.'}

    ####################################  ALL CASH RECEIPT API ####################################################
    @http.route(['/api/get/all/cash_receipt'], auth="public", type='http', csrf=False)
    def get_all_cash_receipts(self, **kw):
        try:
            cash_list = []
            for rec in request.env['cash.receipt'].sudo().search([("state", '=', 'done')]):
                dic = {
                    'cash_bank': rec.cash_bank.name if rec.cash_bank.name else None,
                    'manual_no': rec.manual_no if rec.manual_no else None,
                    'branch': rec.branch_id.id if rec.branch and rec.branch_id.id else None,
                    'narration': rec.narration if rec.narration and rec.narration else None,
                    'line_ids': []
                }
                cash_list.append(dic)
                print("dic", dic)
                for cash in rec.line_ids:
                    line_dic = {
                        'customer': cash.customer.id if cash.customer.id else None,
                        'amount': cash.amount if cash.amount else None
                    }
                    dic['line_ids'].append(line_dic)
            print("cash_list", cash_list)
            return Response(json.dumps({"data": cash_list, 'message': 'Success', 'success': True},
                                       sort_keys=True, indent=4, cls=ObjectEncoder),
                            content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            return Response(json.dumps({'error': traceback.format_exc()}, indent=4),
                            content_type='application/json;charset=utf-8', status=400)
