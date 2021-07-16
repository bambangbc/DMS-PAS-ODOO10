# -*- coding: utf-8 -*-

from odoo import models, fields, tools


class FleetRentalReport(models.Model):
    _name = "report.fleet.charter"
    _description = "Aircraft Charter Analysis"
    _auto = False

    name = fields.Char(string="Name")
    customer_id = fields.Many2one('res.partner')
    vehicle_id = fields.Many2one('fleet.vehicle')
    craft_brand = fields.Char(string="Aircraft Brand")
    craft_color = fields.Char(string="Aircraft Color")
    cost = fields.Float(string="Charter Cost")
    rent_start_date = fields.Date(string="Charter Start Date")
    rent_end_date = fields.Date(string="Charter End Date")
    state = fields.Selection([('draft', 'Draft'), ('running', 'Running'), ('cancel', 'Cancel'),
                              ('checking', 'Checking'), ('done', 'Done')], string="State")
    cost_frequency = fields.Selection([('no', 'No'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'),
                                       ('yearly', 'Yearly')], string="Recurring Cost Frequency")
    total = fields.Float(string="Total(Tools)")
    tools_missing_cost = fields.Float(string="Tools missing cost")
    damage_cost = fields.Float(string="Damage cost")
    damage_cost_sub = fields.Float(string="Damage cost")
    total_cost = fields.Float(string="Total cost")

    _order = 'name desc'

    def _select(self):
        select_str = """
             SELECT
                    (select 1 ) AS nbr,
                    t.id as id,
                    t.name as name,
                    t.craft_brand as craft_brand,
                    t.customer_id as customer_id,
                    t.vehicle_id as vehicle_id,
                    t.craft_color as craft_color,
                    t.cost as cost,
                    t.rent_start_date as rent_start_date,
                    t.rent_end_date as rent_end_date,
                    t.state as state,
                    t.cost_frequency as cost_frequency,
                    t.total as total,
                    t.tools_missing_cost as tools_missing_cost,
                    t.damage_cost as damage_cost,
                    t.damage_cost_sub as damage_cost_sub,
                    t.total_cost as total_cost
        """
        return select_str

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    t.id,
                    name,
                    craft_brand,
                    customer_id,
                    vehicle_id,
                    craft_color,
                    cost,
                    rent_start_date,
                    rent_end_date,
                    state,
                    cost_frequency,
                    total,
                    tools_missing_cost,
                    damage_cost,
                    damage_cost_sub,
                    total_cost
        """
        return group_by_str

    def init(self):
        tools.sql.drop_view_if_exists(self._cr, 'report_fleet_charter')
        self._cr.execute("""
            CREATE view report_fleet_charter as
              %s
              FROM craft_charter_contract t
                %s
        """ % (self._select(), self._group_by()))
