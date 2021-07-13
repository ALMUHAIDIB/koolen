{
	'name': "Avaya VOIP",
	"summary" : "Avaya Voip Integration",
	"description": "Avaya Voip Integration",
	"category": "Sales",
	"author": "LBM",
	"version": "1.0",
	'support': 'cdoquicksolution@gmail.com',
	'images': ['static/description/avaya.png'],
	"depends": [
		"base",
		"mail",
		'contacts',
		"web",
	],
	"data": [
		'security/ir.model.access.csv',
		'views/assets.xml',
		'views/res_config_setting_views.xml',
		'views/res_users_views.xml',		
		'views/history.xml',
	],
	"qweb": [
		'static/src/xml/cstm_dialing_panel.xml',
		'static/src/xml/field_phone.xml',
	],
	'installable': True,
	'application': True,
	'price': 499.00,
	'currency': 'EUR',
	'license': 'OPL-1',
}