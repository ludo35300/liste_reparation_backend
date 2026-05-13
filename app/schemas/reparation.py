from marshmallow import Schema, fields, EXCLUDE
from marshmallow.validate import Length, OneOf
from app.constantes.reparations import STATUTS_REPARATION_VALIDES
from app.schemas.machine import MachineSchema
from app.schemas.piece import PieceChangeeSchema



# ── Reparation ────────────────────────────────────────────────
class ReparationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id              = fields.Int(dump_only=True)
    machine_id      = fields.Int(required=True)
    machine         = fields.Nested(MachineSchema, dump_only=True)
    technicien      = fields.Str(load_default='', validate=Length(max=100))
    technicien_id   = fields.Int(load_default=None, allow_none=True)
    date_reparation = fields.Date(required=True, format='iso')
    date_cloture    = fields.Date(load_default=None, allow_none=True, format='iso') 
    statut          = fields.Str(load_default='en_reparation', validate=OneOf(STATUTS_REPARATION_VALIDES))
    description     = fields.Str(load_default='')
    created_at      = fields.DateTime(dump_only=True)
    pieces          = fields.List(fields.Nested(PieceChangeeSchema), load_default=[])
    actions         = fields.List(fields.Nested('ReparationActionSchema'), dump_only=True, load_default=[])