# -*- encoding: utf-8 -*-


{
    "license":"Other proprietary",
    "name" : "Office 365/Exchange Calendar/Contact/Email Sync - PR1",
    "version" : "1",
    "author" : "PR1",
    "category" : "Extra Tools",
    "description": """Synchronize your calendar and contact and emails with exchange/office365.
    This module allows the creation of user contact lists and syncronizes your Odoo calendar to the exchange calendar.
    Users can add/remove contacts to their contact lists. 
    All sent emails from within Odoo will be logged into your exchange/office sent items box.
    The contacts will migrate into Microsoft Exchange/Office 365 as a contact within you contact list in exchange. 
    The contacts will be visible in all views such as outlook and mobile phones.
    All Odoo meetings will be visible in the exchange calendar, including on mobile phones, outlook webmail etc.
    Supports recurring meetings. Please visit http://pr1.xyz/page/exchange-office-365-sync for more info.
    
    """,
    'website':'https://pr1.xyz/page/exchange-office-365-sync',
    'price':10,
    'currency':'EUR',
    'depends' : ["base",'crm'],

    'data' : [
                  'security/t_m_s.xml',
                  'security/ir.model.access.csv',  
                  'views/a_d_v.xml',
                  'views/c_l_p_v.xml',
                  'views/c_l_u_v.xml',
                  'views/c_l_v.xml',
                  'views/res_users_view.xml',
                  'views/res_partner_view.xml',
                  'views/syn.xml',
                  'views/settings.xml',
                  'views/menu.xml',
                  'data/view_init.xml',   
    
                  ],
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
