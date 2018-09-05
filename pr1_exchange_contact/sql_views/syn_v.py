# -*- coding: utf-8 -*-
#**************************************************************************
#* PR1 CONFIDENTIAL - Copyrighted Code - Do not re-use. Do not distribute.
#* __________________
#*  [2017] PR1 (pr1.xyz) -  All Rights Reserved. 
#* NOTICE:  All information contained herein is, and remains the property of PR1 and its suppliers, if any.  The intellectual and technical concepts contained herein are proprietary to PR1.xyz and its holding company and are protected by trade secret or copyright law. Dissemination of this information, copying of the concepts used or reproduction of any part of this material in any format is strictly forbidden unless prior written permission is obtained from PR1.xyz.
#**************************************************************************
from odoo import api, fields, models, modules, tools, _
class syn_v(models.Model):
    _name = "pr1_exchange_contact.syn_v"
    _auto = False

    partner_id= fields.Integer('Partner ID', readonly=True)
    name= fields.Char('Name', readonly=True)
    comment= fields.Text('Comment', readonly=True)
    use_parent_address= fields.Boolean('Use Parent Address', readonly=True)
    street= fields.Char('street', readonly=True)
    supplier= fields.Boolean('Supplier', readonly=True)
    customer= fields.Boolean('customer', readonly=True)
    city= fields.Char('city', readonly=True)
    zip= fields.Char('zip', readonly=True)
    title= fields.Char('title', readonly=True)
    company_title= fields.Char('company_title', readonly=True)
    function= fields.Char('function', readonly=True)
    phone= fields.Char('phone', readonly=True)
    type= fields.Char('type', readonly=True)
    email= fields.Char('email', readonly=True)
    website= fields.Char('website', readonly=True)
    fax= fields.Char('fax', readonly=True)
    street2= fields.Char('street2', readonly=True)
    country_name= fields.Char('country_name', readonly=True)
    parent_id= fields.Integer('parent_id', readonly=True)
    mobile= fields.Char('mobile', readonly=True)
    birthdate= fields.Char('birthdate', readonly=True)
    is_company= fields.Boolean('is_company', readonly=True)
    state_name= fields.Char('state_name', readonly=True)
    company_name= fields.Char('company_name', readonly=True)
    company_phone= fields.Char('company_phone', readonly=True)
    c_street= fields.Char('c_street', readonly=True)
    c_street2= fields.Char('c_street2', readonly=True)
    c_city= fields.Char('c_city', readonly=True)
    c_zip= fields.Char('c_zip', readonly=True)
    c_state_name= fields.Char('c_state_name', readonly=True)
    c_country_name= fields.Char('c_country_name', readonly=True)
    ad_val= fields.Char('ad_val', readonly=True)
    c_list_name= fields.Char('c_list_name', readonly=True)
    c_list_global= fields.Char('c_list_global', readonly=True)
    c_ad_id= fields.Char('c_ad_id', readonly=True)
    o_id= fields.Char('o_id', readonly=True)
    clp_active= fields.Boolean('clp_active', readonly=True)
    syn=fields.Boolean('syn',readonly=True)
    ad_e=fields.Char('ad_e',size=512,readonly=True)
    c_l_i_d=fields.Char('c_l_i_d',readonly=True)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
