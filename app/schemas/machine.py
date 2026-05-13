# ── Machine ───────────────────────────────────────────────────
from marshmallow import Schema, fields, EXCLUDE
from marshmallow.validate import Length, OneOf

from app.constantes.reparations import STATUTS_VALIDES
from .modele import ModeleSchema

class MachineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id           = fields.Int(dump_only=True)
    numero_serie = fields.Str(required=True, validate=Length(min=1, max=100))
    modele_id    = fields.Int(allow_none=True)
    modele       = fields.Nested(ModeleSchema, dump_only=True)
    statut       = fields.Str(load_default='en_attente', validate=OneOf(
                        STATUTS_VALIDES,
                        error="Statut invalide. Valeurs acceptées : " + ", ".join(STATUTS_VALIDES)
                   ))
    created_at   = fields.DateTime(dump_only=True)