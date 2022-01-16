from odoo import fields, models,api
from odoo.exceptions import UserError

from uuid import uuid4
import qrcode
import base64
import logging
from odoo.addons import decimal_precision as dp

from lxml import etree

from odoo import fields, models
import requests
import json
from datetime import datetime,date
import convert_numbers


class AccountMove(models.Model):
    _inherit = 'account.move'
    _order = "invoice_nat_times desc"


    new_customer = fields.Boolean(string='New')

    def _compute_total_amount_comma(self):
        for each in self:
            if each.state == 'posted':
               net_amount = float(each.amount_untaxed)
               before, after = str(net_amount).split('.')
               before_int = int(before)
               after_int = int(after)
               before_ar = convert_numbers.english_to_arabic(before_int)
               after_ar = convert_numbers.english_to_arabic(after_int)
               each.total_amount_comma = before_ar + '.' + after_ar
               # return before_ar + '.' + after_ar

               # each.net_amount_jan_arabic = convert_numbers.english_to_arabic(int(net_amount))
            else:
                # each.net_amount_jan_arabic = convert_numbers.english_to_arabic(int(0))
                before_int = int(0)
                after_int = int(00)
                before_ar = convert_numbers.english_to_arabic(before_int)
                after_ar = convert_numbers.english_to_arabic(after_int)
                each.total_amount_comma = before_ar + '.' + after_ar



    def update_customers(self):
        responce = requests.get('http://37.99.171.209:1002/api/E_Invoice/getcustomer')
        if responce:
            line_data = json.loads(responce.text)
            invoice_length = 0
            for line in line_data:
                if invoice_length <= 100:
                    invoice_length +=1
                    old_customer = self.env['res.partner'].search([('name', '=', line['CUST_NAME'])])
                    if not old_customer:
                        pin = ''
                        ar_pin = ''
                        if line['ADDR_LINE_1']:
                            if line['ADDR_LINE_2']:
                                pin = line['ADDR_LINE_1'] + line['ADDR_LINE_2']
                                ar_pin = line['A_ADDR_LINE_1']
                            else:
                                pin = line['ADDR_LINE_1']
                                ar_pin = line['A_ADDR_LINE_1']
                        else:
                            if line['ADDR_LINE_2']:
                                pin = line['ADDR_LINE_2']
                                ar_pin = line['ADDR_LINE_2']
                        partner_id = self.env['res.partner'].sudo().create({
                            'name': line['CUST_NAME'],
                            'ar_name': line['A_CUST_NAME'],
                            'phone': line['ADDR_TEL'],
                            'cust_code': line['CUST_CODE'],
                            'ar_phone': line['A_ADDR_TEL'],
                            'street': line['ADDR_LINE_1'],
                            'ar_street': line['A_ADDR_LINE_1'],
                            'street2': line['ADDR_LINE_2'],
                            'cust_address': line['ADDR_CONTACT'],
                            'ar_cust_address': line['A_ADDR_CONTACT'],
                            # 'city': line['City'],
                            'email':line['ADDR_EMAIL'],
                            # 'state_id': self.env['res.country.state'].sudo().search(
                            #     [('name', '=', line['State Name'])]).id,
                            # 'zip': line['PIN CODE'],
                            'zip': pin,
                            # 'ar_zip': line['PIN CODE ARABIC'],
                            'ar_zip': ar_pin,
                            # 'country_id': self.env['res.country'].sudo().search([('name', '=', line['Country'])]).id,
                            # 'ar_country': line['CountryArabic'],
                            'vat': line['VAT_REG_NO'],
                            'ar_tax_id': line['A_VAT_REG_NO'],
                            'type_of_customer': 'b_b',
                            'schema_id':'IQA',
                            'schema_id_no': line['VAT_REG_NO'],
                            'building_no': 'xx',
                            'plot_id': 'xx',
                        })
                        print(partner_id,'old')
                    else:
                        pin = ''
                        ar_pin = ''
                        if line['ADDR_LINE_1']:
                            if line['ADDR_LINE_2']:
                                pin = line['ADDR_LINE_1'] + line['ADDR_LINE_2']
                                ar_pin = line['A_ADDR_LINE_1']
                            else:
                                pin = line['ADDR_LINE_1']
                                ar_pin = line['A_ADDR_LINE_1']
                        else:
                            if line['ADDR_LINE_2']:
                                pin = line['ADDR_LINE_2']
                                ar_pin = line['ADDR_LINE_2']


                        partner_id = self.env['res.partner'].sudo().update({
                            'name': line['CUST_NAME'],
                            'ar_name': line['A_CUST_NAME'],
                            'phone': line['ADDR_TEL'],
                            'cust_code': line['CUST_CODE'],
                            'ar_phone': line['A_ADDR_TEL'],
                            'street': line['ADDR_LINE_1'],
                            'email': line['ADDR_EMAIL'],
                            'new_customer':True,
                            'ar_street': line['A_ADDR_LINE_1'],
                            'street2': line['ADDR_LINE_2'],
                            'cust_address': line['ADDR_CONTACT'],
                            'ar_cust_address': line['A_ADDR_CONTACT'],
                            # 'city': line['City'],
                            # 'state_id': self.env['res.country.state'].sudo().search(
                            #     [('name', '=', line['State Name'])]).id,
                            # 'zip': line['PIN CODE'],
                            'zip':pin,
                            # 'ar_zip': line['PIN CODE ARABIC'],
                            'ar_zip':ar_pin,
                            # 'country_id': self.env['res.country'].sudo().search([('name', '=', line['Country'])]).id,
                            # 'ar_country': line['CountryArabic'],
                            'vat': line['VAT_REG_NO'],
                            'ar_tax_id': line['A_VAT_REG_NO'],
                            'type_of_customer': 'b_b',
                            'schema_id':'IQA',
                            'schema_id_no': line['VAT_REG_NO'],
                            'building_no': 'xx',
                            'plot_id': 'xx',
                        })
                        print(line['CUST_NAME'],'partner_id_newwwwwww')

    @api.constrains('invoice_date','partner_id')
    def onchange_of_invoice_date(self):
        if self.partner_id:
            if self.partner_id.cust_address:
                self.address_contact = self.partner_id.cust_address
                self.address_contact_ar = self.partner_id.ar_cust_address

