"""update_statut_reparation_en_reparation_terminee

Revision ID: b6ceb7c90097
Revises: fbeae12e26b6
Create Date: 2026-05-13

"""
from alembic import op

# ← Ces variables sont OBLIGATOIRES
revision = 'b6ceb7c90097'
down_revision = 'ddb3093b395e'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('ck_reparation_statut', 'reparations', type_='check')
    op.execute("UPDATE reparations SET statut = 'terminee' WHERE statut = 'en_cours'")
    op.execute("UPDATE reparations SET statut = 'terminee' WHERE statut = 'termine'")
    op.create_check_constraint(
        'ck_reparation_statut',
        'reparations',
        "statut IN ('en_reparation', 'terminee')"
    )


def downgrade():
    op.drop_constraint('ck_reparation_statut', 'reparations', type_='check')
    op.execute("UPDATE reparations SET statut = 'en_cours' WHERE statut = 'en_reparation'")
    op.execute("UPDATE reparations SET statut = 'termine' WHERE statut = 'terminee'")
    op.create_check_constraint(
        'ck_reparation_statut',
        'reparations',
        "statut IN ('en_cours', 'termine')"
    )