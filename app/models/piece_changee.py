from app.extensions import db

class PieceChangee(db.Model):
    __tablename__ = 'pieces_changees'

    id            = db.Column(db.Integer, primary_key=True)
    reparation_id = db.Column(db.Integer, db.ForeignKey('reparations.id'), nullable=False)
    ref_piece     = db.Column(db.String(50),  nullable=False)
    designation   = db.Column(db.String(200), nullable=False)
    quantite      = db.Column(db.Integer, nullable=False, default=1)