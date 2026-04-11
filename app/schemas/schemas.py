from marshmallow import Schema, fields, post_load, EXCLUDE

# ── PieceRef ──────────────────────────────────────────────────
class PieceRefSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id          = fields.Int(dump_only=True)
    ref_piece   = fields.Str(required=True)
    designation = fields.Str(load_default='')

# ── PieceChangee ──────────────────────────────────────────────
class PieceChangeeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id          = fields.Int(dump_only=True)
    piece_ref_id = fields.Int(dump_only=True)

    # En entrée (load) : reçus depuis Angular
    ref_piece   = fields.Str(required=True)
    designation = fields.Str(load_default='')
    quantite    = fields.Int(load_default=1)
    is_new      = fields.Bool(load_default=False)  # non persisté

    # En sortie (dump) : lus depuis le @property via piece_ref
    # Marshmallow lit les @property automatiquement sur l'objet SQLAlchemy

# ── MachineTypeRef simple (liste) ────────────────────────────
class MachineTypeRefSimpleSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id           = fields.Int(dump_only=True)
    marque       = fields.Str()
    modele       = fields.Str()
    type_machine = fields.Str()
    url_logo     = fields.Str(allow_none=True)
    label        = fields.Str(dump_only=True)   # @property

# ── MachineTypeRef complet (avec pièces) ─────────────────────
class MachineTypeRefSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id           = fields.Int(dump_only=True)
    marque       = fields.Str(required=True)
    modele       = fields.Str(required=True)
    type_machine = fields.Str(required=True)
    url_logo     = fields.Str(allow_none=True)
    label        = fields.Str(dump_only=True)
    pieces       = fields.List(fields.Nested(PieceRefSchema), dump_only=True)

# ── Reparation ────────────────────────────────────────────────
class ReparationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # dump + load
    id              = fields.Int(dump_only=True)
    numero_serie    = fields.Str(required=True)
    machine_type    = fields.Str(required=True)
    technicien      = fields.Str(load_default='')
    date_reparation = fields.Str(required=True)   # JJ/MM/AAAA
    notes           = fields.Str(load_default='')
    created_at      = fields.DateTime(dump_only=True)
    pieces          = fields.List(fields.Nested(PieceChangeeSchema), load_default=[])