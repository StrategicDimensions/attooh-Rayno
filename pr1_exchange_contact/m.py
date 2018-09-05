#**************************************************************************
#* PR1 CONFIDENTIAL - Copyrighted Code - Do not re-use. Do not distribute.
#* __________________
#*  [2017] PR1 (pr1.xyz) -  All Rights Reserved. 
#* NOTICE:  All information contained herein is, and remains the property of PR1 and its suppliers, if any.  The intellectual and technical concepts contained herein are proprietary to PR1.xyz and its holding company and are protected by trade secret or copyright law. Dissemination of this information, copying of the concepts used or reproduction of any part of this material in any format is strictly forbidden unless prior written permission is obtained from PR1.xyz.
#**************************************************************************

from odoo import api, fields, models, modules, tools, _

class mail_message(models.Model):
    _inherit = "mail.message"
    
    syn= fields.Boolean('Syn')
    ad_e=fields.Char('Active Directory Email/Login',help="Depending on your setup you may need domain \ username here rather than email")
    
    @api.model
    def create(self,values):
        res = super(mail_message, self).create(values)
        

        #if( ('message_type' in values and values['message_type']=='comment') and ('ad_e' not in values and 'author_id' in values) ):
        if(  ('ad_e' not in values and 'author_id' in values) ):
            user_obj=self.env['res.users']
            user_ids=user_obj.sudo().search([('partner_id','=',values['author_id'])]).ids
            
            if(len(user_ids)>0):
                user=user_obj.sudo().browse(user_ids)
                if(user.syn_e==True and user.ex_validated==True and user.ad_e!=None and user.ad_e!=""):
                    res.write({'syn':False,'ad_e':user.ad_e})
        
        return res