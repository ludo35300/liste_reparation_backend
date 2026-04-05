# app/schemas/reparation_schema.py
from app.extensions import ma
from marshmallow import fields, validate
from app.models.reparation import Reparation
from .piece_schema import PieceChangeeSchema


class ReparationSchema(ma.SQLAlchemyAutoSchema):
    pieces          = fields.List(fields.Nested(PieceChangeeSchema), dump_default=[])
    date_reparation = fields.Date(format='%d/%m/%Y')

    # Expose les données relationnelles en lecture
    machine_label   = fields.Method('get_machine_label',  dump_only=True)
    technicien_nom  = fields.Method('get_technicien_nom', dump_only=True)

    class Meta:
        model   = Reparation
        load_instance = True
        include_fk    = True
        # On expose les snapshots + les FK, pas les objets imbriqués entiers
        fields = (
            'id', 'numero_serie',
            'machine_type', 'machine_type_id', 'machine_label',
            'technicien', 'technicien_id', 'technicien_nom',
            'date_reparation', 'notes', 'created_at',
            'pieces',
        )

    def get_machine_label(self, obj):
        return obj.machine_ref.label if obj.machine_ref else obj.machine_type

    def get_technicien_nom(self, obj):
        if obj.technicien_ref:
            return f"{obj.technicien_ref.first_name} {obj.technicien_ref.last_name}".strip()
        return obj.technicien


class ReparationCreateSchema(ma.Schema):
    numero_serie    = fields.Str(required=True, validate=validate.Length(min=1))
    machine_type    = fields.Str(required=True)
    machine_type_id = fields.Int(load_default=None)
    technicien      = fields.Str(load_default='')
    technicien_id   = fields.Int(load_default=None)
    date_reparation = fields.Date(required=True, format='%d/%m/%Y')
    notes           = fields.Str(load_default='')
    pieces          = fields.List(fields.Dict(), load_default=[])