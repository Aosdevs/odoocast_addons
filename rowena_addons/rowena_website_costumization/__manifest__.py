{  # pylint: disable=C8101,C8103,C7902
    "name": "Rowena Website Costumization",
    "description": """Adiciona costumizações no layout do website""",
    "author": "Trustcode",
    "category": "website",
    "version": "14.0.0.2",
    "contributors": ["Jonatas Biazus <jonatasbiazusct@gmail.com>"],
    "depends": ["website_sale", "hidden_delivery_amount", "sale_management", "l10n_br_sale"],
    "data": [
        "views/checkout_custom.xml",
        "views/product.xml",
        "views/website_template.xml",
        "reports/sale_order_report_rowena.xml",
        "views/external_layout_header_custom_rowena.xml",
        "views/sale_order.xml",
    ],
}
