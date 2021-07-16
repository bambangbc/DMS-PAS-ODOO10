from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, tools


class month_of_year(models.Model):
    _name = 'month.of.year'
    _description = 'Month of Year'

    name = fields.Char('Month of Year', required=True)
    year = fields.Integer('Year', required=True)
    month = fields.Integer('Month', required=True)
    date_from = fields.Date('From Date', required=True)
    date_to = fields.Date('To Date', required=True)
    date_cutoff = fields.Date('Cutoff Date', required=True)

    @api.onchange('year', 'month')
    def pick_month(self):
        month = {
            0: "",
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec"
        }[self.month]

        self.name = month + "-" + str(self.year - 2000)

    @api.constrains('year', 'month')
    def _check_unique_name(self):
        if self.search_count(['&', ('year', '=', self.year), ('month', '=', self.month)]) != 1:
            raise ValidationError("Month of year already exists!")