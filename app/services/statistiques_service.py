# app/services/statistiques_service.py
from collections import defaultdict
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models.piece_ref import PieceRef
from app.models.reparation import Reparation
from app.models.piece_changee import PieceChangee
from app.models.machine import Machine


STATUTS_EN_COURS = {'en_attente', 'en_reparation'}


def get_stats_globales() -> dict:
    total_reps    = db.session.query(func.count(Reparation.id)).scalar() or 0
    total_pieces  = db.session.query(func.sum(PieceChangee.quantite)).scalar() or 0
    machines_uniq = db.session.query(func.count(Machine.id)).scalar() or 0

    top_pieces = (
        db.session.query(
            PieceRef.ref_piece.label("ref"),
            PieceRef.designation.label("designation"),
            func.sum(PieceChangee.quantite).label("total"),
        )
        .join(PieceChangee, PieceChangee.piece_ref_id == PieceRef.id)
        .group_by(PieceRef.id, PieceRef.ref_piece, PieceRef.designation)
        .order_by(func.sum(PieceChangee.quantite).desc())
        .limit(10)
        .all()
    )

    reparations = (
        db.session.query(Reparation)
        .options(
            joinedload(Reparation.pieces),
            joinedload(Reparation.machine).joinedload(Machine.modele),
        )
        .order_by(Reparation.date_reparation.desc())
        .all()
    )

    # Dernière réparation par machine (reparations déjà triées par date desc)
    latest_by_machine: dict[int, int] = {}
    for r in reparations:
        mid = r.machine_id
        if mid and mid not in latest_by_machine:
            latest_by_machine[mid] = r.id

    # Stats par technicien — même logique que my-repairs.ts
    par_tech: dict = defaultdict(lambda: {'total': 0, 'en_cours': 0, 'terminees': 0})
    for r in reparations:
        nom = r.technicien or 'Inconnu'
        par_tech[nom]['total'] += 1

        mid = r.machine_id
        statut_machine = r.machine.statut if r.machine else None
        is_latest = mid is not None and latest_by_machine.get(mid) == r.id

        if is_latest and statut_machine in STATUTS_EN_COURS:
            par_tech[nom]['en_cours'] += 1
        else:
            par_tech[nom]['terminees'] += 1

    return {
        "total_reparations": int(total_reps),
        "total_pieces":      int(total_pieces),
        "machines_uniques":  int(machines_uniq),
        "pieces_les_plus_changees": [
            {"ref": p.ref, "designation": p.designation, "total": int(p.total)}
            for p in top_pieces
        ],
        "reparations": [
            {
                "id":              r.id,
                "machine":         r.machine.numero_serie if r.machine else '',
                "modele":          r.machine.modele.label if (r.machine and r.machine.modele) else '',
                "technicien":      r.technicien,
                "date_reparation": str(r.date_reparation),
                "description":     r.description,
                "pieces": [
                    {"ref_piece": pc.ref_piece, "designation": pc.designation, "quantite": pc.quantite}
                    for pc in (r.pieces or [])
                ],
            }
            for r in reparations
        ],
        "par_technicien": [
            {"technicien": k, "total": v["total"], "en_cours": v["en_cours"], "terminees": v["terminees"]}
            for k, v in par_tech.items()
        ],
    }