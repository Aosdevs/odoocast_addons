import re

from odoo import http
from odoo.http import request

from odoo.addons.auth_signup.controllers.main import AuthSignupHome


REQUIRED_FIELDS = [
    "l10n_br_cnpj_cpf",
    "company_type",
]


#  Returns unformatted and formatted cpf
def get_cpf_formats(value):
    numbers = re.sub("[^0-9]", "", value)
    if len(numbers) <= 11:
        numbers = numbers.zfill(11)
        formatted = (
            f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:9]}-{numbers[9:]}"
        )
    elif len(numbers) <= 14:
        numbers.zfill(14)
        formatted = f"{numbers[:2]}.{numbers[2:5]}.{numbers[5:8]}/{numbers[8:12]}-{numbers[12:]}"
    else:
        formatted = numbers
    return numbers, formatted


class CustomLoginController(http.Controller):
    @http.route(
        "/check_existing_cnpj_cpf", type="json", auth="public", website=True
    )
    def check_existing_cnpj_cpf(self, **kw):
        unformatted, formatted = get_cpf_formats((kw.get("cpf")))
        res = (
            request.env["res.users"]
            .sudo()
            .search(
                [
                    (
                        "partner_id.l10n_br_cnpj_cpf",
                        "in",
                        (unformatted, formatted),
                    ),
                ],
                limit=1,
            )
        )
        return {"login": res.login}

    @http.route(
        "/get_company_info", type="json", auth="public", website=True
    )
    def get_company_info(self, **kw):
        unformatted, formatted = get_cpf_formats((kw.get("cnpj")))
        res = (
            request.env["res.partner"]
            .sudo()
            .search(
                [
                    (
                        "l10n_br_cnpj_cpf",
                        "in",
                        (unformatted, formatted),
                    ),
                    ('is_company', '=', True)
                ],
                limit=1,
            )
        )
        return {
            'ok': True if res else False,
            'zip': res.zip,
            'street2': res.street2,
            'l10n_br_number': res.l10n_br_number
        }


class CustomWebSignup(AuthSignupHome):
    def get_partner_token(self, vals):
        unformatted_cpf, formatted_cpf = get_cpf_formats(
            (vals.get("l10n_br_cnpj_cpf"))
        )
        partner_values = {
            k: int(v) if k[-3:] == "_id" else v
            for (k, v) in request.params.items()
            if k
            in REQUIRED_FIELDS
            + [
                "name",
                "phone",
                "street2",
                "l10n_br_number",
                "l10n_br_district",
                "input_parent_cnpj_cpf",
                "office_role",
                "department",
            ]
        }
        parent_cnpj = (
            "input_parent_cnpj_cpf" in partner_values
            and partner_values.pop("input_parent_cnpj_cpf")
        )
        if parent_cnpj and partner_values.get("company_type") == "person":
            parent = (
                request.env["res.partner"]
                .sudo()
                .search(
                    [
                        (
                            "l10n_br_cnpj_cpf",
                            "in",
                            get_cpf_formats(parent_cnpj),
                        ),
                    ],
                    limit=1,
                )
            )
            if parent:
                partner_values.update({"parent_id": parent.id})
        partner = (
            request.env["res.partner"]
            .sudo()
            .search(
                [
                    (
                        "email",
                        "=",
                        vals.get('login'),
                    ),
                ],
                limit=1,
            )
        )

        partner_values.update({"l10n_br_cnpj_cpf": formatted_cpf})
        if partner:
            partner.write(partner_values)
        else:
            partner = request.env["res.partner"].sudo().create(partner_values)
        partner.signup_prepare()
        return partner.signup_token

    def get_auth_signup_qcontext(self):
        res = super(CustomWebSignup, self).get_auth_signup_qcontext()
        res.update(
            {
                k: v
                for (k, v) in request.params.items()
                if k
                in REQUIRED_FIELDS
                + ["phone", "street2", "input_parent_cnpj_cpf"]
            }
        )
        if "error" not in res and request.httprequest.method == "POST":
            unformatted_cpf, formatted_cpf = get_cpf_formats(
                (res.get("l10n_br_cnpj_cpf"))
            )
            user = (
                request.env["res.users"]
                .sudo()
                .search(
                    [
                        (
                            "partner_id.l10n_br_cnpj_cpf",
                            "in",
                            (unformatted_cpf, formatted_cpf),
                        ),
                    ],
                    limit=1,
                )
            )
            if user:
                res.update(
                    {
                        "error": "Já existe um usuário cadastrado para este CPF/CNPJ!"
                    }
                )
            elif not all(res.get(field) for field in REQUIRED_FIELDS):
                res.update(
                    {
                        "error": "Alguns campos obrigatórios não foram preenchidos!"
                    }
                )
            else:
                res.update({"token": self.get_partner_token(res)})
        return res

    @http.route()
    def web_auth_signup(self, *args, **kw):
        res = super(CustomWebSignup, self).web_auth_signup(*args, **kw)
        if request.session.uid:
            return res
        ctx = res.qcontext
        countries = request.env["res.country"].sudo().search([])
        default_country = countries.filtered(
            lambda x: x.l10n_br_ibge_code == "1058"
        )
        ctx.update(
            {
                "alert_msg": [res.qcontext.get("error")],
                "countries": countries,
                "default_country": default_country and default_country[0].id,
                "default_cpf": kw.get("default_cpf", ""),
            }
        )
        return request.render(res.template, ctx)
