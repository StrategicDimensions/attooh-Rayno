# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, modules, tools, _
from odoo.exceptions import AccessDenied, UserError
import sys, xml.dom.minidom
from urllib.request import urlopen, Request
import urllib
import json
import requests;
class pr1_exchange_contact_settings(models.Model):
    _name = 'pr1_exchange_contact.settings'

    
    imp_usr= fields.Char('Impersonate Usr',help="This must be a user on exchange with impersonate enabled.")
    imp_pass= fields.Char('Impersonate Password')
    ews_path= fields.Char('EWS Path',help="If you do not include this the system will attempt to find it for you")
    test_usr= fields.Char('Test User',help="This has to be a valid email address of your system. It is used to test if the main account has impersonation enabled.")
    user_name= fields.Char('User Name',help="This is the PR1 username that you were provided with when you purchased the module")
    access_code= fields.Char('Access Code',help="This is your PR1 Access code you were provided with when you purchased the module.")
    state= fields.Selection([('draft', 'Draft'),                              
                              ('successful', 'Successful')],default="draft",string="State")
    sync_user_count= fields.Integer('Sync User Count',readonly=True)
    email_sync_status= fields.Char('Email Sync Status',readonly=True, default="Not Setup", help="This will let you know the status of the email sync. - Not Setup - Not licensed - Synced")
    last_number_synced= fields.Integer('Last Amount Synced',readonly=True)
    sync_partner_count= fields.Integer('Number of partners Synced',readonly=True)
    last_cal_number_synced= fields.Integer('Last number of calendar events synced',readonly=True)
    last_cal_from_ex_number_synced= fields.Integer('Last number of calendar events synced from Exchange',readonly=True)
    last_email_number_synced= fields.Integer('Last number of emails synced to sent from Exchange',readonly=True)
    contact_limit= fields.Integer('Contact Limit',readonly=True)
    user_limit= fields.Integer('User Limit',readonly=True)
    last_sync_time= fields.Datetime('Last Sync Time',readonly=True)
    last_cal_sync_time= fields.Datetime('Last Cal Sync Time',readonly=True)
    lasterrorlog= fields.Text('Last Error Log')
    url= fields.Char('URL')
    lastcal_errorlog= fields.Text('Last Calendar Error Log')
    enable_email_sync=fields.Boolean('Enable Email Sync',help="To enable email sync, please tick this box then click Setup Email Sync. We suggest entering a minimum sync date. Once Setup Email sync is successful please then run the Test Email Sync Button",default=False)
    last_email_errorlog= fields.Text('Last Email Error Log')
    email_sync_min_date= fields.Datetime('Min Email Sync Date',help="If set, email sent will not sync items before this date, highly recommended to set this in system that has been going for a long time!")
                       
    @api.model
    def setup_views(self):
        cr=self.env.cr
        tools.drop_view_if_exists(cr, 'pr1_exchange_contact_syn_a')
        cr.execute("""
            CREATE OR REPLACE VIEW pr1_exchange_contact_syn_a AS (
            select ca.id,ca.syn, ca.state,ca.email,p.id as partner_id,u.ad_e,ca.event_id  as event_id from  calendar_attendee ca
inner join res_partner p on p.id=ca.partner_Id
left outer join res_users u on u.partner_id=p.id order by ca.event_id

            )""")
        
        tools.drop_view_if_exists(cr, 'pr1_exchange_contact_syn_c')
        cr.execute("""
            CREATE OR REPLACE VIEW pr1_exchange_contact_syn_c AS (
              select c.id,c.name,c.privacy as e_class, c.start_date,c.stop as stop_date,c.stop as end_date  ,c.start_datetime,c.stop_datetime as end_datetime,c.rrule, c.final_date,c.description,
c.allday,c.show_as,c.location,c.interval, ca.duration_minutes, ca.duration,c.active as cal_active
,u.ex_validated,u.syn_e,u.login,u.ad_e,c.user_id, c.ad_val, c.iud as iud
 from calendar_event c
inner join res_users u on u.id=c.user_id
left outer join calendar_alarm_calendar_event_rel cr  on c.id=cr.calendar_event_id
left outer join calendar_alarm ca on ca.id=cr.calendar_alarm_id 
where c.syn=false and u.ex_validated=true
order by u.id desc

            )""")
        tools.drop_view_if_exists(cr, 'pr1_exchange_contact_syn_v')
        cr.execute("""
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
        tools.drop_view_if_exists(cr, 'pr1_exchange_contact_syn_pr')
        cr.execute("""
            CREATE OR REPLACE VIEW pr1_exchange_contact_syn_pr AS (
            select id,'res.partner' as model,email as e from res_partner where (e_sync=false or e_sync is null) and (email is not null and email !='' and email like'%@%') 
            )""")  
        tools.drop_view_if_exists(cr, 'pr1_exchange_contact_syn_u')
        cr.execute("""
            CREATE OR REPLACE VIEW pr1_exchange_contact_syn_u AS (
           select id, ad_e,partner_id,syn_e from res_users
where ex_validated=true and syn_e=true and ad_e is not null
            )""")          
    @api.model
    def total_users(self):
        args=[]
        cr=self.env.cr
        sql="select count(id) from res_users where syn_e = true"
        cr.execute(sql, args)
        result = cr.fetchall()
        ret = list(map(lambda x: x[0], result))
        if(len(ret)>0):
            return ret[0]
        else:
            return 0
    @api.model
    def total_contacts(self):
        args=[]
        sql="select count(distinct partner_id) from pr1_exchange_contact_c_l_p"
        cr=self.env.cr
        cr.execute(sql, args)
        result = cr.fetchall()
        ret = list(map(lambda x: x[0], result))
        if(len(ret)>0):
            return ret[0]
        else:
            return 0
        
    @api.model
    def get_connection(self):
        ids=self.search([]).ids
        #ids=self.search(cr,uid,[('state','=','successful')])
        if(len(ids)>0):
            record=self.browse(ids[0])
            if(record.url==False or record.url=="" or record.url==None):
                record.sudo().write({'url':"https://sharedsync.pr1.xyz:4443/exchange.ashx"})
                record=self.browse(ids[0])
            return record
        raise UserError(_('You must configure a connection to exchange'))
        
    @api.one
    def reset_all(self):
        data={}
        sync_obj=self.env['pr1_exchange_contact.syn']
        sync_obj.with_context(reset=True).go_syn()
        user_obj=self.env['res.users']
        users=user_obj.search([('syn_e','=',True)])
        users.write({'syn_e':False})
    @api.one
    def test_csync(self):
        data={}
        sync_obj=self.env['pr1_exchange_contact.syn']
        sync_obj.go_cal_syn()
    @api.one          
    def test_sync(self):
        data={}
        sync_obj=self.env['pr1_exchange_contact.syn']
        sync_obj.go_syn()
        
    @api.one
    def setup_email_sync(self):
        sync_obj=self.env['pr1_exchange_contact.syn']
        sync_obj.go_syn_pr(aids=[self.id],test=True)
    
    @api.one
    def test_email_sync(self):
        sync_obj=self.env['pr1_exchange_contact.syn']
        sync_obj.go_syn_email(from_scheduler=False)
        
    @api.one
    def ex_sync(self):
        u_obj=self.env['res.users']
        user_ids=u_obj.search([('syn_e','=',True),('ex_validated','=',True)]).ids
        data={}
        user_list=[]
        if(len(user_ids)==0):
            raise UserError(_('No Users to force a sync for!'))
            
        for user in u_obj.browse(user_ids):
            if(user.ad_e!=False):
                usr={}
                usr['o_id']=user.id
                usr['ad_e']=user.ad_e
                usr['login']=user.login
                user_list.append(usr)
        if(len(user_list)==0):
            raise UserError(_('No Users to force a sync for!'))
        
        data['ou']=user_list
        connection=self.get_connection()
        data['user_name']=connection.user_name
        data['access_code']=connection.access_code
        data['Param']='exsync'
        params = json.dumps(data).encode('utf8')
        req = Request(connection.url, data=params)
        req.add_header('Content-Type', 'application/json')
        response = urlopen(req)
        response_data=response.read().decode('utf8')
        data2 = json.loads(response_data) 
        if(data2['ErrorMessage']=="Success!"):
            raise UserError(_("Data has been sync'd from Exchange to the profile, please sync calendars now."))
        elif(data2['ErrorMessage']!="Success"):
            raise UserError(data2['ErrorMessage'])
            
    @api.one 
    def validate_users(self):
        u_obj=self.env['res.users']
        user_ids=u_obj.search([('syn_e','=',True),('ex_validated','=',False)]).ids
        data={}
        user_list=[]
        if(len(user_ids)==0):
            raise UserError(_('No Users to test!'))
            
        for user in u_obj.browse(user_ids):
            if(user.ad_e!=False):
                usr={}
                usr['o_id']=user.id
                usr['ad_e']=user.ad_e
                usr['login']=user.login
                user_list.append(usr)
        if(len(user_list)==0):
            raise UserError(_('No Users to test!'))
        
        data['users']=user_list
        connection=self.get_connection()
        data['user_name']=connection.user_name
        data['access_code']=connection.access_code
        data['Param']='testusers'
        params = json.dumps(data).encode('utf8')
        req = Request(connection.url, data=params)
        req.add_header('Content-Type', 'application/json')
        response = urlopen(req)
        response_data=response.read().decode('utf8')
        data2 = json.loads(response_data) 
        if(data2['ErrorMessage']=="Success!"):
            usrs=[]
            for user in data2['ValidatedUsers']:
                usrs.append(int(user['o_id']))
            
            if(len(usrs)>0):
                u_obj.browse(usrs).write({'ex_validated':True})
                self.env.cr.commit()
            raise UserError(_('All users have validated against exchange!'))
        elif(data2['ErrorMessage']=="See Log"):
            log=""
            for log_line in data2['Errors']:
                log=log+log_line+"\r\n"
            usrs=[]
            for user in data2['ValidatedUsers']:
                usrs.append(int(user['o_id']))
            if(len(usrs)>0):
                u_obj.browse(usrs).write({'ex_validated':True})
                cr.commit()
            raise UserError(_(log))
        
    @api.multi
    def test_connection(self):
        data={}
        ids=self.ids
        records=self.browse(ids)
        for record in records:
            data['EWS_Path']=record.ews_path
            data['Email']=record.imp_usr
            data['Password']=record.imp_pass
            data['IPE']=record.test_usr
            data['user_name']=record.user_name
            data['access_code']=record.access_code
            data['Param']='testcon'
            connection=self.get_connection()
            params = json.dumps(data).encode('utf8')
            req = Request(connection.url, data=params)
            req.add_header('Content-Type', 'application/json')
            response = urlopen(req)
            response_data=response.read().decode('utf8')
            data2 = json.loads(response_data) 
            if(data2['ErrorMessage']==None):
                a=1#SUCCESS!!!!! TODO: Stick EWS URL in here on reponse.
                #state move to successful1!
                record.write({'user_name':data2['user_name'],'access_code':data2['access_code'],'ews_path':data2['ews_path'],'user_limit':data2['UserLimit'],'contact_limit':data2['ContactLimit'],'state':'successful'})
            else:
                raise UserError(_(data2['ErrorMessage']))
            a=response
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
