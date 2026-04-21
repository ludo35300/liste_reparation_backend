from marshmallow import Schema, fields, EXCLUDE

# ── Marque ────────────────────────────────────────────────────
class MarqueSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    id       = fields.Int(dump_only=True)
    nom      = fields.Str(required=True)
    url_logo = fields.Str(allow_none=True)

# ── Modele ────────────────────────────────────────────────────
class ModeleSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    id           = fields.Int(dump_only=True)
    nom          = fields.Str(required=True)
    type_machine = fields.Str(required=True)
    marque_id    = fields.Int(required=True, load_only=True)
    marque       = fields.Nested(MarqueSchema, dump_only=True)
    label        = fields.Str(dump_only=True)

class ModeleSimpleSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    id           = fields.Int(dump_only=True)
    nom          = fields.Str()
    type_machine = fields.Str()
    marque_id    = fields.Int()
    label        = fields.Str(dump_only=True)

# ── PieceRef ──────────────────────────────────────────────────
class PieceRefSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    id          = fields.Int(dump_only=True)
    ref_piece   = fields.Str(required=True)
    designation = fields.Str(load_default='')
    marque_id   = fields.Int(required=True, load_only=True)

# ── Machine ───────────────────────────────────────────────────
class MachineSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    id           = fields.Int(dump_only=True)
    numero_serie = fields.Str(required=True)
    modele_id    = fields.Int(allow_none=True)
    modele       = fields.Nested(ModeleSimpleSchema, dump_only=True)
    statut       = fields.Str(load_default='en_attente')
    date_entree  = fields.Date(allow_none=True)
    notes        = fields.Str(load_default='')
    created_at   = fields.DateTime(dump_only=True)

# ── PieceChangee ──────────────────────────────────────────────
class PieceChangeeSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    id           = fields.Int(dump_only=True)
    piece_ref_id = fields.Int(dump_only=True)
    ref_piece    = fields.Str(required=True)
    designation  = fields.Str(load_default='')
    quantite     = fields.Int(load_default=1)
    is_new       = fields.Bool(load_default=False)

# ── Reparation ────────────────────────────────────────────────
class ReparationSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    id              = fields.Int(dump_only=True)
    machine_id      = fields.Int(required=True)
    machine         = fields.Nested(MachineSchema, dump_only=True)
    technicien      = fields.Str(load_default='')
    technicien_id   = fields.Int(dump_only=True, allow_none=True)
    date_reparation = fields.Str(required=True)   # JJ/MM/AAAA
    description     = fields.Str(load_default='')
    created_at      = fields.DateTime(dump_only=True)
    pieces          = fields.List(fields.Nested(PieceChangeeSchema), load_default=[])
