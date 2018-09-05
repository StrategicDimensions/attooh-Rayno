# -*- coding: utf-8 -*-
#**************************************************************************
#* PR1 CONFIDENTIAL - Copyrighted Code - Do not re-use. Do not distribute.
#* __________________
#*  [2017] PR1 (pr1.xyz) -  All Rights Reserved. 
#* NOTICE:  All information contained herein is, and remains the property of PR1 and its suppliers, if any.  The intellectual and technical concepts contained herein are proprietary to PR1.xyz and its holding company and are protected by trade secret or copyright law. Dissemination of this information, copying of the concepts used or reproduction of any part of this material in any format is strictly forbidden unless prior written permission is obtained from PR1.xyz.
#**************************************************************************
from odoo import api, fields, models, modules, tools, _
class syn_c(models.Model):
    _name = "pr1_exchange_contact.syn_c"
    _auto = False
    id= fields.Integer('ID', readonly=True)
    name= fields.Char('Name', readonly=True)
    start_date= fields.Datetime('start_date', readonly=True)
    stop_date= fields.Datetime('stop_date', readonly=True)
    end_date= fields.Datetime('end_date', readonly=True)
    cal_active= fields.Boolean('active', readonly=True)
    start_datetime= fields.Datetime('start_Datetime', readonly=True)
    end_datetime= fields.Datetime('end_Datetime', readonly=True)
    rrule= fields.Char('city', readonly=True,size=256)
    final_date= fields.Datetime('final_date', readonly=True)
    description= fields.Text('description', readonly=True)
    allday= fields.Boolean('allday', readonly=True)
    show_as= fields.Char('show_as', readonly=True)
    location= fields.Char('location', readonly=True)
    interval= fields.Integer('interval', readonly=True)
    duration_minutes= fields.Integer('duration_minutes', readonly=True)
    duration= fields.Integer('duration', readonly=True)
    att= fields.One2many('pr1_exchange_contact.syn_a', 'event_id', 'att')
    login=fields.Char('login',readonly=True)        
    ex_validated= fields.Boolean('ex_validated', readonly=True)
    ad_e=fields.Char('ad_e',readonly=True)
    user_id= fields.Integer('user_id', readonly=True)              
    syn_e= fields.Boolean('syn_e', readonly=True)
    ad_val=fields.Char('AD VAL',size=256,readonly=True)
    iud=fields.Char('IUD',size=100,readonly=True)
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
