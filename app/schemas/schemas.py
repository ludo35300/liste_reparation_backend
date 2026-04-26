from marshmallow import Schema, fields, EXCLUDE
from marshmallow.validate import Length, OneOf, Range

STATUTS_VALIDES = ('en_attente', 'en_reparation', 'pret', 'termine')


# ── Marque ────────────────────────────────────────────────────
class MarqueSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id       = fields.Int(dump_only=True)
    nom      = fields.Str(required=True, validate=Length(min=1, max=100))
    url_logo = fields.Str(allow_none=True, validate=Length(max=500))


# ── Modele ────────────────────────────────────────────────────
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


# ── PieceRef ──────────────────────────────────────────────────
class PieceRefSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id          = fields.Int(dump_only=True)
    ref_piece   = fields.Str(required=True, validate=Length(min=1, max=100))
    designation = fields.Str(load_default='', validate=Length(max=200))
    marque_id   = fields.Int(required=True, load_only=True)


# ── Machine ───────────────────────────────────────────────────
class MachineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id           = fields.Int(dump_only=True)
    numero_serie = fields.Str(required=True, validate=Length(min=1, max=100))
    modele_id    = fields.Int(allow_none=True)
    modele       = fields.Nested(ModeleSimpleSchema, dump_only=True)
    statut       = fields.Str(load_default='en_attente', validate=OneOf(
                        STATUTS_VALIDES,
                        error="Statut invalide. Valeurs acceptées : " + ", ".join(STATUTS_VALIDES)
                   ))
    date_entree  = fields.Date(allow_none=True)
    notes        = fields.Str(load_default='', validate=Length(max=2000))
    created_at   = fields.DateTime(dump_only=True)


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


# ── Reparation ────────────────────────────────────────────────
class ReparationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id              = fields.Int(dump_only=True)
    machine_id      = fields.Int(required=True)
    machine         = fields.Nested(MachineSchema, dump_only=True)
    technicien      = fields.Str(load_default='', validate=Length(max=100))
    technicien_id   = fields.Int(dump_only=True, allow_none=True)
    date_reparation = fields.Date(required=True, format='iso')
    description     = fields.Str(load_default='')
    created_at      = fields.DateTime(dump_only=True)
    pieces          = fields.List(fields.Nested(PieceChangeeSchema), load_default=[])