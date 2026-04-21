from app.extensions import db


class Marque(db.Model):
    __tablename__ = 'marques'

    id       = db.Column(db.Integer, primary_key=True)
    nom      = db.Column(db.String(100), nullable=False, unique=True)
    url_logo = db.Column(db.String(500), nullable=True)

    modeles  = db.relationship('Modele',    back_populates='marque',
                               cascade='all, delete-orphan', lazy='select')
    pieces   = db.relationship('PieceRef',  back_populates='marque',
                               cascade='all, delete-orphan', lazy='select')

    def __repr__(self):
        return f'<Marque {self.nom}>'
