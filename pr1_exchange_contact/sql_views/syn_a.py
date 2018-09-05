# -*- coding: utf-8 -*-
#**************************************************************************
#* PR1 CONFIDENTIAL - Copyrighted Code - Do not re-use. Do not distribute.
#* __________________
#*  [2017] PR1 (pr1.xyz) -  All Rights Reserved. 
#* NOTICE:  All information contained herein is, and remains the property of PR1 and its suppliers, if any.  The intellectual and technical concepts contained herein are proprietary to PR1.xyz and its holding company and are protected by trade secret or copyright law. Dissemination of this information, copying of the concepts used or reproduction of any part of this material in any format is strictly forbidden unless prior written permission is obtained from PR1.xyz.
#**************************************************************************
from odoo import api, fields, models, modules, tools, _
class syn_a(models.Model):
    _name = "pr1_exchange_contact.syn_a"
    _auto = False

    id=fields. Integer('ID', readonly=True)
    state=fields.Char('state', readonly=True)
    email=fields.Char('email', readonly=True)
    partner_id=fields.Integer('Partner ID', readonly=True)
    ad_e=fields.Char('state', readonly=True)
    event_id=fields.Many2one('pr1_exchange_contact.syn_c','event_id') 
    syn=fields.Boolean('SYN')  



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
