from app.extensions import ma
from app.models.piece_changee import PieceChangee
from marshmallow import Schema, fields

class PieceChangeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PieceChangee
        load_instance = True
        exclude = ('reparation_id',)

class PieceRefSchema(Schema):
    id          = fields.Int(dump_only=True)
    ref_piece   = fields.Str(required=True)
    designation = fields.Str()

class MachineTypeRefSchema(Schema):
    id           = fields.Int(dump_only=True)
    marque       = fields.Str(required=True)
    modele       = fields.Str(required=True)
    type_machine = fields.Str(required=True)
    url_logo     = fields.Str(allow_none=True)
    label        = fields.Method('get_label', dump_only=True)
    pieces       = fields.List(fields.Nested(lambda: PieceRefSchema()), dump_only=True)

    def get_label(self, obj):
        return obj.label  # appelle la @property Python

class MachineTypeRefSimpleSchema(Schema):
    id           = fields.Int(dump_only=True)
    marque       = fields.Str()
    modele       = fields.Str()
    type_machine = fields.Str()
    url_logo     = fields.Str(allow_none=True) 
    label        = fields.Method('get_label', dump_only=True)

    def get_label(self, obj):
        return obj.label