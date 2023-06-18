{  # pylint: disable=C8101,C8103
    "name": "Website Custom Login",
    "summary": "Change the authentication on the ecommerce",
    "version": "14.0.1.1.0",
    "category": "website",
    "author": "Trustcode",
    "website": "http://www.trustcode.com.br",
    "contributors": [
        "Danimar Ribeiro <danimaribeiro@gmail.com>",
        "Felipe Paloschi <paloschi.eca@gmail.com>",
    ],
    "depends": [
        "l10n_br_website_sale",
    ],
    "data": [
        "views/signup.xml",
        "views/res_partner.xml",
    ],
    "qweb": [
        "static/src/xml/templates.xml",
    ],
}
