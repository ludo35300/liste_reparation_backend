from marshmallow import Schema, fields, EXCLUDE, validates, ValidationError
from marshmallow.validate import Length, OneOf, Range

from app.constantes.reparations import STATUTS_VALIDES

TYPES_ACTION_VALIDES = (
    'diagnostic', 'demontage', 'remplacement_piece',
    'nettoyage', 'test', 'commentaire', 'statut'
)

class ActionPieceChangeeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id           = fields.Int(dump_only=True)
    piece_ref_id = fields.Int(required=True)
    ref_piece    = fields.Str(dump_only=True)
    designation  = fields.Str(dump_only=True)
    quantite     = fields.Int(load_default=1, validate=Range(
                       min=1, error="La quantité doit être ≥ 1"
                   ))


class ReparationActionSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id            = fields.Int(dump_only=True)
    reparation_id = fields.Int(dump_only=True)
    technicien_id = fields.Int(load_default=None, allow_none=True)
    type          = fields.Str(required=True, validate=OneOf(
                       TYPES_ACTION_VALIDES,
                       error="Type invalide. Valeurs : " + ", ".join(TYPES_ACTION_VALIDES)
                   ))
    titre         = fields.Str(required=True, validate=Length(min=1, max=200))
    description   = fields.Str(load_default='')
    technicien    = fields.Str(load_default='', validate=Length(max=100))
    date_action   = fields.Date(required=True, format='iso')
    duree_minutes = fields.Int(load_default=None, allow_none=True,
                               validate=Range(min=1, error="Durée doit être ≥ 1 min"))
    statut_avant  = fields.Str(load_default=None, allow_none=True,
                               validate=OneOf(STATUTS_VALIDES + (None,)))
    statut_apres  = fields.Str(load_default=None, allow_none=True,
                               validate=OneOf(STATUTS_VALIDES + (None,)))
    pieces        = fields.List(fields.Nested(ActionPieceChangeeSchema), load_default=[])
    created_at    = fields.DateTime(dump_only=True)

    @validates('statut_apres')
    def validate_statut_apres(self, value):
        """statut_apres requis si type == 'statut'."""
        # Validation croisée gérée dans le service
        pass
