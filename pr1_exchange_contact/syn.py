from odoo import api, fields, models, modules, tools, _
from odoo.exceptions import AccessDenied, UserError
import sys,   xml.dom.minidom
import json
from urllib.request import urlopen, Request
import requests;
from datetime import datetime
from datetime import date, timedelta

import logging
logger = logging.getLogger(__name__)
class syn(models.Model):
    _description ='syn'
    _name = 'pr1_exchange_contact.syn'
    
    #//todo next make the role that says sync..
    #modify the create code so that it creates a contct list if one doesnt exist upon assignemnt of role
    #add 'enabled' to contact list
    #get back from server the 'limits' from test connection
    #throw data to server
    #handle exceptions
    #make wizard
    #worry about user is impersonate user for that sync.
    #worry about global list. 
    @api.model
    def get_needing_to_sync(self):
        args=[]
        cr=self.env.cr
        query="""
SELECT clp.id,p.id as partner_id, p.name,  p.comment, false as use_parent_address, p.street, p.supplier, p.customer, p.city,  
p.zip, p.title, p.function, p.phone,p.type, p.email, p.vat, p.website, '' as fax, p.street2, 
 cc.name, p.parent_id, p.employee, 
  p.mobile, p.birthdate,  p.is_company, s.name as state_name,  cc.name AS country_name,
   c.name AS company_name, c.phone AS company_phone, c.street AS c_street, c.street2 AS c_street2, c.city AS c_city, 
   c.zip AS c_zip, 
   c_s.name AS c_state_name, c_cc.name AS c_country_name,clp.ad_val,
   cl.name as c_list_name, cl.fglobal as c_list_global,cl.ad_id as c_ad_id,cl.owner_id as o_id,clp.active as clp_active
   FROM res_partner p
   inner join pr1_exchange_contact_c_l_p clp on p.id=clp.partner_id and clp.syn=False
   inner join pr1_exchange_contact_c_l cl on cl.id=clp.c_l_id
   LEFT OUTER JOIN res_partner c ON p.parent_id = c.id
   LEFT OUTER  JOIN res_country_state s ON p.state_id = s.id
   LEFT OUTER  JOIN res_country_state c_s ON c.state_id = c_s.id
   LEFT OUTER  JOIN res_country cc ON p.country_id = cc.id
   LEFT OUTER  JOIN res_country c_cc ON c.country_id = c_cc.id
  WHERE p.is_company = false

             """
        cr.execute(query, args)
        result = cr.fetchall()
        #ret = map(lambda x: x[0], result)
        return result 
    @api.model
    def go_syn_pr(self, automatic=False, use_new_cursor=False,   context={},aids=[],test=False,return_dict=False):
        data={}
        cr=self.env.cr
        s_obj=self.env['pr1_exchange_contact.settings']
        syn_u_obj=self.env['pr1_exchange_contact.syn_u']
        if(len(aids)==0):
            aids=s_obj.search([]).ids
        
        p_obj=self.env['res.partner']
        connection=s_obj.sudo().get_connection()
        if(connection.enable_email_sync==False):
            return
        if(connection.email_sync_status!='Synced' and test==False):
            return
        data['user_name']=connection.user_name
        data['access_code']=connection.access_code
        data['Param']='checkemailsync'
        #need to test this all now.... so ned to do module update on admin
        #new copy down pr1
        #try sync of partners...
        #then continue email server side.
        
        req = Request(connection.url)
        req.add_header('Content-Type', 'application/json')
       
        response=None
        data2=None
        if(return_dict==False):
            params = json.dumps(data).encode('utf8')
            req = Request(connection.url, data=params)
            req.add_header('Content-Type', 'application/json')
            response_data=response.read().decode('utf8')
            data2 = json.loads(response_data) 
            if(data2['ErrorMessage']=="Success!"): 
                return_dict=True
            else:
                return_dict=False
        pr_list=[]
        pu_list=[]
        if(return_dict==True):
            data={}
            data['user_name']=connection.user_name
            data['access_code']=connection.access_code
            data['Param']='prsync'
            prs=[]
            pr_obj=self.env['pr1_exchange_contact.syn_pr']
            ids=[]
            u_ids=[]
            try:
                ids=pr_obj.sudo().search([]).ids
                u_ids=syn_u_obj.sudo().search([]).ids
            except:
                cr.commit()
                s_obj.setup_views()
                ids=pr_obj.sudo().search([]).ids
                u_ids=syn_u_obj.sudo().search([]).ids
            if(len(ids)==0):
                if(test==True):
                    raise UserError(_('Nothing to sync!'))
            records=pr_obj.sudo().browse(ids)
            u_records=syn_u_obj.sudo().browse(u_ids)
         
            p_ids=[]
            for record in records:
                pr={}
                pr['p_id']=record.id
                pr['model']=record.model
                pr['e']=record.e
                pr_list.append(pr)
                p_ids.append(record.id)
            for u_record in u_records:
                pr_u={}
                pr_u['odoo_id']=u_record.id
                pr_u['ad_e']=u_record.ad_e
                pr_u['syn_e']=u_record.syn_e
                pr_u['partner_id']=u_record.partner_id
                pu_list.append(pr_u)
            data['prs']=pr_list
            data['pr_us']=pu_list
            if(return_dict==True and test==False):
                return data
            data['Param']='prsync'
            
            params = json.dumps(data).encode('utf8')
            req = Request(connection.url, data=params)
            req.add_header('Content-Type', 'application/json')
            response = urlopen(req)
            response_data=response.read().decode('utf8')
            data2 = json.loads(response_data) 
            records=s_obj.browse(aids)
            if(data2['ErrorMessage']=="Success!"):
                s_obj.browse(aids).write({'email_sync_status':'Synced'})
            elif(data2['ErrorMessage']=="See Log"):
                s_obj.browse(aids).write({'email_sync_status':'Unknown Error'})
                if(test==True):
                    raise UserError(_('Please contact support: info@pr1.xyz '+ data2['ErrorMessage']))
            
        else:
            s_obj.browse(aids).write({'email_sync_status':'Not licensed'})
            if(test==True):
                raise UserError(_(data2['ErrorMessage']))
        
        
        
    @api.model
    def go_syn_email(self,  automatic=False, use_new_cursor=False,   context={}, from_scheduler=True):
        cr=self.env.cr    
        data={}
        mm_obj=self.env['mail.message']
        mm_ids=mm_obj.sudo().search([('syn','=',False)]).ids
        to_ignore=[]
        outbound_email={}
        emails=[]
        s_obj=self.env['pr1_exchange_contact.settings']
        connection=s_obj.sudo().get_connection()
        if(connection.enable_email_sync==False):
            if(from_scheduler==False):
                raise UserError(_('Please tick enable email sync'))
            else:
                return
        email_ids=[]
        s_min_date=connection.email_sync_min_date
        min_date=False
        if(s_min_date!=False):
            min_date=datetime.strptime(s_min_date, '%Y-%m-%d %H:%M:%S')
        data=self.sudo().go_syn_pr(  False, False,   context,test=False,return_dict=True)
        for record in mm_obj.browse(mm_ids):
            outbound_email={}
            outbound_email['date']=record.date
            date_sent=datetime.strptime(record.date, '%Y-%m-%d %H:%M:%S')
            if(s_min_date!=False and date_sent<min_date):
                continue
            email_ids.append(record.id)
            if(len(record.body)==0):
                to_ignore.append(record.id)
                continue
            outbound_email['body']=record.body
            outbound_email['record_name']=record.record_name
            outbound_email['subject']=record.subject
            outbound_email['odoo_id']=record.id
            outbound_email['create_uid']=record.create_uid.id
            outbound_email['message_id']=record.message_id
            if(record.parent_id.id!=False):
                outbound_email['parent_id']=record.parent_id.id
            if(record.res_id!=False and record.res_id!=None):
                outbound_email['res_id']=record.res_id
            outbound_email['reply_to']=record.reply_to
            if(record.ad_e!=False):
                outbound_email['ad_e']=record.ad_e
            elif(len(record.author_id.user_ids)>0):
                if(record.author_id.user_ids[0].syn_e==True):
                    outbound_email['ad_e']=record.author_id.user_ids[0].ad_e
            
            outbound_email['author_id']=record.author_id.id
            outbound_email['model']=record.model
            outbound_email['email_from']=record.email_from
            
            recips=[]
            ids_already_added=[]
            for to in record.partner_ids:
                if(to.id in ids_already_added):
                    continue
                recip={}
                recip['partner_id']=to.id
                recip['mail_unique_id']=record.message_id
                recip['email_address']=to.email
                recips.append(recip)
                ids_already_added.append(to.id)
            for to in record.notification_ids:
                if(to.is_email==False):
                    continue
                if(to.res_partner_id.id in ids_already_added):
                    continue
                recip={}
                recip['partner_id']=to.res_partner_id.id
                recip['mail_unique_id']=record.message_id
                recip['email_address']=to.res_partner_id.email
                recips.append(recip)
                ids_already_added.append(to.res_partner_id.id)
                
            outbound_email['recipients']=recips
            if(len(recips)>0):
                emails.append(outbound_email)
            else:
                to_ignore.append(record.id)
                
        if(len(to_ignore)>0):
            mm_obj.browse(to_ignore).write({'syn':True})
            
        if(len(emails)>0):    
            data['emails']=emails
            req = Request(connection.url)
            req.add_header('Content-Type', 'application/json')
           
            try:
                data['Param']='emailsync'
                params = json.dumps(data).encode('utf8')
                req = Request(connection.url, data=params)
                req.add_header('Content-Type', 'application/json')
                response = urlopen(req)
                response_data=response.read().decode('utf8')
                data2 = json.loads(response_data)  
                num_emails_done=0
                if(data2['ErrorMessage']=="Success!"):
                    if('ids' in data2):
                        num_emails_done=len(data2['ids'])
                        sql="update mail_message set syn=True where id in ("+str(data2['ids']).replace("[","").replace("]","")+")"
                        cr.execute(sql)
                    connection.write({'last_email_number_synced':num_emails_done,'email_sync_status':'Synced'})
                elif(data2['ErrorMessage']=="See Log"):
                    connection.write({'email_sync_status':'Unknown Error'})
                    if(test==True):
                        raise UserError(_('Please contact support: info@pr1.xyz '+ data2['ErrorMessage']))
            except Exception as e:
                 raise UserError(_('Please contact support: info@pr1.xyz - Unable to connect'))
        else:
            connection.write({'last_email_number_synced':0,'email_sync_status':'Synced'})
                
        #OVERRIDE CREATE OF MAIL MESSAGE TO PREVENT CREATION OF EMAIL!
        #GET EMAILS TO SYNC (WHERE SYNC=TRUE)
        #PUSH TO SERVER
            #List response.mail_message_ids.write(sync,True)
            #if response.groups
            #Loop through reponse.user_groups
                #load user
                #Loop through usergroup_message
                #  mail_message_ids = mail_msg_obj.search(cr, uid, [('message_id', 'in', msg_references)], context=context)
                
                #Attempt to find reference using EWS item.References
                #mail thread
                # def message_route(self, cr, uid, message, message_dict, model=None, thread_id=None,
                      #custom_values=None, context=None):
                #so usergroup_message={} of exact mail_message definitions..
                #if(user message private)
                # mark private
                #create message
    
    @api.model
    def parse_date(self,datestring):
        if(datestring=="" or datestring==None or datestring==False):
            return ""
       
        try:
            res=datetime.utcfromtimestamp(float(datestring.split('(')[1][:-5])).strftime('%Y-%m-%d %H:%M:%S')
        except:
            res=datetime.utcfromtimestamp(float(datestring.split('(')[1][:-5])).strftime('%Y-%m-%d')
        return res
    
    @api.model
    def go_ex_syn(self):
        s_obj=self.env['pr1_exchange_contact.settings']
        connection=s_obj.sudo().get_connection()
        connection.ex_sync()
        
    @api.model
    def go_cal_syn(self,  automatic=False, use_new_cursor=False):
        s_obj=self.env['pr1_exchange_contact.settings']
        s_cobj=self.env['pr1_exchange_contact.syn_c']
        cal_att_obj=self.env['calendar.attendee']
        cal_evt_obj=self.env['calendar.event']
        u_obj=self.env['res.users']
        u_ids=u_obj.search([('ex_validated','=',True)]).ids
        users=u_obj.browse(u_ids)
        c_ids=[]
        cr=self.env.cr
        try:
            c_ids=s_cobj.sudo().search([]).ids
        except:
            cr.commit()
            s_obj.setup_views()
            c_ids=s_cobj.sudo().search([]).ids
        records=s_cobj.sudo().browse(c_ids)
        connection=s_obj.sudo().get_connection()
        rcs=[]
        data={}
        accepted_ids=[]
        data['Param']='cal'
        data['user_name']=connection.user_name
        data['access_code']=connection.access_code
        ou=[]
        if(len(records)>0): #try and get one, if it fails the view might have changed so resetup views.
            try:
                name=records[0]['name']
            except:
                cr.commit()
                s_obj.setup_views()
                records=s_cobj.sudo().browse(c_ids)
        att_update=[] 
        for record in records:
            
            r={}
            oud={}
            r['name']=record.name or ''
            r['id']=record.id
            r['start_date']=record.start_date or ''
            r['stop_date']=record.stop_date or ''
            r['end_date']=record.end_date or ''
            r['start_datetime']=record.start_datetime or ''
            r['end_datetime']=record.end_datetime or ''
            r['rrule']=record.rrule or ''
            r['final_date']=record.final_date or ''
            r['user_id']=record.user_id
           
            r['ex_validated']=record.ex_validated
            r['syn_e']=record.syn_e 
            r['ad_e']=record.ad_e or ''
            r['iud']=record.iud or ''
            r['uniqueid']=record.ad_val or ''
            r['login']=record.login or ''
            r['description']=record.description or ''
            r['allday']=record.allday
            r['show_as']=record.show_as or ''
            r['location']=record.location or ''
            r['interval']=record.interval or '-1'
            r['duration_minutes']=record.duration_minutes or '-1'
            r['duration']=record.duration or '-1'
            r['active']=record.cal_active
            
            satt=[]
            for att in record.att:
                if(att.syn==False):
                    at={}
                    at['id']=att.id
                    at['state']=att.state or ''
                    at['email']=att.email or ''
                    at['partner_id']=att.partner_id or '-1'
                    at['state']=att.state or ''
                    at['ad_e']=att.ad_e or ''
                    att_update.append(att.id)
                    satt.append(at)
            r['att']=satt
            rcs.append(r)
            
        for record in users:
            oud={}
            oud['o_id']=record.id
            oud['login']=record.ad_e
            oud['ad_e']=record.ad_e or ''
            
            if(record.ex_validated):
                oud['barred']=False
            else:
                oud['barred']=True
            ou.append(oud)
        data['cals']=rcs
        data['ou']=ou
        req = Request(connection.url)
        req.add_header('Content-Type', 'application/json')
        n_from_ex=0
       
        try:
            params = json.dumps(data).encode('utf8')
            req = Request(connection.url, data=params)
            req.add_header('Content-Type', 'application/json')
            response = urlopen(req)
            response_data=response.read().decode('utf8')
            data2 = json.loads(response_data) 
            logger.info('data2:'+str(data2))
            ex={}
            sql=""
            if('suc' in data2 and data2['suc']==True):
                calendar_event = self.env['calendar.event']
                calendar_attendee_obj = self.env['calendar.attendee']
                logger.info('data2[cb]:'+str(data2['CB']))
                if('CB' in data2):
                    n_from_ex=len(data2['CB'])    
                for ob in data2['CB']:
                    if(ob['FromEX']==True):
                        cal_obj={}
                        sql2="select id from calendar_event where iud like '"+ob['iud']+"%'"
                        id=False
                        args=[]
                        cr.execute(sql2, args)
                        result = cr.fetchall()
                        if(result):
                            logger.info('Found result')
                            ret = list(map(lambda x: x[0], result))
                            id=ret
                        else:
                            logger.info('New Item result')                                
                            id=False
                        
                        cal_obj['name']=ob['name']
                        cal_obj['allday']=ob['allday']
                        cal_obj['iud']=ob['iud']
                        if(self.parse_date(ob['start_date'])):
                           cal_obj['start_date']=self.parse_date(ob['start_date'])
                           cal_obj['start']=cal_obj['start_date']
                        if(self.parse_date(ob['start_datetime'])): 
                            cal_obj['start_datetime']=self.parse_date(ob['start_datetime'])
                            cal_obj['start']=cal_obj['start_datetime']
                        if(self.parse_date(ob['end_date'])):
                            cal_obj['stop_date']=self.parse_date(ob['end_date'])
                            cal_obj['stop']=cal_obj['stop_date']
                        if(self.parse_date(ob['end_datetime'])):
                            cal_obj['stop_datetime']=self.parse_date(ob['end_datetime'])
                            cal_obj['stop']=cal_obj['stop_datetime']
                        cal_obj['duration']=ob['duration']
                        cal_obj['description']=ob['description']
                        cal_obj['class']=ob['e_class']
                        cal_obj['location']=ob['location']
                        cal_obj['show_as']=ob['show_as']
                        if(self.parse_date(ob['final_date'])):
                            cal_obj['final_date']=self.parse_date(ob['final_date'])
                        cal_obj['user_id']=ob['u_id']
                        cal_obj['syn']=True
                        cal_obj['ad_val']=ob['uniqueid']
                        
                        deleted=ob['deleted']
                                
                        start= self.parse_date(ob['start_date']) if cal_obj['allday'] else self.parse_date(ob['start_datetime'])
                        if('rule' in ob and ob['rrule']!=None and ob['rrule']!=False and ob['rrule']!=""):
                            cal_obj=calendar_event._rrule_parse(ob['rrule'],cal_obj,start)
                        if(id==False): #create
                            logger.info('In create')
                            cal_id=calendar_event.with_context(from_ex=True).create(cal_obj).id
                            logger.info('After Create:'+str(cal_id))
                        else: #update
                            logger.info('In update')
                            if(deleted==True):
                                cale=calendar_event.browse(id)
                                cale.with_context(ignore_code=True).unlink()
                                logger.info('deleted:'+str(id))    
                            else:
                                if('att' in ob and len(ob['att'])>0):
                                    cale=calendar_event.browse(id)
                                    for att in ob['att']:
                                        if(att['state']=="accepted"):
                                            for ocale in cale.attendee_ids:
                                                if(ocale.email==att['Email']):
                                                    try:
                                                        accepted_ids.append(ocale.id)
                                                    except:
                                                        accepted_ids.append(ocale)
                                                
                                calendar_event.sudo().browse(id).with_context(from_ex=True).write(cal_obj)
                                logger.info('after update:'+str(id))       
                        
                        #for att in ob['att']:
                        #    at={}
                        # #   at['id']=att.id
                        #    at['state']=att.state or ''
                       #     at['email']=att.email or ''
                        #    at['partner_id']=att.partner_id or '-1'
                        #    at['ad_e']=att.ad_e or ''
                         #   satt.append(at)
                       
                        sql+=""
                        #TODO ACK command to ex.
                    else: #bring the values back saying its sync'd this is Odoo out to ex, then mark as done.
                        sql+="update calendar_event set syn=True, iud= '"+ob['iud']+"',  ad_val = '"+ob['uniqueid']+"' where id="+str(ob['id'])+";"
                
                if(len(att_update)>0):
                    sql+="update calendar_attendee set syn=True where id in ("""+str(att_update).replace("[", "").replace("]","")+""" );"""
                if(len(accepted_ids)>0):
                    sql+="update calendar_attendee set state='accepted',syn=True where id in ("""+str(accepted_ids).replace("[", "").replace("]","")+""" );"""
           
                ex['last_cal_number_synced']=data2['n_sync']
                ex['last_cal_from_ex_number_synced']=n_from_ex
                #for ob in data2['OS']:
                 #   if(ob['uniqueid']!=None):
                  #      sql+="update pr1_exchange_contact_c_l_p set syn=True, ad_val = '"+ob['uniqueid']+"' where id="+str(ob['id'])+";"
            if(sql!=""):  
                args=[]
                cr.execute(sql, args)
            errorstr=""
            if('Errors' in data2 and data2['Errors']!="" and data2['Errors']!=False and len(data2['Errors'])>0):
                for error in data2['Errors']:
                    errorstr+=error+"\r\n"
                    if(errorstr.find('Calendar sync not enabled')>-1):
                        raise UserError(_(errorstr))
            if(errorstr!=""):
                ex['lastcal_errorlog']=errorstr
            else:
                ex['lastcal_errorlog']=''

            ex['last_cal_sync_time']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            s_obj.browse(connection.id).write(ex)
            
        except Exception as e:
            raise e
        
        logger.info('sync completed')
        
    def go_syn(self, automatic=False, use_new_cursor=False):
        context=self.env.context
        s_obj=self.env['pr1_exchange_contact.settings']
        s_v_obj=self.env['pr1_exchange_contact.syn_v']
        clu_obj=self.env['pr1_exchange_contact.c_l_u']
        clu_ids=clu_obj.search([]).ids
        
        ids=s_v_obj.search([]).ids
        records=s_v_obj.browse(ids)
        connection=s_obj.get_connection()
        cr=self.env.cr
        opa=[]
        data={}
        if('reset' in context and context['reset']==True):
            data['Param']='resetall'
        else:
            data['Param']='sync'
        data['user_name']=connection.user_name
        data['access_code']=connection.access_code
        cluo=[]
        if(len(clu_ids)>0):
            clus=clu_obj.browse(clu_ids)
            for clu in clus:
                c={}
                if(clu.c_l_id.owner_id.ex_validated==False ):
                    continue
                c['name']=clu.name
                c['c_l_id']=clu.c_l_id.id
                c['active']=True
                c['odoo_user_id']=clu.c_l_id.owner_id.id
                c['syn_e']=clu.c_l_id.owner_id.syn_e
                c['ad_e']=clu.c_l_id.owner_id.ad_e
                c['login']=clu.c_l_id.owner_id.login
                c['o_id']=clu.c_l_id.owner_id.id
                c['c_l_u_id']=clu.id
                c['fglobal']=clu.c_l_id.g_l
                c['ad_val']=clu.ad_val
                cluo.append(c)
        data['clu']=cluo 
        if(len(records)==0 and data['Param']!='resetall'):
            raise UserError(_('Nothing to sync!'))
        for  record in records:
            op={}
            op['id']=record.id
            op['partner_id']=record.partner_id
            op['name']=record.name or ''
            op['comment']=record.comment or ''
            #op['use_parent_address']=record.use_parent_address
            op['street']=record.street or ''
            op['supplier']=record.supplier or 'false'
            op['customer']=record.customer or 'false'
            op['city']=record.city or ''
            op['zip']=record.zip or ''
            op['title']=record.title or ''
            op['company_title']=record.company_title or ''
            op['function']=record.function or ''
            op['phone']=record.phone or ''
            op['type']=record.type or ''
            op['email']=record.email or ''
            op['website']=record.website or ''
            op['fax']=''#record.fax or ''
            op['street2']=record.street2 or ''
            op['country_name']=record.country_name or ''
            op['parent_id']=record.parent_id or ''
            op['mobile']=record.mobile or ''
            if(record.birthdate!=False):
                op['birthdate']=record.birthdate
            op['is_company']=record.is_company
            op['state_name']=record.state_name or ''
            op['company_name']=record.company_name or ''
            op['company_phone']=record.company_phone or ''
            op['c_street']=record.c_street or ''
            op['c_street2']=record.c_street2 or ''
            op['c_city']=record.c_city or ''
            op['c_zip']=record.c_zip or ''
            op['c_state_name']=record.c_state_name or ''
            op['c_country_name']=record.c_country_name or ''
            op['ad_val']=record.ad_val  or ''
            op['c_list_name']=record.c_list_name or ''
            op['c_list_global']=record.c_list_global
            op['c_ad_id']=record.c_ad_id
            op['o_id']=record.o_id 
            op['ad_e']=record.ad_e 
            op['clp_active']=record.clp_active 
            op['syn']=record.syn
            op['c_l_i_d']=record.c_l_i_d
            opa.append(op)
        data['p']=opa
        req = Request(connection.url)
        req.add_header('Content-Type', 'application/json')
        try:
            params = json.dumps(data).encode('utf8')
            req = Request(connection.url, data=params)
            req.add_header('Content-Type', 'application/json')
            response = urlopen(req)
            response_data=response.read().decode('utf8')
            data2 = json.loads(response_data) 
            ex={}
            sql=""
            if('suc' in data2 and data2['suc']==True):
                for ob in data2['CL']:
                    sql+="update pr1_exchange_contact_c_l_u set ad_val = '"+ob['uniqueid']+"' where id="+str(ob['CID'])+";"
                    
                ex['sync_partner_count']=data2['TotalContacts']
                ex['sync_user_count']=data2['TotalUsers']
                ex['user_limit']=data2['UserLimit']
                ex['contact_limit']=data2['ContactLimit']
                ex['last_number_synced']=data2['n_sync']
               
                for ob in data2['OS']:
                    if(ob['deleted']==True):
                        sql+="delete from pr1_exchange_contact_c_l_p where id="+str(ob['id'])+";"
                    if(ob['uniqueid']!=None):
                        sql+="update pr1_exchange_contact_c_l_p set syn=True, ad_val = '"+ob['uniqueid']+"' where id="+str(ob['id'])+";"
            if(sql!=""):  
                args=[]
                cr.execute(sql, args)
            errorstr=""
            if('Errors' in data2 and data2['Errors']!="" and data2['Errors']!=False and len(data2['Errors'])>0):
                for error in data2['Errors']:
                    errorstr+=error+"\r\n"
            if(errorstr!=""):
                ex['lasterrorlog']=errorstr
            else:
                ex['lasterrorlog']=''
            

            ex['last_sync_time']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            s_obj.browse(connection.id).write(ex)
            if(errorstr!="" and 'reset' in context and context['reset']==True):
                #raise osv.except_osv('Error', errorstr)
                raise UserError(_(errorstr))
            
            
            if('reset' in context and context['reset']==True):
                sql2="update calendar_event set ad_val='', syn=False"
                sql="delete from pr1_exchange_contact_c_l_u; delete from pr1_exchange_contact_c_l_p; delete from pr1_exchange_contact_c_l;"
                args=[]
                self.env.cr.execute(sql, args)
                self.env.cr.execute(sql2, args)
        except Exception as e:
            raise e
        return True
            
   
   
syn()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
