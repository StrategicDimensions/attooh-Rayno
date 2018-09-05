#**************************************************************************
#* PR1 CONFIDENTIAL - Copyrighted Code - Do not re-use. Do not distribute.
#* __________________
#*  [2017] PR1 (pr1.xyz) -  All Rights Reserved. 
#* NOTICE:  All information contained herein is, and remains the property of PR1 and its suppliers, if any.  The intellectual and technical concepts contained herein are proprietary to PR1.xyz and its holding company and are protected by trade secret or copyright law. Dissemination of this information, copying of the concepts used or reproduction of any part of this material in any format is strictly forbidden unless prior written permission is obtained from PR1.xyz.
#**************************************************************************
import odoo
from odoo import api, fields, models, modules, tools, SUPERUSER_ID,_
from datetime import datetime
from datetime import date, timedelta
class calendar_event(models.Model):
    """ Model for Calendar Event """
    _name="calendar.event"
    _inherit = 'calendar.event'
     
    ad_val=fields.Char('ad_val')   
    iud=fields.Char('iud')
    syn=fields.Boolean('SYN',default=False)    
              
    @api.multi
    def write(self,vals):
        if(self.env.context and ('from_ex' not in self.env.context )):
            vals['syn']=False
        result = super(calendar_event, self).write(vals)
        return result 
    @api.multi
    def unlink(self):   
        a_ids=[]
        b_ids=[]
        if(self.env.context and 'ignore_code' in self.env.context):
            result = super(calendar_event, self).unlink()
            return result
        
        for record in self.browse(self.ids):
            if(record.syn==True):
                #b_ids.append(record.id)
                record.write({'active':False})
            else:
                result = super(calendar_event, record).unlink()
                
                #a_ids.append(record.id)
        
        
        if(len(b_ids)>0):
            #self.write(cr,uid,b_ids,{'active':False})
            self.browse(b_ids).write({'active':False})
        if(len(a_ids)>0):
            result = self.browse(a_ids).with_context(ignore_code=True).unlink()
            #result = super(calendar_event, self).unlink(cr, uid, aids, context)
            return result
        return True
    
    

class calendar_attendee(models.Model):
    """
    Calendar Attendee Information
    """
    _name = 'calendar.attendee'
    _inherit = 'calendar.attendee'
    syn=fields.Boolean('SYN',default=False)
    
    @api.multi
    def write(self,vals):
        if(self.env.context and 'state' in self.env.context and self.env.context['state']=='accepted'):
            vals['syn']=False
            for record in self.browse(self.ids):
                record.event_id.write({'syn':False})
                #cal_obj.write(cr,uid,{'syn':False}) #force a update to exchange...
        result = super(calendar_attendee, self).write(vals)
        return result 
    
    @api.multi
    def _send_mail_to_attendees(self, template_xmlid, force_send=False):
        usr_obj=self.env['res.users']
        ad_users=usr_obj.search([('syn_e','=',True),('ex_validated','=',True)]).ids
        uids=[] 
        for ad_usr in ad_users:
            uids.append(ad_usr)
        if(self.env.user.id in uids):
            return #dont do it if its an exchange user!! we dont want odoo to have anything to do with it
        
        return super(calendar_attendee, self)._send_mail_to_attendees(template_xmlid, force_send)
   

           
