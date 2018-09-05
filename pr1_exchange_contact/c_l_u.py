#**************************************************************************
#* PR1 CONFIDENTIAL - Copyrighted Code - Do not re-use. Do not distribute.
#* __________________
#*  [2017] PR1 (pr1.xyz) -  All Rights Reserved. 
#* NOTICE:  All information contained herein is, and remains the property of PR1 and its suppliers, if any.  The intellectual and technical concepts contained herein are proprietary to PR1.xyz and its holding company and are protected by trade secret or copyright law. Dissemination of this information, copying of the concepts used or reproduction of any part of this material in any format is strictly forbidden unless prior written permission is obtained from PR1.xyz.
#**************************************************************************
from odoo import api, fields, models, modules, tools, _
class c_l_u(models.Model):
    _name="pr1_exchange_contact.c_l_u"
    
    name=fields.Char('Name')                
    user_id=fields.Many2one('res.users','User')
    ad_val=fields.Char('AD Val')
    c_l_id=fields.Many2one('pr1_exchange_contact.c_l','C_L')
    syn_e=fields.Boolean('Sync Enabled',default=False)
              
    