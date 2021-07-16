from openerp import models, fields, api
from openerp.exceptions import except_orm



class report_disposisi(models.TransientModel):
    _name = 'report.dispo'

    dispo = fields.Many2one('disposisi.masuk','Disposisi', domain="[('state','!=','draft')]")

    @api.multi
    def genertae(self):
        dispo = self.env['disposisi.masuk']
        sql = "delete from hasil_laporan_disposisi"
        self._cr.execute(sql)
        xxx = False
        yy = 0
        dis_tr = False
        dis_app = dispo.sudo().search([('source','=',self.dispo.name)])
        dis_tr = True
        dispo_create = False
        while dis_tr == True :
            dis_tr = False
            cek_source = dis_app
            dis_app = dispo.sudo().search([('source','=','---')])
            for cek in cek_source :
                #import pdb;pdb.set_trace()
                ids1 = ""
                ids2 = ""
                ids3 = ""
                ids4 = ""
                for job in cek.user_ids1 :
                    ids1 = ids1 + job.name
                for job in cek.user_ids2 :
                    ids2 = ids1 + job.name
                for job in cek.user_ids3 :
                    ids3 = ids1 + job.name
                for job in cek.user_ids4 :
                    ids4 = ids1 + job.name
                dispo_create = self.env['hasil_laporan.disposisi'].create(                  {'name':cek.name,
                                        'jenis' : 'Disposisi',
                                        'ditujukan':ids1,
                                        'ditujukan_info':ids2,
                                        'ditujukan_tanggapan':ids3,
                                        'ditujukan_file':ids4,
                                        'pembuat': cek.user_id1.name,
                                        'date': cek.date,
                                        'note': cek.note,
                                        'source_document': cek.source,
                                        'state' : cek.state
                                        })
                dis_app = dis_app + dispo.sudo().search([('source','=',cek.name)])
                if dis_app :
                    dis_tr = True
        if dispo_create != False :
            ctx = dict(self.env.context)
            return {
                'name': 'Report Disposisi',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'hasil_laporan.disposisi',
                'res_id': dispo_create.id,
                'type': 'ir.actions.act_window',
                'context': ctx,
            }

