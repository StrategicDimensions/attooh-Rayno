#**************************************************************************
#* PR1 CONFIDENTIAL - Copyrighted Code - Do not re-use. Do not distribute.
#* __________________
#*  [2017] PR1 (pr1.xyz) -  All Rights Reserved. 
#* NOTICE:  All information contained herein is, and remains the property of PR1 and its suppliers, if any.  The intellectual and technical concepts contained herein are proprietary to PR1.xyz and its holding company and are protected by trade secret or copyright law. Dissemination of this information, copying of the concepts used or reproduction of any part of this material in any format is strictly forbidden unless prior written permission is obtained from PR1.xyz.
#**************************************************************************

from odoo import api, fields, models, modules, tools, _
from odoo.exceptions import AccessDenied, UserError
class res_partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"
    birthdate = fields.Date('Birthdate')
    @api.one
    def _is_on_user(self):
        oid=-1
        uid=self.env.user.id
        cr=self.env.cr
        if(len(self.ids)==0):
            return
        ids=self.ids
        if(len(ids)==1):
            record=self.browse(ids[0])
            if(record.is_company==True):
                if(len(record.child_ids)>0):
                    oid=ids[0]
                    ids=[]
                    for cid in record.child_ids:
                        ids.append(cid.id)
                    
        args=[]
        
        
        sql="""select rp.id from res_partner  rp
   inner join pr1_exchange_contact_c_l_p  clp on clp.partner_id=rp.id and clp.active=True
   inner join pr1_exchange_contact_c_l cl on cl.id=clp.c_l_id
  where  (cl.g_l=False and cl.owner_id= """+str(uid)+")  and rp.id in """+"("+str(ids).replace("[", "").replace("]","")+") order by rp.id"
        self.env.cr.execute(sql, args)
        result = self.env.cr.fetchall()
        ret = list(map(lambda x: x[0], result))
        #ok this works by if we are on it return it, if we are not on it dont return it
        #so we need to say if we are a parent and we have the same amount returned that we 
        #have children then set it to true.
        if(oid!=-1 and len(result)==len(ids)):
            for record in self:
                record.is_on_user=True
            
            return
            
        elif (oid!=-1):
            for record in self:
                record.is_on_user=False
            return
        
        #more than one....
        result={}
        for record in self:
            if(record.id in ret):
                record.is_on_user=True
            else:
                record.is_on_user=False
                            
                    
        return  #ok on so remove from c_l_p mark as delete and inactive it. delete it on re sync
    #next step, button visible to add to global/add to my address list
  
                
    
    c_l_p_ids= fields.One2many('pr1_exchange_contact.c_l_p', 'partner_id', 'C_Ls')
    ad_val=fields.Char('AD VAl')
    is_on_user=fields.Boolean(compute='_is_on_user',string="Is On User")
    e_sync=fields.Boolean('e_sync',default=False)
    
    
    @api.model
    def create(self, vals):
        res= super(res_partner, self).create(vals)
        return res
    
   
    @api.multi
    def add_to_my_contact_list1(self):
        self.add_to_my_contact_list()
    
    @api.multi
    def add_all_to_my_contact_list(self):
        c_ids=[]
        ids=self.ids
        for record in self.browse(ids):
            if(len(record.child_ids)==0):
                    return
            for aid in record.child_ids:
                c_ids.append(aid.id)
            
            records_to_add=self.browse(c_ids)
            records_to_add.add_to_my_contact_list()
    
    @api.multi
    def remove_all_from_my_contact_list(self):
        c_ids=[]
        ids=self.ids
        for record in self.browse(ids):
            for aid in record.child_ids:
                c_ids.append(aid.id)
            
            records_to_remove=self.browse(c_ids)
            records_to_remove.remove_from_my_contact_list()
    
    @api.multi        
    def add_to_global_list1(self):
        self.add_to_global_list()

    @api.multi
    def unlink(self):
        
        ids=self.ids
        sql2="update pr1_exchange_contact_c_l_p set active=false where partner_id in  ("+str(ids).replace("[", "").replace("]","")+" ); "
        sql2+="update pr1_exchange_contact_c_l_p set partner_id = null  where partner_id in  ("+str(ids).replace("[", "").replace("]","")+" ); "
        args=[]          
        self.env.cr.execute(sql2, args)
        result = super(res_partner, self).unlink()

        return result
    
    @api.multi    
    def remove_from_my_contact_list1(self):
        self.remove_from_my_contact_list()
    
    @api.multi    
    def remove_from_my_contact_list(self):
        cr=self.env.cr
        ids=self.ids
        uid=self.env.user.id
        c_l_obj=self.env['pr1_exchange_contact.c_l']
        c_l_p_obj=self.env['pr1_exchange_contact.c_l_p']
        c_l_ids=c_l_obj.search([('owner_id','=',uid),('g_l','=',False)]).ids
        if(len(c_l_ids)==0):
            raise UserError(_('You do not have a Contact List!'))
        c_l=c_l_obj.browse(c_l_ids[0])
        if(len(c_l.c_l_u_ids)==0):
            raise UserError(_('You do not have a Contact List!'))
        
        args=[]          
        sql2="delete from pr1_exchange_contact_c_l_p where ad_val is null and  c_l_id="+str(c_l.id)+" and partner_id in ("+str(ids).replace("[", "").replace("]","")+" )"
        cr.execute(sql2, args)
        
        sql="update  pr1_exchange_contact_c_l_p set active=False,syn=False where c_l_id="+str(c_l.id)+" and partner_id in ("+str(ids).replace("[", "").replace("]","")+" )"
        cr.execute(sql, args)
        
    @api.multi
    def add_to_my_contact_list(self):
        cr=self.env.cr
        ids=self.ids
        uid=self.env.user.id
        c_l_obj=self.env['pr1_exchange_contact.c_l']
        c_l_p_obj=self.env['pr1_exchange_contact.c_l_p']
        c_l_ids=c_l_obj.search([('owner_id','=',uid),('g_l','=',False)]).ids
        if(len(c_l_ids)==0):
            raise UserError(_('You do not have a Contact List!'))
        c_l=c_l_obj.browse(c_l_ids[0])
        if(len(c_l.c_l_u_ids)==0):
            raise UserError(_('You do not have a Contact List!'))
            
        sql="""
        select id from res_partner r where  id  in ("""+str(ids).replace("[", "").replace("]","")+""" ) and id not in 
(select partner_id from pr1_exchange_contact_c_l_p clp 
inner join pr1_exchange_contact_c_l_u clu on clu.c_l_id=clp.c_l_id 
inner join pr1_exchange_contact_c_l cl on clu.c_l_id=cl.id
 where clp.active=True and cl.fglobal=False and clu.user_id="""+str(uid)+""" and partner_id  in ("""+str(ids).replace("[", "").replace("]","")+""" ) ) """
        
     #   select id from res_partner r where  id  in ("+str(ids).replace("[", "").replace("]","")+") and id not in (select partner_id from pr1_exchange_contact_c_l_p where partner_id in ("+str(ids).replace("[", "").replace("]","")+") )"
        
        args=[]          
        cr.execute(sql, args)
        result = cr.fetchall()
        ret = list(map(lambda x: x[0], result))
        if(len(ret)>0):
            for id in ret:
                c_l_p={}
                c_l_p['name']=id
                c_l_p['partner_id']=id
                c_l_p['c_l_id']=c_l_ids[0]
                c_l_p_obj.create(c_l_p)         
        
        pr1_set_obj=self.env['pr1_exchange_contact.settings']
        connection=pr1_set_obj.get_connection()
        contact_limit=pr1_set_obj.total_contacts()
        if(contact_limit >connection.contact_limit): #Prevents server from blocking syncs. Ensures user/contact limit stays correct.
            raise UserError(_("Your contact limit is:"+str(connection.contact_limit)+" please either purchase more contacts or remove existing contacts."))

    @api.multi    
    def write(self,vals):
        res = super(res_partner, self).write(vals)
        ids=self.ids
        cr=self.env.cr
        
        if(len(ids)>0):
            args=[]
            sql="update pr1_exchange_contact_c_l_p set syn=False where id in ("+str(ids).replace("[", "").replace("]","")+") and syn=True"
            cr.execute(sql, args)
        return res
