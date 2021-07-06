# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning as UserError
import openerp.addons.decimal_precision as dp
from odoo.tools import float_round, float_is_zero


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    invoice_ids = fields.One2many(
        'account.move',
        'stock_landed_cost_id',
        string='Invoices',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Invoices which contain items to be used as landed costs',
        copy=False,
    )
    move_ids = fields.Many2many(
        'stock.move',
        'stock_landed_move_rel',
        'stock_landed_cost_id',
        'move_id',
        string='Production Moves',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('production_id', '!=', False), ('state', 'in', ('done',))],
        help='Production Moves to be increased in costs',
        copy=False,
    )

    @api.onchange('invoice_ids')
    def onchange_invoice_ids(self):
        for lc_brw in self:
            lc_brw.update({'cost_lines': [(6, False, {})]})
            cost_lines = []
            for inv_brw in lc_brw.invoice_ids:
                company_currency = inv_brw.company_id.currency_id  #inv_brw is account.invoice
                diff_currency = inv_brw.currency_id != company_currency
                if diff_currency:
                    currency = inv_brw.currency_id.with_context(
                        date=inv_brw.date_invoice)
                for ail_brw in inv_brw.invoice_line_ids:
                    if not ail_brw.product_id:
                        continue
                    # if not ail_brw.product_id.landed_cost_ok:
                    #     print("inside inside9")
                    #     continue
                    if diff_currency:
                        price_subtotal = currency.compute(
                            ail_brw.price_subtotal, company_currency)
                    else:
                        price_subtotal = ail_brw.price_subtotal
                    cost_lines.append((0, False, {
                        'name': ail_brw.name,
                        'account_id': ail_brw.account_id and
                        ail_brw.account_id.id,
                        'product_id': ail_brw.product_id and
                        ail_brw.product_id.id,
                        'price_unit': price_subtotal,
                        'split_method': ail_brw.product_id.split_method_landed_cost,
                    }))
            if cost_lines:
                lc_brw.update({'cost_lines': cost_lines})

    # @api.multi
    def get_costs_from_invoices(self):
        """Update Costs Lines with Invoice Lines in the Invoices related to
        Document
        """
        slcl_obj = self.env['stock.landed.cost.lines']
        for lc_brw in self:
            for cl_brw in lc_brw.cost_lines:
                cl_brw.unlink()
            for inv_brw in lc_brw.invoice_ids:
                company_currency = inv_brw.company_id.currency_id
                diff_currency = inv_brw.currency_id != company_currency
                if diff_currency:
                    currency = inv_brw.currency_id.with_context(
                        date=inv_brw.date_invoice)
                for ail_brw in inv_brw.invoice_line_ids:
                    if not ail_brw.product_id:
                        continue
                    if not ail_brw.product_id.landed_cost_ok:
                        continue
                    if diff_currency:
                        price_subtotal = currency.compute(
                            ail_brw.price_subtotal, company_currency)
                    else:
                        price_subtotal = ail_brw.price_subtotal
                    vals = {
                        'cost_id': lc_brw.id,
                        'name': ail_brw.name,
                        'account_id': ail_brw.account_id and
                        ail_brw.account_id.id,
                        'product_id': ail_brw.product_id and
                        ail_brw.product_id.id,
                        'price_unit': price_subtotal,
                        'split_method': 'by_quantity',
                    }
                    slcl_obj.create(vals)
        return True

    # @api.multi
    # def get_valuation_lines(self, picking_ids=None):
    #     """It returns product valuations based on picking's moves
    #     """
    #
    #     picking_obj = self.env['stock.picking']
    #     lines = []
    #     if not picking_ids and not self.move_ids:
    #         return lines
    #
    #     # NOTE: Now it is valid for all costing methods available
    #     move_ids = [  #cntains lines from stock.move
    #         move_id
    #         for picking in picking_obj.browse(picking_ids)
    #         for move_id in picking.move_lines
    #         if move_id.product_id.valuation == 'real_time'
    #     ]
    #
    #
    #     move_ids += [
    #         move_id
    #         for move_id in self.move_ids
    #         if move_id.product_id.valuation == 'real_time'
    #     ]
    #
    #
    #     for move in move_ids:
    #         total_cost = 0.0
    #         total_qty = move.product_qty
    #         weight = move.product_id and \
    #             move.product_id.weight * move.product_qty
    #         volume = move.product_id and \
    #             move.product_id.volume * move.product_qty
    #
    #
    #         # for quant in move.move_line_ids:
    #         # for quant in move.move_line_ids:
    #         for quant in self.mapped('picking_ids').mapped('move_lines'):
    #             total_cost += quant.value
    #         vals = dict(
    #             product_id=move.product_id.id,
    #             account_journal_id=self.account_journal_id.id,
    #             move_id=move.id,
    #             quantity=move.product_uom_qty,
    #             former_cost=total_cost * total_qty,
    #             weight=weight,
    #             volume=volume)
    #         lines.append(vals)
    #     if not lines:
    #         raise except_orm(
    #             _('Error!'),
    #             _('The selected picking does not contain any move that would '
    #               'be impacted by landed costs. Landed costs are only possible'
    #               ' for products configured in real time valuation. Please '
    #               'make sure it is the case, or you selected the correct '
    #               'picking.'))
    #     return lines

    def get_valuation_lines(self,picking_ids=None):
        lines = []

        for move in self.mapped('picking_ids').mapped('move_lines'):
            # it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
            # if move.product_id.valuation != 'real_time' or move.product_id.cost_method != 'fifo':
            #     continue
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': move.value,
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty
            }
            lines.append(vals)

        if not lines and self.mapped('picking_ids'):
            raise UserError(_("You cannot apply landed costs on the chosen transfer(s). Landed costs can only be applied for products with automated inventory valuation and FIFO costing method."))
        return lines

    def _create_deviation_account_move_line(
            self, move_id, gain_account_id, loss_account_id,
            valuation_account_id, diff, product_brw):
        """It generates journal items to track landed costs
        """
        ctx = dict(self._context)
        aml_obj = self.pool.get('account.move.line')

        base_line = {
            'move_id': move_id,
            'product_id': product_brw.id,
        }

        name = u'{name}: {memo} - AVG'

        if diff < 0:
            name = name.format(
                name=product_brw.name, memo=_('Losses on Inventory Deviation'))
            debit_line = dict(
                base_line,
                name=name,
                account_id=loss_account_id,
                debit=-diff,)
            credit_line = dict(
                base_line,
                name=name,
                account_id=valuation_account_id,
                credit=-diff,)
        else:
            name = name.format(
                name=product_brw.name, memo=_('Gains on Inventory Deviation'))
            debit_line = dict(
                base_line,
                name=name,
                account_id=valuation_account_id,
                credit=diff,)
            credit_line = dict(
                base_line,
                name=name,
                account_id=gain_account_id,
                debit=diff,)
        aml_obj.create(
            self._cr, self._uid, debit_line, context=ctx, check=False)
        aml_obj.create(
            self._cr, self._uid, credit_line, context=ctx, check=False)
        return True

    def _get_deviation_accounts(self, product_id, acc_prod):
        """This method takes the variation in value for average and books it as
        Inventory Valuation Deviation
        """
        accounts = acc_prod[product_id]
        valuation_account_id = accounts['property_stock_valuation_account_id']

        company_brw = self.env.user.company_id
        gain_account_id = company_brw.gain_inventory_deviation_account_id.id
        loss_account_id = company_brw.loss_inventory_deviation_account_id.id

        if not gain_account_id or not loss_account_id:
            raise except_orm(
                _('Error!'),
                _('Please configure Gain & Loss Inventory Valuation in your'
                  ' Company'))

        return valuation_account_id, gain_account_id, loss_account_id

    def _create_deviation_accounting_entries(
            self, move_id, product_id, diff, acc_prod=None):
        """This method takes the variation in value for average and books it as
        Inventory Valuation Deviation
        """
        # TODO: improve code to profit from acc_prod dictionary
        # and reduce overhead with this repetitive query
        valuation_account_id, gain_account_id, loss_account_id = \
            self._get_deviation_accounts(product_id, acc_prod)

        product_brw = self.env['product.product'].browse(product_id)

        return self._create_deviation_account_move_line(
            move_id, gain_account_id, loss_account_id,
            valuation_account_id, diff, product_brw)

    def _create_standard_deviation_entry_lines(
            self, line, move_id, valuation_account_id, gain_account_id,
            loss_account_id):
        """It generates journal items to track landed costs, using arbitrary
        accounts for valuation, gain and loss
        """
        aml_obj = self.env['account.move.line']
        base_line = {
            'name': line.name,
            'move_id': move_id,
            'product_id': line.product_id.id,
            'quantity': line.quantity,
        }
        debit_line = dict(base_line)
        credit_line = dict(base_line)
        diff = line.additional_landed_cost
        if diff > 0:
            debit_line['account_id'] = loss_account_id
            debit_line['debit'] = diff
            credit_line['account_id'] = line.cost_line_id.account_id.id
            credit_line['credit'] = diff
        else:
            # negative cost, reverse the entry
            debit_line['account_id'] = line.cost_line_id.account_id.id
            debit_line['debit'] = -diff
            credit_line['account_id'] = gain_account_id
            credit_line['credit'] = -diff
        aml_obj.create(debit_line, check=False)
        aml_obj.create(credit_line, check=False)
        return True

    # @api.multi
    def _create_standard_deviation_entries(self, line, move_id, acc_prod=None):
        """Create standard deviation journal items based on predefined product
        account valuation, gain and loss company's accounts
        """
        if float_is_zero(
                line.additional_landed_cost,
                self.pool.get('decimal.precision').precision_get(
                    self._cr, self._uid, 'Account')):
            return False

        valuation_account_id, gain_account_id, loss_account_id = \
            self._get_deviation_accounts(line.product_id.id, acc_prod)

        return self._create_standard_deviation_entry_lines(
            line, move_id, valuation_account_id, gain_account_id,
            loss_account_id)

    # @api.multi
    def _create_cogs_accounting_entries(
            self, product_id, move_id, diff, acc_prod=None):
        """This method takes the amount of cost that needs to be booked as
        inventory value and later takes the amount of COGS that is needed to
        book if any sale was done because of this landing cost been applied
        """
        product_brw = self.env['product.product'].browse(product_id)
        accounts = acc_prod[product_id]
        debit_account_id = accounts['property_stock_valuation_account_id']
        # NOTE: BEWARE of accounts when account_anglo_saxon applies
        # TODO: Do we have to set another account for cogs_account_id?
        cogs_account_id = \
            product_brw.property_account_expense and \
            product_brw.property_account_expense.id or \
            product_brw.categ_id.property_account_expense_categ and \
            product_brw.categ_id.property_account_expense_categ.id

        if not cogs_account_id:
            raise except_orm(
                _('Error!'),
                _('Please configure Stock Expense Account for product: %s.') %
                (product_brw.name))

        return self._create_cogs_account_move_line(
            product_brw, move_id, debit_account_id, cogs_account_id, diff)

    # @api.multi
    def _create_cogs_account_move_line(
            self, product_brw, move_id, debit_account_id, cogs_account_id,
            diff):
        """Create journal items for COGS for those products sold
        before landed costs were applied
        """

        ctx = dict(self._context)
        aml_obj = self.pool.get('account.move.line')
        base_line = {
            'move_id': move_id,
            'product_id': product_brw.id,
        }
        # Create COGS account move lines for products that were sold prior to
        # applying landing costs
        # NOTE: knowing how many products that were affected, COGS was to
        # change, by this landed cost is not really necessary

        name = u'{name}: COGS - {memo}'
        if diff > 0:
            name = name.format(
                name=product_brw.name, memo='[+]')
            debit_line = dict(
                base_line,
                name=name,
                account_id=cogs_account_id,
                debit=diff,)
            credit_line = dict(
                base_line,
                name=name,
                account_id=debit_account_id,
                credit=diff,)
        else:
            # /!\ NOTE: be careful when making reversions on landed costs or
            # negative landed costs
            name = name.format(
                name=product_brw.name, memo='[-]')
            debit_line = dict(
                base_line,
                name=name,
                account_id=debit_account_id,
                debit=-diff,)
            credit_line = dict(
                base_line,
                name=name,
                account_id=cogs_account_id,
                credit=-diff,)

        aml_obj.create(
            self._cr, self._uid, debit_line, context=ctx, check=False)
        aml_obj.create(
            self._cr, self._uid, credit_line, context=ctx, check=False)
        return True

    def compute_average_cost(self, dct=None):
        """This method updates standard_price field in products with costing
        method equal to average
        """
        dct = dict(dct or {})
        scp_obj = self.env['stock.card.product']
        if not dct:
            return True
        for product_id in dct.keys():
            field2write = dct[product_id]
            scp_obj.write_standard_price(product_id, field2write)
        return True

    # @api.multi
    # # @do_profile(follow=[])
    # def button_validate(self):
    #     self.ensure_one()
    #     precision_obj = self.pool.get('decimal.precision').precision_get(
    #          self, 'Account') # ' self._cr, self._uid
    #     quant_obj = self.env['stock.quant']
    #     template_obj = self.pool.get('product.template')
    #     scp_obj = self.env['stock.card.product']
    #     get_average = scp_obj.get_average
    #     stock_card_move_get = scp_obj._stock_card_move_get
    #     ctx = dict(self._context)
    #
    #     for cost in self:
    #         if cost.state != 'draft':
    #             raise UserError(
    #                 _('Only draft landed costs can be validated'))
    #         if not cost.valuation_adjustment_lines or \
    #                 not self._check_sum():#cost
    #             raise UserError(
    #                 _('You cannot validate a landed cost which has no valid '
    #                   'valuation adjustments lines. Did you click on '
    #                   'Compute?'))
    #
    #         move_id = self._model._create_account_move(
    #             self._cr, self._uid, cost, context=ctx)
    #         prod_dict = {}
    #         init_avg = {}
    #         first_lines = {}
    #         first_card = {}
    #         last_lines = {}
    #         prod_qty = {}
    #         acc_prod = {}
    #         quant_dict = {}
    #         for line in cost.valuation_adjustment_lines:
    #             if not line.move_id:
    #                 continue
    #             product_id = line.product_id
    #
    #             if product_id.id not in acc_prod:
    #                 acc_prod[product_id.id] = \
    #                     template_obj.get_product_accounts(
    #                     self._cr, self._uid, product_id.product_tmpl_id.id,
    #                     context=ctx)
    #
    #             if product_id.cost_method == 'standard':
    #                 self._create_standard_deviation_entries(
    #                     line, move_id, acc_prod)
    #                 continue
    #
    #             if product_id.cost_method == 'average':
    #                 if product_id.id not in prod_dict:
    #                     first_card = stock_card_move_get(product_id.id)
    #                     prod_dict[product_id.id] = get_average(first_card)
    #                     first_lines[product_id.id] = first_card['res']
    #                     init_avg[product_id.id] = product_id.standard_price
    #                     prod_qty[product_id.id] = first_card['product_qty']
    #
    #             per_unit = line.final_cost / line.quantity
    #             diff = per_unit - line.former_cost_per_unit
    #             quants = [quant for quant in line.move_id.quant_ids]
    #             for quant in quants:
    #                 if quant.id not in quant_dict:
    #                     quant_dict[quant.id] = quant.cost + diff
    #                 else:
    #                     quant_dict[quant.id] += diff
    #
    #             qty_out = 0
    #             for quant in line.move_id.quant_ids:
    #                 if quant.location_id.usage != 'internal':
    #                     qty_out += quant.qty
    #
    #             if product_id.cost_method == 'average':
    #                 # /!\ NOTE: Inventory valuation
    #                 self._create_landed_accounting_entries(
    #                     line, move_id, 0.0, acc_prod)
    #
    #             if product_id.cost_method == 'real':
    #                 self._create_landed_accounting_entries(
    #                     line, move_id, qty_out, acc_prod)
    #
    #         for key, value in quant_dict.items():
    #             quant_obj.sudo().browse(key).write(
    #                 {'cost': value})
    #
    #         # /!\ NOTE: This new update is taken out of for loop to improve
    #         # performance
    #         for prod_id in prod_dict:
    #             last_card = stock_card_move_get(prod_id)
    #             prod_dict[prod_id] = get_average(last_card)
    #             last_lines[prod_id] = last_card['res']
    #
    #         # /!\ NOTE: COGS computation
    #         # NOTE: After adding value to product with landing cost products
    #         # with costing method `average` need to be check in order to
    #         # find out the change in COGS in case of sales were performed prior
    #         # to landing costs
    #         to_cogs = {}
    #         for prod_id in prod_dict:
    #             to_cogs[prod_id] = zip(
    #                 first_lines[prod_id], last_lines[prod_id])
    #         for prod_id in to_cogs:
    #             fst_avg = 0.0
    #             lst_avg = 0.0
    #             ini_avg = init_avg[prod_id]
    #             diff = 0.0
    #             for tpl in to_cogs[prod_id]:
    #                 first_line = tpl[0]
    #                 last_line = tpl[1]
    #                 fst_avg = first_line['average']
    #                 lst_avg = last_line['average']
    #                 if first_line['qty'] >= 0:
    #                     # /!\ TODO: This is not true for devolutions
    #                     continue
    #
    #                 # NOTE: Rounding problems could arise here, this needs to
    #                 # be checked
    #                 diff += (lst_avg - fst_avg) * abs(first_line['qty'])
    #             if not float_is_zero(diff, precision_obj):
    #                 self._create_cogs_accounting_entries(
    #                     prod_id, move_id, diff, acc_prod)
    #
    #             # TODO: Compute deviation
    #             diff = 0.0
    #             if prod_qty[prod_id] and fst_avg != ini_avg and \
    #                     lst_avg != ini_avg:
    #                 diff = (fst_avg - ini_avg) * prod_qty[prod_id]
    #                 if not float_is_zero(diff, precision_obj):
    #                     self._create_deviation_accounting_entries(
    #                         move_id, prod_id, diff, acc_prod)
    #
    #         # TODO: Write latest value for average
    #         cost.compute_average_cost(prod_dict)
    #
    #         cost.write(
    #             {'state': 'done', 'account_move_id': move_id})
    #
    #         # Post the account move if the journal's auto post true
    #         move_obj = self.env['account.move'].browse(move_id)
    #         if move_obj.journal_id.entry_posted:
    #             move_obj.post()
    #             move_obj.validate()
    #
    #     return True

    # @api.multi
    def button_validate(self):
        if any(cost.state != 'draft' for cost in self):
            raise UserError(_('Only draft landed costs can be validated'))
        if any(not cost.valuation_adjustment_lines for cost in self):
            raise UserError(_('No valuation adjustments lines. You should maybe recompute the landed costs.'))
        if not self._check_sum():
            raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

        for cost in self:
            move = self.env['account.move']
            move_vals = {
                'journal_id': cost.account_journal_id.id,
                'date': cost.date,
                'ref': cost.name,
                'line_ids': [],
            }
            prod_id_to_gen_stockcard=None
            for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                # Prorate the value at what's still in stock
                cost_to_add = (line.move_id.remaining_qty / line.move_id.product_qty) * line.additional_landed_cost


                new_landed_cost_value = line.move_id.landed_cost_value + line.additional_landed_cost


                #added by omara, 19 JUne 2019

                # get last average value after last added landed cost to this product
                last_average = self.env['product.product.withlandedcost'].sudo().search([
                    ('product_id', '=', line.product_id.id)
                ])

                #calculate the qunatity of product, from avaialbe onhand qnt, in selected picking_ids
                product_onhand_qnts_for_selected_pickings=0
                for picking in self.picking_ids:
                    #get on hand quantity from stock.quant for that product id, location id
                    stock_quant_obj = self.env['stock.quant'].search([
                        ('product_id', '=', line.product_id.id), ('location_id', '=', picking.location_dest_id.id)
                    ])
                    product_onhand_qnts_for_selected_pickings+=stock_quant_obj.quantity if stock_quant_obj else 0

                # calculate new average to wirte in ir_property for that product
                new_avaerage = ((
                                    last_average.price_unit if last_average else 0) + line.move_id.value + line.additional_landed_cost) / product_onhand_qnts_for_selected_pickings

                print("new_avaerage",new_avaerage)
                print("line.move_id.value",line.move_id.value)
                print("line.additional_landed_cost",line.additional_landed_cost)
                print("product_onhand_qnts_for_selected_pickings",product_onhand_qnts_for_selected_pickings)
                #added by omara, 19 JUne 2019


                line.move_id.write({
                    'landed_cost_value': new_landed_cost_value,
                    'value': line.move_id.value + line.additional_landed_cost,
                    'remaining_value': line.move_id.remaining_value + cost_to_add,
                    'price_unit': (line.move_id.value + line.additional_landed_cost) / line.move_id.product_qty,
                })

                #added by omara at 31 may 2019, update standard price in product.product
                # add landed cost to it


                #"""
                product_to_update =  self.env['ir.property'].search([
                                ('res_id', '=', 'product.product,'+str(line.product_id.id))
                            ], limit=1)

                # product_to_update.write({'value_float':(line.additional_landed_cost/line.quantity)+ line.product_id.standard_price}); #/line.quantity
                product_to_update.write({'value_float':new_avaerage})


                #save the price_unit of the product in a table, to fetsh when calculation it again, when adding another landed cost
                #price_unit=line.move_id.price_unit, product_id=line.product_id.id
                if last_average:
                    self.env['product.product.withlandedcost'].sudo().write({'price_unit':new_avaerage,'product_id':line.product_id.id})
                else:
                    self.env['product.product.withlandedcost'].sudo().create({'price_unit':new_avaerage,'product_id':line.product_id.id})

               #"""

                #added by omara at 31 may 2019

                #added by omara, 24 Jun
                prod_id_to_gen_stockcard=line.product_id.id



                # `remaining_qty` is negative if the move is out and delivered proudcts that were not
                # in stock.
                qty_out = 0
                if line.move_id._is_in():
                    qty_out = line.move_id.product_qty - line.move_id.remaining_qty
                elif line.move_id._is_out():
                    qty_out = line.move_id.product_qty
                move_vals['line_ids'] += line._create_accounting_entries(move, qty_out)



            # added by omara at 23 Jun 2019, generating stock card    line.product_id.id
            """
            add unlink in it fot stock_card_product table
            this is the field  has the ids to ulink stock.card.product .stock_card_move_ids

            then call funcion:create_stock_card_lines  passig product id it's aproduct.product 
            """
            # self.env['stock.card.move'].search([('stock_card_product_id','=',line.move_id.stock_card_product_id.id),('move_id','=',line.move_id.id)]).unlink()
            self.env['stock.card.product'].create_stock_card_lines(prod_id_to_gen_stockcard)

            # added by omara at 23 Jun 2019



            move = move.create(move_vals)
            cost.write({'state': 'done', 'account_move_id': move.id})
            move.post()

        return True

    # @api.v7
    def compute_landed_cost_v7(self, cr, uid, ids, context=None):
        """It compute valuation lines for landed costs based on
        splitting method used
        """

        line_obj = self.pool.get('stock.valuation.adjustment.lines')
        unlink_ids = line_obj.search(self.env['stock.valuation.adjustment.lines'],
            [('cost_id', 'in', ids)]).unlink()


        digits = dp.get_precision('Product Price')(cr)
        towrite_dict = {}
        for cost in self.browse(ids): #cr, uid, cost is stovk.landed.cost
            if not cost.picking_ids and not cost.move_ids:
                continue
            picking_ids = [p.id for p in cost.picking_ids]
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
            vals = self.get_valuation_lines(
                 picking_ids )#cr, uid, [cost.id], picking_ids
            for v in vals:
                for line in cost.cost_lines:
                    v.update({'cost_id': cost.id, 'cost_line_id': line.id})
                    line_obj.create(self.env['stock.valuation.adjustment.lines'], v) #cr, uid, v
                total_qty += v.get('quantity', 0.0)
                total_cost += v.get('former_cost', 0.0)
                total_weight += v.get('weight', 0.0)
                total_volume += v.get('volume', 0.0)
                total_line += 1

            vals_adjus=line_obj.search(self.env['stock.valuation.adjustment.lines'],[])
            for line in cost.cost_lines:
                value_split = 0.0
                for valuation in cost.valuation_adjustment_lines:#todo call the model again stock valu adjust lines
                    value = 0.0
                    if valuation.cost_line_id and \
                            valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and \
                                total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        else:
                            value = (line.price_unit / total_line)

                        if digits:
                            value = float_round(
                                value, precision_digits=digits[1],
                                rounding_method='UP')
                            fnc = min if line.price_unit > 0 else max
                            value = fnc(value, line.price_unit - value_split)
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
        if towrite_dict:
            AdjustementLines = self.env['stock.valuation.adjustment.lines']
            for key, value in towrite_dict.items():
                AdjustementLines.browse(key).write({'additional_landed_cost': value})

        return True

    def compute_landed_cost(self):  # pylint: disable=E0102
        return self.compute_landed_cost_v7(self._cr, self._uid, self.ids)  #_model #

    def _create_landed_account_move_line(
            self, line, move_id, credit_account_id, debit_account_id, qty_out,
            already_out_account_id):
        """Generate the account.move.line values to track the landed cost.
        Afterwards, for the goods that are already out of stock, we should
        create the out moves
        """
        ctx = dict(self._context)
        cr, uid = self._cr, self._uid
        aml_obj = self.pool.get('account.move.line')
        base_line = {
            'name': line.name,
            'move_id': move_id,
            'product_id': line.product_id.id,
            'quantity': line.quantity,
        }
        debit_line = dict(base_line, account_id=debit_account_id)
        credit_line = dict(base_line, account_id=credit_account_id)
        diff = line.additional_landed_cost
        if diff > 0:
            debit_line['debit'] = diff
            credit_line['credit'] = diff
        elif diff < 0:
            # negative cost, reverse the entry
            debit_line['credit'] = -diff
            credit_line['debit'] = -diff
        if diff != 0:
            aml_obj.create(cr, uid, debit_line, context=ctx, check=False)
            aml_obj.create(cr, uid, credit_line, context=ctx, check=False)

        # Create account move lines for quants already out of stock
        if qty_out > 0:
            debit_line = dict(
                debit_line,
                name=(line.name + ": " + str(qty_out) + _(' already out')),
                quantity=qty_out,
                account_id=already_out_account_id)
            credit_line = dict(
                credit_line,
                name=(line.name + ": " + str(qty_out) + _(' already out')),
                quantity=qty_out,
                account_id=debit_account_id)
            diff = diff * qty_out / line.quantity
            if diff > 0:
                debit_line['debit'] = diff
                credit_line['credit'] = diff
            elif diff < 0:
                # negative cost, reverse the entry
                debit_line['credit'] = -diff
                credit_line['debit'] = -diff
            if diff != 0:
                aml_obj.create(
                    cr, uid, debit_line, context=ctx, check=False)
                aml_obj.create(
                    cr, uid, credit_line, context=ctx, check=False)
        return True

    def _create_landed_accounting_entries(
            self, line, move_id, qty_out, acc_prod=None):
        cost_product = line.cost_line_id and line.cost_line_id.product_id
        if not cost_product:
            return False

        accounts = acc_prod[line.product_id.id]

        debit_account_id = accounts['property_stock_valuation_account_id']
        already_out_account_id = accounts['stock_account_output']

        # /!\ NOTE: This can be optimized by providing the accounts in a dict
        credit_account_id = line.cost_line_id.account_id.id or \
            cost_product.property_account_expense.id or \
            cost_product.categ_id.property_account_expense_categ.id

        if not credit_account_id:
            raise except_orm(
                _('Error!'),
                _('Please configure Stock Expense Account for product: %s.') %
                (cost_product.name))

        return self._create_landed_account_move_line(
            line, move_id, credit_account_id, debit_account_id, qty_out,
            already_out_account_id)
