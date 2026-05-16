# app/models/reparation.py
# ─────────────────────────────────────────────────────────────────────────────
# Modèle SQLAlchemy pour une réparation.
#
# Note de conception :
#   La colonne `technicien` (String) co-existe avec la FK `technicien_id`.
#   - technicien_id : référence l'utilisateur actif (peut devenir NULL si l'user est supprimé)
#   - technicien    : snapshot du nom au moment de la réparation (historique)
#   Utiliser la property `technicien_nom` pour obtenir toujours le nom le plus à jour.
# ─────────────────────────────────────────────────────────────────────────────
from datetime import datetime, timezone

from app.constantes.reparations import STATUTS_REPARATION_VALIDES
from app.extensions import db

# Construction de la contrainte SQL depuis la constante Python.
# Génère : statut IN ('en_reparation', 'pret', 'termine', ...)
# Défini au niveau module (hors de la classe) pour être accessible dans __table_args__.
_STATUTS_SQL = ", ".join(f"'{s}'" for s in STATUTS_REPARATION_VALIDES)


class Reparation(db.Model):
    """Représente une réparation associée à une machine.

    Relations :
        machine       : la machine concernée (Many-to-One)
        technicien_ref: l'utilisateur technicien (Many-to-One, nullable)
        pieces        : pièces remplacées lors de la réparation (One-to-Many)
        actions       : journal des interventions (One-to-Many, ordonné par date)
    """

    __tablename__ = 'reparations'

    # ── Clé primaire ─────────────────────────────────────────────────────────────
    id              = db.Column(db.Integer, primary_key=True)

    # ── Clés étrangères ──────────────────────────────────────────────────────────
    # CASCADE : si la machine est supprimée, ses réparations le sont aussi
    machine_id      = db.Column(db.Integer,
                                db.ForeignKey('machines.id', ondelete='CASCADE'),
                                nullable=False, index=True)
    # SET NULL : si le technicien est supprimé, la réparation reste mais sans référence user
    technicien_id   = db.Column(db.Integer,
                                db.ForeignKey('users.id', ondelete='SET NULL'),
                                nullable=True, index=True)

    # ── Colonnes métier ───────────────────────────────────────────────────────────
    # Nom du technicien en snapshot (historique, voir note de conception en tête de fichier)
    technicien      = db.Column(db.String(100), default='')
    date_reparation = db.Column(db.Date, nullable=False)           # Date d'entrée en réparation
    date_cloture    = db.Column(db.Date, nullable=True)            # Date de clôture (NULL si en cours)
    # Statut validé par CheckConstraint ci-dessous
    statut          = db.Column(db.String(20), nullable=False, default='en_reparation')
    description     = db.Column(db.Text, default='')               # Descriptif de la panne
    created_at      = db.Column(db.DateTime(timezone=True),
                                default=lambda: datetime.now(timezone.utc))

    # ── Contraintes de table ─────────────────────────────────────────────────────────
    # Vérifie au niveau base de données que `statut` ne peut contenir
    # qu'une valeur de STATUTS_REPARATION_VALIDES (défini dans app/constantes/).
    __table_args__ = (
        db.CheckConstraint(f"statut IN ({_STATUTS_SQL})", name='ck_reparation_statut'),
    )

    # ── Relations SQLAlchemy ─────────────────────────────────────────────────────────
    machine         = db.relationship('Machine', back_populates='reparations')
    technicien_ref  = db.relationship('User', back_populates='reparations',
                                      foreign_keys=[technicien_id])
    # cascade='all, delete-orphan' : supprime les pièces et actions si la réparation est supprimée
    pieces          = db.relationship('PieceChangee', back_populates='reparation',
                                      cascade='all, delete-orphan', lazy='select')
    actions         = db.relationship('ReparationAction', back_populates='reparation',
                                      cascade='all, delete-orphan',
                                      order_by='ReparationAction.date_action',
                                      lazy='select')

    # ── Properties ────────────────────────────────────────────────────────────────

    @property
    def technicien_nom(self) -> str:
        """Retourne le nom du technicien le plus à jour.

        Priorité :
          1. Le nom de l'utilisateur lié (technicien_ref) si la relation existe
          2. Le snapshot stocké dans la colonne `technicien` (historique)
          3. Chaîne vide si aucun des deux n'est disponible
        """
        if self.technicien_ref:
            return f"{self.technicien_ref.first_name} {self.technicien_ref.last_name}".strip()
        return self.technicien or ''

    def __repr__(self):
        return f'<Reparation machine={self.machine_id} {self.date_reparation} [{self.statut}]>'
