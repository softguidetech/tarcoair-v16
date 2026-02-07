# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_airline_invoice = fields.Boolean(string="Airline Invoice", default=False, index=True)

    airline_total_basic_fare = fields.Monetary(
        string="Basic Fare Total",
        currency_field="currency_id",
        compute="_compute_airline_totals",
        store=False,
    )
    airline_total_vat = fields.Monetary(
        string="VAT Total",
        currency_field="currency_id",
        compute="_compute_airline_totals",
        store=False,
    )
    airline_total_taxes = fields.Monetary(
        string="Taxes Total",
        currency_field="currency_id",
        compute="_compute_airline_totals",
        store=False,
    )
    airline_total_baq_protect = fields.Monetary(
        string="BAQ/Protect Total",
        currency_field="currency_id",
        compute="_compute_airline_totals",
        store=False,
    )
    airline_total_bill_diff = fields.Monetary(
        string="Bill Diff Total",
        currency_field="currency_id",
        compute="_compute_airline_totals",
        store=False,
    )
    airline_total_ins_premium = fields.Monetary(
        string="Ins. Premium Total",
        currency_field="currency_id",
        compute="_compute_airline_totals",
        store=False,
    )
    airline_grand_total = fields.Monetary(
        string="Airline Grand Total",
        currency_field="currency_id",
        compute="_compute_airline_totals",
        store=False,
    )

    # Fields to track which columns have non-zero values (for view visibility)
    airline_has_basic_fare = fields.Boolean(
        string="Has Basic Fare",
        compute="_compute_airline_has_fields",
        store=False,
    )
    airline_has_vat = fields.Boolean(
        string="Has VAT",
        compute="_compute_airline_has_fields",
        store=False,
    )
    airline_has_taxes = fields.Boolean(
        string="Has Taxes",
        compute="_compute_airline_has_fields",
        store=False,
    )
    airline_has_baq_protect = fields.Boolean(
        string="Has BAQ/Protect",
        compute="_compute_airline_has_fields",
        store=False,
    )
    airline_has_bill_diff = fields.Boolean(
        string="Has Bill Diff",
        compute="_compute_airline_has_fields",
        store=False,
    )
    airline_has_ins_premium = fields.Boolean(
        string="Has Ins. Premium",
        compute="_compute_airline_has_fields",
        store=False,
    )

    @api.depends(
        "is_airline_invoice",
        "invoice_line_ids.display_type",
        "invoice_line_ids.air_basic_fare",
        "invoice_line_ids.air_vat_amount",
        "invoice_line_ids.air_taxes_amount",
        "invoice_line_ids.air_baq_protect",
        "invoice_line_ids.air_bill_diff",
        "invoice_line_ids.air_ins_premium",
    )
    def _compute_airline_has_fields(self):
        """Compute which airline fields have non-zero values"""
        for move in self:
            if not move.is_airline_invoice or not move.is_invoice(include_receipts=False):
                move.airline_has_basic_fare = False
                move.airline_has_vat = False
                move.airline_has_taxes = False
                move.airline_has_baq_protect = False
                move.airline_has_bill_diff = False
                move.airline_has_ins_premium = False
                continue

            lines = move.invoice_line_ids.filtered(lambda l: l.display_type in (False, "product"))
            move.airline_has_basic_fare = any((l.air_basic_fare or 0) != 0 for l in lines)
            move.airline_has_vat = any((l.air_vat_amount or 0) != 0 for l in lines)
            move.airline_has_taxes = any((l.air_taxes_amount or 0) != 0 for l in lines)
            move.airline_has_baq_protect = any((l.air_baq_protect or 0) != 0 for l in lines)
            move.airline_has_bill_diff = any((l.air_bill_diff or 0) != 0 for l in lines)
            move.airline_has_ins_premium = any((l.air_ins_premium or 0) != 0 for l in lines)

    @api.depends(
        "is_airline_invoice",
        "invoice_line_ids.display_type",
        "invoice_line_ids.air_ticket_no",
        "invoice_line_ids.air_pax_name",
        "invoice_line_ids.air_basic_fare",
        "invoice_line_ids.air_vat_amount",
        "invoice_line_ids.air_taxes_amount",
        "invoice_line_ids.air_baq_protect",
        "invoice_line_ids.air_bill_diff",
        "invoice_line_ids.air_ins_premium",
    )
    def _compute_airline_totals(self):
        for move in self:
            if not move.is_airline_invoice or not move.is_invoice(include_receipts=False):
                move.airline_total_basic_fare = 0.0
                move.airline_total_vat = 0.0
                move.airline_total_taxes = 0.0
                move.airline_total_baq_protect = 0.0
                move.airline_total_bill_diff = 0.0
                move.airline_total_ins_premium = 0.0
                move.airline_grand_total = 0.0
                continue

            # In Odoo 16 invoice product lines usually have display_type = 'product'.
            # Sections/notes have 'line_section'/'line_note' and must be excluded.
            lines = move.invoice_line_ids.filtered(lambda l: l.display_type in (False, "product"))
            move.airline_total_basic_fare = sum(lines.mapped("air_basic_fare"))
            move.airline_total_vat = sum(lines.mapped("air_vat_amount"))
            move.airline_total_taxes = sum(lines.mapped("air_taxes_amount"))
            move.airline_total_baq_protect = sum(lines.mapped("air_baq_protect"))
            move.airline_total_bill_diff = sum(lines.mapped("air_bill_diff"))
            move.airline_total_ins_premium = sum(lines.mapped("air_ins_premium"))
            move.airline_grand_total = (
                move.airline_total_basic_fare
                + move.airline_total_vat
                + move.airline_total_taxes
                + move.airline_total_baq_protect
                + move.airline_total_bill_diff
                + move.airline_total_ins_premium
            )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_airline_invoice = fields.Boolean(
        string="Is Airline Invoice",
        related="move_id.is_airline_invoice",
        readonly=True,
        store=False,
    )

    # Related fields to access move-level computed fields for visibility
    airline_has_basic_fare = fields.Boolean(
        string="Move Has Basic Fare",
        related="move_id.airline_has_basic_fare",
        readonly=True,
        store=False,
    )
    airline_has_vat = fields.Boolean(
        string="Move Has VAT",
        related="move_id.airline_has_vat",
        readonly=True,
        store=False,
    )
    airline_has_taxes = fields.Boolean(
        string="Move Has Taxes",
        related="move_id.airline_has_taxes",
        readonly=True,
        store=False,
    )
    airline_has_baq_protect = fields.Boolean(
        string="Move Has BAQ/Protect",
        related="move_id.airline_has_baq_protect",
        readonly=True,
        store=False,
    )
    airline_has_bill_diff = fields.Boolean(
        string="Move Has Bill Diff",
        related="move_id.airline_has_bill_diff",
        readonly=True,
        store=False,
    )
    airline_has_ins_premium = fields.Boolean(
        string="Move Has Ins. Premium",
        related="move_id.airline_has_ins_premium",
        readonly=True,
        store=False,
    )

    air_ticket_no = fields.Char(string="Ticket No")
    air_pax_name = fields.Char(string="Pax Name")

    air_basic_fare = fields.Monetary(string="Basic Fare", currency_field="currency_id")
    air_vat_amount = fields.Monetary(string="VAT", currency_field="currency_id")
    air_taxes_amount = fields.Monetary(string="Taxes", currency_field="currency_id")
    air_baq_protect = fields.Monetary(string="BAQ/Protect", currency_field="currency_id")
    air_bill_diff = fields.Monetary(string="Bill Diff", currency_field="currency_id")
    air_ins_premium = fields.Monetary(string="Ins. Premium", currency_field="currency_id")

    air_total_amount = fields.Monetary(
        string="Total",
        currency_field="currency_id",
        compute="_compute_air_total_amount",
        store=False,
    )

    # Fields to track if individual values are non-zero (for view visibility)
    air_has_basic_fare = fields.Boolean(
        string="Has Basic Fare",
        compute="_compute_air_has_fields",
        store=False,
    )
    air_has_vat = fields.Boolean(
        string="Has VAT",
        compute="_compute_air_has_fields",
        store=False,
    )
    air_has_taxes = fields.Boolean(
        string="Has Taxes",
        compute="_compute_air_has_fields",
        store=False,
    )
    air_has_baq_protect = fields.Boolean(
        string="Has BAQ/Protect",
        compute="_compute_air_has_fields",
        store=False,
    )
    air_has_bill_diff = fields.Boolean(
        string="Has Bill Diff",
        compute="_compute_air_has_fields",
        store=False,
    )
    air_has_ins_premium = fields.Boolean(
        string="Has Ins. Premium",
        compute="_compute_air_has_fields",
        store=False,
    )

    @api.depends(
        "air_basic_fare",
        "air_vat_amount",
        "air_taxes_amount",
        "air_baq_protect",
        "air_bill_diff",
        "air_ins_premium",
        "display_type",
        "move_id.is_airline_invoice",
    )
    def _compute_air_has_fields(self):
        """Compute which airline fields have non-zero values for this line"""
        for line in self:
            if line.display_type or not line.move_id.is_airline_invoice:
                line.air_has_basic_fare = False
                line.air_has_vat = False
                line.air_has_taxes = False
                line.air_has_baq_protect = False
                line.air_has_bill_diff = False
                line.air_has_ins_premium = False
                continue
            line.air_has_basic_fare = (line.air_basic_fare or 0) != 0
            line.air_has_vat = (line.air_vat_amount or 0) != 0
            line.air_has_taxes = (line.air_taxes_amount or 0) != 0
            line.air_has_baq_protect = (line.air_baq_protect or 0) != 0
            line.air_has_bill_diff = (line.air_bill_diff or 0) != 0
            line.air_has_ins_premium = (line.air_ins_premium or 0) != 0

    @api.depends(
        "air_basic_fare",
        "air_vat_amount",
        "air_taxes_amount",
        "air_baq_protect",
        "air_bill_diff",
        "air_ins_premium",
        "display_type",
        "move_id.is_airline_invoice",
    )
    def _compute_air_total_amount(self):
        for line in self:
            if line.display_type or not line.move_id.is_airline_invoice:
                line.air_total_amount = 0.0
                continue
            line.air_total_amount = (
                (line.air_basic_fare or 0.0)
                + (line.air_vat_amount or 0.0)
                + (line.air_taxes_amount or 0.0)
                + (line.air_baq_protect or 0.0)
                + (line.air_bill_diff or 0.0)
                + (line.air_ins_premium or 0.0)
            )


