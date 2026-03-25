from app.extensions import ma
from app.models.piece_changee import PieceChangee

class PieceChangeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PieceChangee
        load_instance = True
        exclude = ('reparation_id',)