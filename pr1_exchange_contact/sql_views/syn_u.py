# -*- coding: utf-8 -*-
#**************************************************************************
#* PR1 CONFIDENTIAL - Copyrighted Code - Do not re-use. Do not distribute.
#* __________________
#*  [2017] PR1 (pr1.xyz) -  All Rights Reserved. 
#* NOTICE:  All information contained herein is, and remains the property of PR1 and its suppliers, if any.  The intellectual and technical concepts contained herein are proprietary to PR1.xyz and its holding company and are protected by trade secret or copyright law. Dissemination of this information, copying of the concepts used or reproduction of any part of this material in any format is strictly forbidden unless prior written permission is obtained from PR1.xyz.
#**************************************************************************
from odoo import api, fields, models, modules, tools, _
class syn_u(models.Model):
    _name = "pr1_exchange_contact.syn_u"
    _auto = False

    ad_e=fields.Char('ad_e',size=512,readonly=True)
    partner_id= fields.Integer('Partner ID', readonly=True)
    syn_e=fields.Boolean('syn',readonly=True)
    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
