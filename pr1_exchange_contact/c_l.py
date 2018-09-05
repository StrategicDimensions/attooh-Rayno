#**************************************************************************
#* PR1 CONFIDENTIAL - Copyrighted Code - Do not re-use. Do not distribute.
#* __________________
#*  [2017] PR1 (pr1.xyz) -  All Rights Reserved. 
#* NOTICE:  All information contained herein is, and remains the property of PR1 and its suppliers, if any.  The intellectual and technical concepts contained herein are proprietary to PR1.xyz and its holding company and are protected by trade secret or copyright law. Dissemination of this information, copying of the concepts used or reproduction of any part of this material in any format is strictly forbidden unless prior written permission is obtained from PR1.xyz.
#**************************************************************************
from odoo import api, fields, models, modules, tools, _
class c_l(models.Model):
    _name="pr1_exchange_contact.c_l"
    
    name=fields.Char('Name',size=50)
    owner_id=fields.Many2one('res.users','Owner')
    r_w_to_o=fields.Boolean('R_W_TO_O')
    fglobal=fields.Boolean('Global')
    d_l=fields.Boolean('D_L')#rm
    g_l=fields.Boolean('G_L')#rm
    ad_id=fields.Char('AD_ID',size=256)
    c_l_u_ids= fields.One2many('pr1_exchange_contact.c_l_u', 'c_l_id', 'C_L_Us')
    c_l_p_ids= fields.One2many('pr1_exchange_contact.c_l_p', 'c_l_id', 'C_P_Us')
                
   