class ResPartner(models.Model):
    _inherit = 'res.partner'

    cust_address = fields.Char(string="cust_address")
    ar_cust_address = fields.Char(string="ar cust_address")


class JsonCalling(models.Model):
    _inherit = 'json.calling'

    def callrequest(self):
        if self.env['json.configuration'].search([]):
            link = self.env['json.configuration'].search([])[0].name
            link_no = self.env['json.configuration'].search([])[-1].no_of_invoices
            import datetime

            responce = requests.get(link)
            json_data = self.env['json.calling'].create({
                'name':'Invoice Creation on '+str(datetime.date.today()),
                'date':datetime.date.today(),
            })
            if responce:
                line_data = json.loads(responce.text)
                invoice_no = None
                invoice_date = None
                invoice_length = 0
                line_data.reverse()
                for line in line_data:
                    if invoice_length <= link_no:
                        old_invoice = self.env['account.move'].search([('system_inv_no','=',line['InvoiceNo'])])
                        if not old_invoice:
                            invoice_length += 1
                            # print(type(line['InvoiceDate']))
                            partner_details = self.env['res.partner'].sudo().search([('name', '=', line['Customer Name'])])
                            if partner_details:
                                partner_id = partner_details
                            else:
                                partner_id = self.env['res.partner'].sudo().create({
                                    'name': line['Customer Name'],
                                    'ar_name':line['Customer Name Arabic'],
                                    'phone': line['Mobile Number'],
                                    'cust_code':line['CUST_CODE'],
                                    'ar_phone':line['Mobile Number Arabic'],
                                    'street': line['Street Name'],
                                    'street2': line['Street2 Name'],
                                    'city': line['City'],
                                    'state_id': self.env['res.country.state'].sudo().search([('name', '=', line['State Name'])]).id,
                                    'zip': line['PIN CODE'],
                                    'ar_zip':line['PIN CODE ARABIC'],
                                    'country_id': self.env['res.country'].sudo().search([('name', '=', line['Country'])]).id,
                                    'ar_country':line['CountryArabic'],
                                    'vat': line['VAT No'],
                                    'ar_tax_id':line['VAT No Arabic'],
                                    'type_of_customer': line['Type of customer'],
                                    'schema_id': line['schemeID'],
                                    'schema_id_no': line['scheme Number'],
                                    'building_no': line['Building Number'],
                                    'plot_id': line['Plot Identification'],
                                })
                            invoice_list = []
                            for inv_line in line['Invoice lines']:
                                product = self.env['product.product'].sudo().search(
                                    [('name', '=', inv_line['Product Name'])])
                                if not product:
                                    product = self.env['product.template'].sudo().create({
                                        'name': inv_line['Product Name'],
                                        'type':'service',
                                        'invoice_policy':'order',
                                    })
                                invoice_list.append((0, 0, {
                                    'name': inv_line['description'],
                                    'price_unit': inv_line['Price'],
                                    'quantity': inv_line['Quantity'],
                                    'discount': inv_line['Discount'],
                                    'product_uom_id': self.env['uom.uom'].sudo().search([('name', '=', inv_line['UoM'])]).id,
                                    'vat_category': inv_line['Vat Category'],
                                    'product_id': product.id,
                                    'tax_ids': [(6, 0, self.env['account.tax'].sudo().search(
                                        [('name', '=', inv_line['Taxes']), ('type_tax_use', '=', 'sale')]).ids)]}))
                            invoice_date = (line['InvoiceDate'].split(" ")[0]).split("/")
                            month = invoice_date[0]
                            day = invoice_date[1]
                            year = invoice_date[2]

                            # ar_amount_total = fields.Char('Total')
                            # ar_amount_untaxed = fields.Char('Untaxed Amount')
                            # ar_amount_tax = fields.Char('Taxes')
                            # amount_in_word_en = fields.Char()
                            # amount_in_word_ar = fields.Char()
                            # amount_in_word_vat_en = fields.Char()
                            # amount_in_word_vat_ar = fields.Char()
                            # arabic_date = fields.Char()



                            account_move = self.env['account.move'].sudo().create({
                                'partner_id': partner_id[0].id,
                                'invoice_line_ids': invoice_list,
                                'move_type': line['Invoice Type'],
                                'payment_mode': line['Payment Mode'],
                                'contact': line['Address Contact'],
                                'contact_address': line['Address Contact Arabic'],
                                'payment_reference': line['payment reference'],
                                # 'invoice_date': year+'-'+month+'-'+day ,
                                'system_inv_no':line['InvoiceNo'],
                                'invoice_nat_time':line['INVOICE_DATETIME'],
                                'customer_po': line['PONO'],
                                'ar_amount_untaxed': line['Word without vat'],
                                'amount_in_word_ar': line['Word with vat'],
                                'system_inv_no_ar':line['InvoiceNoArabic'],
                                'invoice_date_time':line['InvoiceDate'],
                                'advance_with_vat':line['ADVANCE_WITH_VAT'],
                                'a_advance_with_vat':line['A_ADVANCE_WITH_VAT'],
                                'invoice_date_time_ar':line['InvoiceDateArabic'],
                                'sales_man':line['Salesman Name'],
                                'so_number':line['SO No'],
                                'curr_code':line['CURR_CODE'],
                                'remarks':line['ANNOTATION'],
                                'advance': line['ADVANCE'],
                                'ar_advance': line['ADVANCE_A'],
                                'exchg_rate': line['EXCHG_RATE'],
                                'discount_value': line['DISCOUNT_VALUE'],
                                'discount_value_a': line['DISCOUNT_VALUE_A'],
                                'word_without_vat_english': line['Word without vat english'],
                                'word_with_vat_english': line['Word with vat english'],
                                'address_contact':line['Address Contact'],
                                'address_contact_ar':line['Address Contact Arabic'],
                            })
                            invoice_no = line['InvoiceNo']
                            invoice_date = line['InvoiceDate']
                            account_move.action_post()
                            if account_move:
                                import datetime
                                date = datetime.date(account_move.invoice_date.year, account_move.invoice_date.month,
                                                     account_move.invoice_date.day)
                                # month = invoice_date[0]
                                # day = invoice_date[1]
                                # year = invoice_date[2]
                                tota = line['INVOICE_DATETIME'].rsplit(' ')[1].rsplit(':')[0]
                                hr = int(tota[0])
                                min = int(tota[1])
                                # sec = tota[2]
                                import datetime
                                times = datetime.time(hr,min)
                                # datetime.time(each.datetime_field.time().hour, each.datetime_field.time().minute)
                                account_move.invoice_nat_times = datetime.datetime.combine(account_move.invoice_date, times)

                        if line_data:
                            json_data.system_inv_no = invoice_no
                            json_data.invoice_date_time = invoice_date


    def callrequest1(self):
        if self.env['json.configuration'].search([]):
            link = self.env['json.configuration'].search([])[-1].name
            link_no = self.env['json.configuration'].search([])[-1].no_of_invoices
            responce = requests.get(link)
            if responce:
                line_data = json.loads(responce.text)
                invoice_no = None
                invoice_date = None
                invoice_length = 0
                line_data.reverse()
                for line in line_data:
                    if invoice_length <= link_no:
                        old_invoice = self.env['account.move'].search([('system_inv_no', '=', line['InvoiceNo'])])
                        if not old_invoice:
                            invoice_length += 1
                            partner_details = self.env['res.partner'].sudo().search([('name', '=', line['Customer Name'])])
                            if partner_details:
                                partner_id = partner_details
                            else:
                                partner_id = self.env['res.partner'].sudo().create({
                                    'name': line['Customer Name'],
                                    'ar_name':line['Customer Name Arabic'],
                                    'phone': line['Mobile Number'],
                                    'cust_code': line['CUST_CODE'],
                                    'ar_phone':line['Mobile Number Arabic'],
                                    'street': line['Street Name'],
                                    'street2': line['Street2 Name'],
                                    'city': line['City'],
                                    'state_id': self.env['res.country.state'].sudo().search([('name', '=', line['State Name'])]).id,
                                    'zip': line['PIN CODE'],
                                    'ar_zip':line['PIN CODE ARABIC'],
                                    'country_id': self.env['res.country'].sudo().search([('name', '=', line['Country'])]).id,
                                    'ar_country':line['CountryArabic'],
                                    'vat': line['VAT No'],
                                    'ar_tax_id':line['VAT No Arabic'],
                                    'type_of_customer': line['Type of customer'],
                                    'schema_id': line['schemeID'],
                                    'schema_id_no': line['scheme Number'],
                                    'building_no': line['Building Number'],
                                    'plot_id': line['Plot Identification'],
                                })
                            invoice_list = []
                            for inv_line in line['Invoice lines']:
                                product = self.env['product.product'].sudo().search(
                                    [('name', '=', inv_line['Product Name'])])
                                if not product:
                                    product = self.env['product.template'].sudo().create({
                                        'name': inv_line['Product Name'],
                                        'type': 'service',
                                        'invoice_policy': 'order',
                                    })
                                invoice_list.append((0, 0, {
                                    'name': inv_line['description'],
                                    'price_unit': inv_line['Price'],
                                    'quantity': inv_line['Quantity'],
                                    'discount': inv_line['Discount'],
                                    'product_uom_id': self.env['uom.uom'].sudo().search([('name', '=', inv_line['UoM'])]).id,
                                    'vat_category': inv_line['Vat Category'],
                                    'product_id': product.id,
                                    'tax_ids': [(6, 0, self.env['account.tax'].sudo().search(
                                        [('name', '=', inv_line['Taxes']), ('type_tax_use', '=', 'sale')]).ids)]}))
                            invoice_date = (line['InvoiceDate'].split(" ")[0]).split("/")
                            month = invoice_date[0]
                            day = invoice_date[1]
                            year = invoice_date[2]
                            # tota = line['INVOICE_DATETIME'].rsplit(' ')[1].rsplit(':')
                            # import datetime
                            # hr = int(tota[0])
                            # min = int(tota[1])
                            # sec = int(tota[2])
                            # time = datetime.time(hr,hr)
                            # # datetime.time(each.datetime_field.time().hour, each.datetime_field.time().minute)
                            # # account_move.invoice_nat_times = datetime.datetime.combine(date, time)

                            account_move = self.env['account.move'].sudo().create({
                                'partner_id': partner_id.id,
                                'invoice_line_ids': invoice_list,
                                'move_type': line['Invoice Type'],
                                'payment_mode': line['Payment Mode'],
                                'payment_reference': line['payment reference'],
                                # 'invoice_date': year+'-'+month+'-'+day ,
                                'system_inv_no':line['InvoiceNo'],
                                'customer_po':line['PONO'],
                                'invoice_nat_time': line['INVOICE_DATETIME'],
                                'ar_amount_untaxed': line['Word without vat'],
                                'advance_with_vat': line['ADVANCE_WITH_VAT'],
                                'a_advance_with_vat': line['A_ADVANCE_WITH_VAT'],
                                'amount_in_word_ar': line['Word with vat'],
                                'system_inv_no_ar':line['InvoiceNoArabic'],
                                'invoice_date_time':line['InvoiceDate'],
                                'invoice_date_time_ar':line['InvoiceDateArabic'],
                                'contact':line['Address Contact'],
                                'contact_address':line['Address Contact Arabic'],
                                'sales_man':line['Salesman Name'],
                                'so_number':line['SO No'],
                                'remarks': line['ANNOTATION'],
                                'curr_code': line['CURR_CODE'],
                                'advance': line['ADVANCE'],
                                'ar_advance': line['ADVANCE_A'],
                                'exchg_rate': line['EXCHG_RATE'],
                                'discount_value': line['DISCOUNT_VALUE'],
                                'discount_value_a': line['DISCOUNT_VALUE_A'],
                                'word_without_vat_english': line['Word without vat english'],
                                'word_with_vat_english': line['Word with vat english'],
                                'address_contact':line['Address Contact'],
                                'address_contact_ar':line['Address Contact Arabic'],
                            })
                            print(account_move)
                            invoice_no = line['InvoiceNo']
                            invoice_date = line['InvoiceDate']
                            account_move.action_post()
                            if account_move:
                                import datetime
                                date = datetime.date(account_move.invoice_date.year, account_move.invoice_date.month,
                                                     account_move.invoice_date.day)
                                # month = invoice_date[0]
                                # day = invoice_date[1]
                                # year = invoice_date[2]
                                tota = line['INVOICE_DATETIME'].rsplit(' ')[1].rsplit(':')[0]
                                hr = int(tota[0])
                                min = int(tota[1])
                                # sec = tota[2]
                                import datetime
                                times = datetime.time(hr, min)
                                # datetime.time(each.datetime_field.time().hour, each.datetime_field.time().minute)
                                account_move.invoice_nat_times = datetime.datetime.combine(account_move.invoice_date,
                                                                                           times)

                        if line_data:
                            self.system_inv_no = invoice_no
                            self.invoice_date_time = invoice_date
