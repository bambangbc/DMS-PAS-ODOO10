from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class laporan_disposisi(models.Model):
    _name = "hasil_laporan.disposisi"
    _description = "hasil laporan disposisi"

    name = fields.Char("Nomor")
    jenis = fields.Char("Jenis Surat")
    ditujukan = fields.Char("Ditujukan Untuk (Action)")
    ditujukan_tanggapan = fields.Char('Ditujukan Untuk (Tanggalpan)')
    ditujukan_info = fields.Char('Ditujukan Untuk (Info)')
    ditujukan_file = fields.Char('Ditujukan Untuk (File)')
    pembuat = fields.Char("Pembuat")
    date = fields.Datetime("Tanggal")
    note = fields.Html("Note")
    source_document = fields.Char("Source Document")
    state = fields.Char("State")