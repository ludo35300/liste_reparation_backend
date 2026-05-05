from marshmallow import Schema, fields, EXCLUDE
from marshmallow.validate import Length, Range

# ── PieceRef ──────────────────────────────────────────────────
class PieceRefSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id          = fields.Int(dump_only=True)
    ref_piece   = fields.Str(required=True, validate=Length(min=1, max=100))
    designation = fields.Str(load_default='', validate=Length(max=200))
    marque_id   = fields.Int(required=True, load_only=True)
    
# ── PieceRefUpdate ──────────────────────────────────────────────
class PieceRefUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    ref_piece   = fields.Str(required=True, validate=Length(min=1, max=100))
    designation = fields.Str(load_default='', validate=Length(max=200))

# ── PieceChangee ──────────────────────────────────────────────
class PieceChangeeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id           = fields.Int(dump_only=True)
    piece_ref_id = fields.Int(dump_only=True)
    ref_piece    = fields.Str(required=True, validate=Length(min=1, max=100))
    designation  = fields.Str(load_default='')
    quantite     = fields.Int(load_default=1, validate=Range(
                        min=1, error="La quantité doit être ≥ 1"
                   ))
    is_new       = fields.Bool(load_default=False)