from datetime import datetime
from odoo import api, fields, models, modules, tools, _
from odoo.exceptions import AccessDenied, UserError
class res_users(models.Model):
    _name="res.users"
    _inherit="res.users"
    @api.model
    def in_rol(self,rn,usr=None):
        
        for r in usr.groups_id:
            if(r.name==rn):
                return True  
        return False
    
    @api.multi
    def write(self, vals):
       cr=self.env.cr
       ids=self.ids
       if('ad_e' in vals):
           vals['ex_validated']=False 
       if('active' in vals and vals['active']==False):
           vals['ex_validated']=False 
           vals['syn_e']=False
           
       res = super(res_users, self).write( vals)
       clu_obj=self.env['pr1_exchange_contact.c_l_u']
       cl_obj=self.env['pr1_exchange_contact.c_l']
       a_grp=-1
       b_grp=-1
       found=False
       for key in vals.keys():
            if(key.find('in_group')!=-1):
                #if(len(cg_ids)==0):
                grp_obj=self.env['res.groups']
                grp_ids=grp_obj.search([('name','=','Exchange Contact User')]).ids
                a_grp=grp_ids[0]
               # b_grp=grp_ids[1]
            group_id=list(vals.keys())[0][9:]
            if(group_id==str(a_grp)): #or group_id==str(b_grp)):
                found==True
                
       if(found==True or ('syn_e' in vals and vals['syn_e']==True)):
            pr1_set_obj=self.env['pr1_exchange_contact.settings']
            connection=pr1_set_obj.get_connection()
            usr_count=pr1_set_obj.total_users()
            if(usr_count >connection.user_limit): #prevents server from blocking sync - do not tamper.
                if(connection.user_limit==0):
                    raise UserError(_("Please ensure that you have setup and run test connection before you enable the Exchange Sync Checkbox."))
                elif(usr_count >connection.user_limit):
                    raise UserError(_("Your user limit is:"+str(connection.user_limit)+" please either purchase more users or disable the sync on existing users."))
                                 
       for id in self.ids:
           if('syn_e' in vals and vals['syn_e']==True):
               pr1_set_obj=self.env['pr1_exchange_contact.settings']
               connection=pr1_set_obj.get_connection()
               usr_count=pr1_set_obj.total_users()
               if(usr_count >connection.user_limit):#prevents server from blocking sync - do not tamper.
                   if(connection.user_limit==0):
                       raise UserError(_('Please ensure that you have setup and run test connection before you enable the Exchange Sync Checkbox.'))
                       
                   else:
                       raise UserError(_("Your user limit is:"+str(connection.user_limit)+" please either purchase more users or disable the sync on existing users."))
      
               usr_obj=self.env['res.users']
               clu_ids=clu_obj.search([('user_id','=',id)]).ids
               clus=clu_obj.browse(clu_ids)
               found=False
               for clu in clus:
                   if(clu.c_l_id.g_l==False):
                       found=True
                       clu.write({'syn_e':True})
                       #clu_obj.write(cr,uid,clu.id,{'syn_e':True})   
                   
               if(found==False):
                   usr=usr_obj.browse(id)
                   obj={}
                   obj['owner_id']=id
                   obj['name']=usr.name+" contact list"
                   cl_id=cl_obj.create(obj).id
                   clu_obj1={}
                   clu_obj1['user_id']=id
                   clu_obj1['c_l_id']=cl_id
                   clu_obj1['syn_e']=True
                   clu_obj1['name']=usr.name+" contact list"
                   c_l_u_id=clu_obj.create(clu_obj1).id
           elif('syn_e' in vals and vals['syn_e']==False):
               clu_ids=clu_obj.search([('user_id','=',id)]).ids
               clus=clu_obj.browse(clu_ids)
               for clu in clus:
                   if(clu.c_l_id.g_l==False):
                       clu.write({'syn_e':False})
                       #clu_obj.write(cr,uid,clu.id,{'syn_e':False})
                       args=[] 
                       sql="update pr1_exchange_contact_c_l_p set active=False where c_l_id="+str(clu.id)+";"
                       self.env.cr.execute(sql, args)
               
       return res 
   
       @api.model
       def setup_views(self):
        tools.drop_view_if_exists(cr, 'pr1_exchange_contact_syn_a')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW pr1_exchange_contact_syn_a AS (
            select ca.id,ca.syn, ca.state,ca.email,p.id as partner_id,u.ad_e,ca.event_id  as event_id from calendar_attendee ca
inner join res_partner p on p.id=ca.partner_Id
left outer join res_users u on u.partner_id=p.id order by ca.event_id

            )""")
        
        tools.drop_view_if_exists(cr, 'pr1_exchange_contact_syn_c')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW pr1_exchange_contact_syn_c AS (
              select c.id,c.name,c.class as e_class, c.start_date,c.stop as stop_date,c.stop as end_date  ,c.start_datetime,c.stop_datetime as end_datetime,c.rrule, c.final_date,c.description,
c.allday,c.show_as,c.location,c.interval, ca.duration_minutes, ca.duration,c.active as cal_active
,u.ex_validated,u.syn_e,u.login,u.ad_e,c.user_id, c.ad_val, c.iud
 from calendar_event c
inner join res_users u on u.id=c.user_id
left outer join calendar_alarm_calendar_event_rel cr  on c.id=cr.calendar_event_id
left outer join calendar_alarm ca on ca.id=cr.calendar_alarm_id 
where c.syn=false and u.ex_validated=true
order by u.id desc

            )""")
        tools.drop_view_if_exists(cr, 'pr1_exchange_contact_syn_v')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW pr1_exchange_contact_syn_v AS (
                SELECT clp.id as id, p.id as partner_id, p.name,  p.comment, false as use_parent_address,  p.street, p.supplier, p.customer, p.city,  
p.zip, rpt.name as title, p.function, p.phone,p.type, p.email, p.website, '' as fax, p.street2, 
 cc.name as country_name, p.parent_id,  
  p.mobile, p.birthdate,  p.is_company, s.name as state_name, 
   c.name AS company_name, c.phone AS company_phone, c.street AS c_street, c.street2 AS c_street2, c.city AS c_city, 
   c.zip AS c_zip, 
   c_s.name AS c_state_name, c_cc.name AS c_country_name,clp.ad_val,
   cl.name as c_list_name, cl.fglobal as c_list_global,cl.ad_id as c_ad_id,cl.owner_id as o_id,clp.active as clp_active,c_rpt.name as company_title,clp.syn,ru.ad_e,cl.id as c_l_i_d
   FROM res_partner p
   inner join pr1_exchange_contact_c_l_p clp on p.id=clp.partner_id and clp.syn=False
   inner join pr1_exchange_contact_c_l cl on cl.id=clp.c_l_id
    left outer join res_partner_title rpt on rpt.id=p.title
    left outer join  res_users ru on cl.owner_id=ru.id
   LEFT OUTER JOIN res_partner c ON p.parent_id = c.id
    left outer join res_partner_title c_rpt on rpt.id=c.title
   LEFT OUTER  JOIN res_country_state s ON p.state_id = s.id
   LEFT OUTER  JOIN res_country_state c_s ON c.state_id = c_s.id
   LEFT OUTER  JOIN res_country cc ON p.country_id = cc.id
   LEFT OUTER  JOIN res_country c_cc ON c.country_id = c_cc.id
  WHERE p.is_company = false and ru.ex_validated=true and ru.syn_e=true and clp.syn=false  and ru.ad_e is not null
            )""")

    
    ad_e=fields.Char('Active Directory Email/Login',help="Depending on your setup you may need domain \ username here rather than email")
    syn_e=fields.Boolean('Exchange Sync Enabled',default=False)
    ex_validated=fields.Boolean('Ex Validated',readonly=True)
                   
              

    