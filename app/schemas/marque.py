# ── Marque ────────────────────────────────────────────────────
from marshmallow import Schema, fields, EXCLUDE
from marshmallow.validate import Length


class MarqueSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id       = fields.Int(dump_only=True)
    nom      = fields.Str(required=True, validate=Length(min=1, max=100))
    url_logo = fields.Str(allow_none=True, validate=Length(max=500))