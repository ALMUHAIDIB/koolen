# -*- coding: utf-8 -*-
##############################################################################
#
#    DevIntelle Solution(Odoo Expert)
#    Copyright (C) 2015 Devintelle Soluation (<http://devintelle.com/>)
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.translate import _
from odoo.exceptions import except_orm
from odoo import models, fields, api
from odoo.tools.misc import str2bool, xlwt
from xlsxwriter.workbook import Workbook
import base64
from io import BytesIO
from xlwt import easyxf
import csv


class inventory_wizard(models.TransientModel):
    _name = 'inventory.age.wizard'
    _description = 'Stock Ageing Report'

    period_length = fields.Integer('Period Length (days)', default=30)
    product_id = fields.Many2many('product.product', string='Product')
    # product_category_id = fields.Many2many('product.category', 'Product Category')
    product_category_ids = fields.Many2many(comodel_name="product.category", relation="product_category_rel",
                                            string="Product Category", )
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id)
    date_from = fields.Date('Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    # get_all_locations = fields.Boolean()
    get_all_categories = fields.Boolean()

    # location_ids = fields.Many2many('stock.location', string='Location')
    #
    # @api.onchange('get_all_locations')
    # def _onchange_get_all_locations(self):
    #     for rec in self:
    #         if rec.get_all_locations:
    #             location_list = []
    #             locations = self.env['stock.location'].search([('usage', '=', 'internal')])
    #             for location in locations:
    #                 location_list.append(location.id)
    #             rec.location_ids = location_list
    #         else:
    #             rec.location_ids = [(6, 0, [])]

    @api.onchange('get_all_categories')
    def _onchange_get_all_categories(self):
        for rec in self:
            if rec.get_all_categories:
                category_list = []
                categories = self.env['product.category'].search([])
                for category in categories:
                    category_list.append(category.id)
                rec.product_category_ids = category_list
                print(rec.product_category_ids)
            else:
                rec.product_category_ids = [(6, 0, [])]


    # @api.multi
    # def get_location_name(self, location_ids):
    #     location_pool = self.env['stock.location']
    #     name = ''
    #     for location in location_pool.browse(location_ids):
    #         if name:
    #             name = name + ',' + location.name
    #         else:
    #             name = location.name
    #     return name

    @api.model
    def get_lines(self, form):
        res = []
        product_ids = []
        stock_move_line_obj = self.env.get('stock.move.line')
        product_category_ids = form['product_category_ids']
        product_obj = self.env['product.product']
        if product_category_ids:
            products = product_obj.search([('categ_id', 'in', product_category_ids)])
            product_ids = products._ids
        if form.get('product_id'):
            wizard_product_id = form['product_id']
            product_ids = wizard_product_id

        for product in product_obj.browse(product_ids):
            # print('my product >> ', product)
            product_dict = {
                'pname': product.name,
                'pnumber': product.default_code,
                'cost': product.standard_price,
                'onhand_qty': product.qty_available,
            }
            date_from = form['date_from']
            # product_qty = product._product_available(False, False)
            # qty_list = product_qty.get(product.id)
            # product_dict.update({
            #     'onhand_qty': qty_list['qty_available'],
            # })
            # print('DATE FROM  >> ', date_from)
            total_in = 0
            total_out = 0
            domain_total = [('date', '<=', date_from),
                            ('product_id', '=', product.id), ]
            # ('location_id.usage', '=', 'supplier'),
            # ('location_dest_id.is_aging', '=', True),]
            # domain_out_total = [('date', '<=', date_from),
            #                     ('product_id', '=', product.id), ]
            # ('location_dest_id.usage', '=', 'customer'),
            # ('location_id.is_aging', '=', True)]
            for move in stock_move_line_obj.search(domain_total):
                if move.location_dest_id.is_aging:
                    total_in += move.qty_done
                elif move.location_id.is_aging:
                    total_out += move.qty_done
            # for move in stock_move_line_obj.search(domain_out_total):
            #     total_out += move.qty_done
            # print('total_in = ', total_in, ' total_out = ', total_out)
            total_in_o = total_in
            total_out_o = total_out
            # print('total_in_o = ', total_in_o, ' total_out_o = ', total_out_o)

            diff = total_in_o - total_out_o
            # print('DIFF >> ', diff)
            for data in range(13)[::-1]:
                # print('diff >> ', diff)
                total_qty_in = 0
                if form.get(str(data)):
                    start_date = form.get(str(data)).get('start')
                    stop_date = form.get(str(data)).get('stop')
                    # print('start date', start_date)
                    # print('stop date', stop_date)

                    domain_in = [('date', '<=', stop_date),
                                 ('date', '>=', start_date),
                                 ('location_dest_id.is_aging', '=', True),
                                 # ('location_id.usage', '=', 'supplier'),
                                 ('product_id', '=', product.id)]
                    if start_date:
                        # print('in start date')
                        start_stock_move = stock_move_line_obj.search(domain_in, order='date desc')
                        qty_done_move = start_stock_move.mapped('qty_done')
                        # for move in start_stock_move:
                        #     total_qty_in += move.qty_done
                        total_qty_in = sum(qty_done_move)
                        print('total_qty_in sum >> ', total_qty_in)
                        # print('total_qty_in >> ', total_qty_in)
                        if total_qty_in > 0:
                            # print('in total_qty_in')
                            if total_qty_in <= diff:
                                # print('in <= diff')
                                product_dict[str(data)] = total_qty_in
                                diff = diff - total_qty_in
                            elif total_qty_in > diff:
                                # print('in > diff')
                                product_dict[str(data)] = diff
                                diff = 0
                        else:
                            product_dict[str(data)] = 0
                    else:
                        start_stock_move = stock_move_line_obj.search([('date', '<=', stop_date),
                                                                       ('product_id', '=', product.id),
                                                                       # ('location_id.usage', '=', 'supplier'),
                                                                       ('location_dest_id.is_aging', '=', True)])
                        move_qty_done = start_stock_move.mapped('qty_done')
                        print('move_qty_done >> ', move_qty_done)
                        # for move in start_stock_move:
                        #     total_qty_in += move.qty_done
                        total_qty_in = sum(move_qty_done)
                        print('total_qty_in >> ', total_qty_in)

                        if total_qty_in > 0:
                            if total_qty_in <= diff:
                                product_dict[str(data)] = total_qty_in
                            elif total_qty_in > diff:
                                product_dict[str(data)] = diff
                        else:
                            product_dict[str(data)] = 0
            res.append(product_dict)
        return res

    def _print_exp_report(self, data):
        res = {}
        period_length = data['form']['period_length']
        if period_length <= 0:
            raise except_orm(_('User Error!'), _('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise except_orm(_('User Error!'), _('You must set a start date.'))

        start = datetime.strptime(str(data['form']['date_from']), "%Y-%m-%d")
        # print('start >>>>> MAIN ', start)
        for i in range(13)[::-1]:
            stop = start - relativedelta(days=period_length)
            # print('stop >>> ', stop)
            res[str(i)] = {
                # str((13 - (i + 1)) * period_length) + '-' +
                'name': (i != 0 and (str((13 - i) * period_length)) or (
                        '+' + str(12 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
            # print('start >>> ', start)
            # print('res[str(i)] i >> ', i, ' >> ', res[str(i)])
        # print(res)
        data['form'].update(res)
        import base64
        filename = 'Inventory Aging Report.xls'
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Inventory Aging Report')

        header_style = easyxf(
            'font:height 200;pattern: pattern solid, fore_color black;'
            ' align: horiz center;font: color white;'
            ' font:bold True;' "borders: top thin,left thin,right thin,bottom thin")
        colomn_style = easyxf(' align: horiz center;')

        first_col = worksheet.col(0)
        second_col = worksheet.col(1)
        third_col = worksheet.col(2)
        four_col = worksheet.col(3)
        five_col = worksheet.col(4)
        six_col = worksheet.col(5)
        seven_col = worksheet.col(6)
        eight_col = worksheet.col(7)
        nine_col = worksheet.col(8)
        ten_col = worksheet.col(9)
        eleven_col = worksheet.col(10)
        twelve_col = worksheet.col(11)
        thirteen_col = worksheet.col(12)
        fourteen_col = worksheet.col(13)
        fifteen_col = worksheet.col(14)
        sixteen_col = worksheet.col(15)
        seventeen_col = worksheet.col(16)
        eighteen_col = worksheet.col(16)

        first_col.width = 130 * 30
        second_col.width = 150 * 30
        third_col.width = 180 * 30
        four_col.width = 130 * 30
        five_col.width = 150 * 30
        six_col.width = 130 * 30
        seven_col.width = 130 * 30
        eight_col.width = 130 * 30
        nine_col.width = 130 * 30
        ten_col.width = 130 * 30
        eleven_col.width = 130 * 30
        twelve_col.width = 130 * 30
        thirteen_col.width = 130 * 30
        fourteen_col.width = 130 * 30
        fifteen_col.width = 130 * 30
        sixteen_col.width = 130 * 30
        seventeen_col.width = 130 * 30
        eighteen_col.width = 130 * 30

        worksheet.write_merge(0, 1, 0, 3, 'Inventory Aging Report', easyxf(
            'font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin"))
        date_from = data['form']['date_from'] or ' '
        if date_from:
            date = datetime.strptime(str(date_from).split(' ')[0], '%Y-%m-%d')
            date_from = date.strftime('%d-%m-%Y')
            worksheet.write(2, 4, 'Start Date' + '-' + str(date_from))
        worksheet.write(5, 0, 'Product', header_style)
        worksheet.write(5, 1, 'Product Number', header_style)
        worksheet.write(5, 2, 'Unit Cost', header_style)
        worksheet.write(5, 3, 'Quantity', header_style)
        worksheet.write(5, 4, 'Total cost', header_style)
        worksheet.write(5, 5, data['form']['12']['name'], header_style)
        worksheet.write(5, 6, data['form']['11']['name'], header_style)
        worksheet.write(5, 7, data['form']['10']['name'], header_style)
        worksheet.write(5, 8, data['form']['9']['name'], header_style)
        worksheet.write(5, 9, data['form']['8']['name'], header_style)
        worksheet.write(5, 10, data['form']['7']['name'], header_style)
        worksheet.write(5, 11, data['form']['6']['name'], header_style)
        worksheet.write(5, 12, data['form']['5']['name'], header_style)
        worksheet.write(5, 13, data['form']['4']['name'], header_style)
        worksheet.write(5, 14, data['form']['3']['name'], header_style)
        worksheet.write(5, 15, data['form']['2']['name'], header_style)
        worksheet.write(5, 16, data['form']['1']['name'], header_style)
        worksheet.write(5, 17, data['form']['0']['name'], header_style)
        worksheet.write(5, 18, 'Total Quantity', header_style)

        line = self.get_lines(data['form'])
        # print('Line >> = ', line)
        if line:
            i = 6
            p = 0
            for product in line:
                total = 0
                if product.get('onhand_qty', 0) and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 0, product['pname'], colomn_style)

                if product.get('onhand_qty', 0) and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1

                    worksheet.write(i, 1, product['pnumber'], colomn_style)

                if product.get('onhand_qty', 0) and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1

                    worksheet.write(i, 2, product['cost'], colomn_style)

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1

                    worksheet.write(i, 5, product['12'], colomn_style)
                    total += product['12']

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 6, product['11'], colomn_style)
                    total += product['11']

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 7, product['10'], colomn_style)
                    total += product['10']

                if product.get('onhand_qty', 0) != 0 \
                        and product.get('onhand_qty', 0) > 0 \
                        and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 8, product['9'], colomn_style)

                    total += product['9']

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 9, product['8'], colomn_style)

                    total += product['8']

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 10, product['7'], colomn_style)
                    total += product['7']

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 11, product['6'], colomn_style)
                    total += product['6']

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 12, product['5'], colomn_style)
                    total += product['5']

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 13, product['4'], colomn_style)
                    total += product['4']

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 14, product['3'], colomn_style)
                    total += product['3']

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 15, product['2'], colomn_style)
                    total += product['2']

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 16, product['1'], colomn_style)
                    total += product['1']

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 17, product['0'], colomn_style)
                    total += product['0']

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 3, product['onhand_qty'], colomn_style)  # total

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 4, product['onhand_qty'] * product['cost'], colomn_style)

                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (
                        product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product[
                    '4'] > 0 or product['5'] > 0 or product['6'] > 0 or product['7'] > 0 or product['8'] > 0 or product[
                            '9'] > 0 or product['10'] > 0 or product['11'] > 0 or product['12'] > 0):
                    p += 1
                    worksheet.write(i, 18, total, colomn_style)

                if p > 0:
                    i += 1
                p = 0

        fp = BytesIO()
        workbook.save(fp)
        export_id = self.env['inventory.age.dow'].create(
            {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'inventory.age.dow',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
        }

    def inventory_age_history_excel(self):
        data = {'ids': self._context.get('active_ids', []), 'model': self._context.get('active_model', 'ir.ui.menu')}
        for record in self:
            data['form'] = self.read(
                ['period_length', 'product_id', 'product_category_ids', 'company_id', 'date_from'])[0]
        return self._print_exp_report(data)


class inventory_age_dow(models.TransientModel):
    _name = "inventory.age.dow"

    excel_file = fields.Binary('Excel Report ')
    file_name = fields.Char('Excel File', size=64)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
