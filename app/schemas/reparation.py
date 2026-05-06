from marshmallow import Schema, fields, EXCLUDE
from marshmallow.validate import Length
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
    description     = fields.Str(load_default='')
    created_at      = fields.DateTime(dump_only=True)
    pieces          = fields.List(fields.Nested(PieceChangeeSchema), load_default=[])