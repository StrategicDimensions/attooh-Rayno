#**************************************************************************
#* PR1 CONFIDENTIAL - Copyrighted Code - Do not re-use. Do not distribute.
#* __________________
#*  [2017] PR1 (pr1.xyz) -  All Rights Reserved. 
#* NOTICE:  All information contained herein is, and remains the property of PR1 and its suppliers, if any.  The intellectual and technical concepts contained herein are proprietary to PR1.xyz and its holding company and are protected by trade secret or copyright law. Dissemination of this information, copying of the concepts used or reproduction of any part of this material in any format is strictly forbidden unless prior written permission is obtained from PR1.xyz.
#**************************************************************************
from odoo import api, fields, models, modules, tools, _

class a_d(models.Model):
    _name="pr1_exchange_contact.a_d"
    
    a_d_loc=fields.Char('A_D_LOC')
    a_d_key=fields.Char('A_D_Key')
    a_d_un=fields.Char('A_D_UN')                
    a_d_mu=fields.Integer('A_D_MU')
              
