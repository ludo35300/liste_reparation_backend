# app/schemas/piece_schema.py
from app.extensions import ma
from marshmallow import Schema, fields, validate
from app.models.piece_changee import PieceChangee


class PieceChangeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model         = PieceChangee
        load_instance = True
        exclude       = ('reparation_id',)

    # Champ calculé : si la FK existe on retourne la désignation de référence
    designation_ref = fields.Method('get_designation_ref', dump_only=True)

    def get_designation_ref(self, obj):
        return obj.piece_ref.designation if obj.piece_ref else None


class PieceRefSchema(Schema):
    id          = fields.Int(dump_only=True)
    ref_piece   = fields.Str(required=True)
    designation = fields.Str()
    nb_machines = fields.Method('get_nb_machines', dump_only=True)

    def get_nb_machines(self, obj):
        return len(obj.machines)


class MachineTypeRefSchema(Schema):
    id           = fields.Int(dump_only=True)
    marque       = fields.Str(required=True)
    modele       = fields.Str(required=True)
    type_machine = fields.Str(required=True)
    url_logo     = fields.Str(allow_none=True)
    label        = fields.Method('get_label', dump_only=True)
    pieces       = fields.List(fields.Nested(lambda: PieceRefSchema()), dump_only=True)

    def get_label(self, obj):
        return obj.label


class MachineTypeRefSimpleSchema(Schema):
    id           = fields.Int(dump_only=True)
    marque       = fields.Str()
    modele       = fields.Str()
    type_machine = fields.Str()
    url_logo     = fields.Str(allow_none=True)
    label        = fields.Method('get_label', dump_only=True)

    def get_label(self, obj):
        return obj.label