# -*- coding: utf-8 -*-
##############################################################################
#
#    DevIntelle Solution(Odoo Expert)
#    Copyright (C) 2015 Devintelle Soluation (<http://devintelle.com/>)
#
##############################################################################
from datetime import datetime, timedelta
from odoo import api, models
import odoo.addons.decimal_precision as dp
from num2words import num2words


class stock_ageing_report(models.AbstractModel):
    _name = 'report.dev_inventory_ageing_report_old.report_stockageing'

    @api.model
    def get_lines(self, form):
        print('in get_lines PDF')
        res = []
        product_ids = []
        quant_obj = self.env.get('stock.quant')
        product_category_id = form['product_category_id'][0]
        product_obj = self.env.get('product.product')
        if product_category_id:
            products = product_obj.search([('categ_id', 'child_of', product_category_id)])
            product_ids = products._ids

        if form.get('product_id'):
            wizard_product_id = form['product_id']
            product_ids = wizard_product_id

        for product in product_obj.browse(product_ids):
            product_dict = {
                'pname': product.name
            }
            location_id = form['location_ids']

            date_from = form['date_from']
            # warehouse = form['warehouse_id'][0]
            ctx = self._context.copy()
            ctx.update({
                'location': location_id,
                'from_date': date_from,
                'to_date': date_from
            })
            product_qty = product._product_available(False, False)
            qty_list = product_qty.get(product.id)
            product_dict.update({
                'onhand_qty': qty_list['qty_available'],
            })
            for data in range(0, 7):
                total_qty = 0
                if form.get(str(data)):
                    start_date = form.get(str(data)).get('start')
                    stop_date = form.get(str(data)).get('stop')
                    if not start_date:
                        domain = [('create_date', '<=', stop_date), ('location_id', 'in', location_id),
                                  ('product_id', '=', product.id)]
                    else:
                        domain = [('create_date', '<=', stop_date), ('create_date', '>=', start_date),
                                  ('location_id', 'in', location_id), ('product_id', '=', product.id)]

                    for quant in quant_obj.search(domain):
                        total_qty += quant.quantity
                    product_dict[str(data)] = total_qty
            res.append(product_dict)
            print('res >>> ', res)
        return res

    # @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['inventory.age.wizard'].browse(docids)

        location_pool = self.env['stock.location']
        lo_name = ''
        location_ids = data['form']['location_ids']
        for location in location_pool.browse(location_ids):
            if lo_name:
                lo_name = lo_name + ',' + location.name
            else:
                lo_name = location.name

        lo_name = str(lo_name)

        return {
            'doc_ids': docs.ids,
            'doc_model': 'inventory.age.wizard',
            'docs': docs,
            'data': data,
            'get_lines': self.get_lines(data['form']),
            'get_location_name': lo_name,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
