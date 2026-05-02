# ── Modele ────────────────────────────────────────────────────
from marshmallow import Schema, fields, EXCLUDE
from marshmallow.validate import Length
from .marque import MarqueSchema

class ModeleSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id           = fields.Int(dump_only=True)
    nom          = fields.Str(required=True, validate=Length(min=1, max=100))
    type_machine = fields.Str(required=True, validate=Length(min=1, max=100))
    marque_id    = fields.Int(required=True, load_only=True)
    marque       = fields.Nested(lambda: MarqueSchema(), dump_only=True)
    label        = fields.Str(dump_only=True)


class ModeleSimpleSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id           = fields.Int(dump_only=True)
    nom          = fields.Str(dump_only=True)
    type_machine = fields.Str(dump_only=True)
    marque_id    = fields.Int(dump_only=True)
    label        = fields.Str(dump_only=True)