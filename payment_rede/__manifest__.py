# pylint: skip-file
{
    "name": "Método de Pagamento ASAAS",
    "summary": "Payment Acquirer: ASAAS",
    "category": "Accounting",
    "version": "14.0.1.0.0",
    "author": "Code 137",
    "website": "http://www.code137.com.br",
    "contributors": [
        "Felipe Paloschi <paloschi.eca@gmail.com>",
    ],
    "depends": ["payment", "website_sale"],
    "data": [
        "views/asaas.xml",
        "data/data.xml",
        "views/res_partner.xml",
        "views/account_move.xml",
        "views/templates.xml",
        "views/res_config_settings.xml",
    ],
    "application": True,
}
