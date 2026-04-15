# app/reparations/service.py
from datetime import datetime
from difflib import get_close_matches

from app.extensions           import db
from app.models.reparation    import Reparation
from app.models.piece_changee import PieceChangee
from app.utils.fuzzy          import fuzzy_machine, fuzzy_piece


# ── Helpers internes ──────────────────────────────────────────
def _load_labels_machines() -> list:
    from app.models.reference import MachineTypeRef
    return [m.label for m in MachineTypeRef.query.all()]


def _load_pieces_connues() -> dict:
    from app.models.reference import PieceRef
    return {p.ref_piece.upper(): p.designation for p in PieceRef.query.all()}


# ── CRUD ──────────────────────────────────────────────────────
def creer_reparation(data: dict) -> Reparation:
    from app.models.reference import MachineTypeRef, PieceRef

    date_rep = data['date_reparation']
    if isinstance(date_rep, str):
        date_rep = datetime.strptime(date_rep, '%d/%m/%Y').date()

    labels         = _load_labels_machines()
    pieces_connues = _load_pieces_connues()

    machine_corrigee, _ = fuzzy_machine(data.get('machine_type', ''), labels)

    # ── Résolution machine ────────────────────────────────────
    machine_ref     = MachineTypeRef.find_by_label(machine_corrigee) if machine_corrigee else None
    machine_type_id = machine_ref.id if machine_ref else None

    # ── Résolution technicien ─────────────────────────────────
    technicien_id = None
    if data.get('technicien'):
        from app.models.user import User
        user = User.query.filter_by(first_name=data['technicien']).first()
        technicien_id = user.id if user else None

    rep = Reparation(
        numero_serie    = data['numero_serie'].strip().upper(),
        machine_type    = machine_corrigee or data.get('machine_type', ''),
        machine_type_id = machine_type_id,
        technicien      = data.get('technicien', ''),
        technicien_id   = technicien_id,
        date_reparation = date_rep,
        notes           = data.get('notes', '')
    )
    db.session.add(rep)
    db.session.flush()

    for p in data.get('pieces', []):
        ref_brute    = p.get('ref_piece', '').strip().upper()
        ref_corrigee, designation, _ = fuzzy_piece(ref_brute, pieces_connues, cutoff=0.80)

        # ── Cherche ou crée la PieceRef ───────────────────────
        piece_obj = PieceRef.query.filter_by(ref_piece=ref_corrigee).first()
        if not piece_obj:
            # Nouvelle pièce → on la crée dans le catalogue
            piece_obj = PieceRef(
                ref_piece   = ref_corrigee,
                designation = p.get('designation', designation or ref_corrigee)
            )
            db.session.add(piece_obj)
            db.session.flush()  # obtenir l'id immédiatement

        # ── Association machine ↔ pièce (si connue) ──────────
        if machine_ref and piece_obj not in machine_ref.pieces:
            machine_ref.pieces.append(piece_obj)

        # ── Enregistre la pièce changée ───────────────────────
        db.session.add(PieceChangee(
            reparation_id = rep.id,
            piece_ref_id  = piece_obj.id,
            quantite      = int(p.get('quantite', 1))
        ))

    db.session.commit()
    return rep


def get_historique(numero_serie: str) -> list:
    return (
        Reparation.query
        .filter_by(numero_serie=numero_serie.strip().upper())
        .order_by(Reparation.date_reparation.desc())
        .all()
    )


def get_by_id(rep_id: int) -> Reparation:
    return db.get_or_404(Reparation, rep_id)


def supprimer(rep_id: int) -> None:
    rep = db.get_or_404(Reparation, rep_id)
    db.session.delete(rep)
    db.session.commit()


# ── Suggestions ───────────────────────────────────────────────
def suggest_machine_types(query: str, n: int = 5) -> list[str]:
    labels = _load_labels_machines()
    return get_close_matches(query, labels, n=n, cutoff=0.5) if labels else []


def suggest_piece_refs(query: str, n: int = 5) -> list[str]:
    refs = list(_load_pieces_connues().keys())
    return get_close_matches(query, refs, n=n, cutoff=0.5) if refs else []

# ── Recherche enrichie ────────────────────────────────────────
def search_numero_serie(query: str) -> dict:
    """
    Recherche les réparations par numéro de série (recherche partielle)
    et enrichit le résultat avec les infos spécifiques au modèle de machine
    (vue éclatée, specs, description) via le registre app/machines/.
    """
    from app.machines import resolve_machine_info

    query_clean = query.strip().upper()

    # Toutes les réparations dont le numéro de série contient la recherche
    reparations = (
        Reparation.query
        .filter(Reparation.numero_serie.ilike(f'%{query_clean}%'))
        .order_by(Reparation.date_reparation.desc())
        .all()
    )

    if not reparations:
        return {
            "query": query,
            "found": False,
            "nombre_reparations": 0,
            "reparations": [],
            "machine_info": None,
        }

    # La réparation la plus récente fournit le snapshot machine_type
    derniere = reparations[0]

    # Construit le détail de chaque réparation
    historique = [
        {
            "id":               r.id,
            "date_reparation":  r.date_reparation.isoformat(),
            "machine_type":     r.machine_type,
            "technicien":       r.technicien,
            "notes":            r.notes,
            "pieces": [
                {
                    "ref_piece":   pc.piece_ref.ref_piece if pc.piece_ref else None,
                    "designation": pc.piece_ref.designation if pc.piece_ref else None,
                    "quantite":    pc.quantite,
                }
                for pc in r.pieces
            ],
        }
        for r in reparations
    ]

    # Résolution des infos machine (vue éclatée, specs…)
    machine_info = get_machine_info(
        machine_type=derniere.machine_type,
        numero_serie=derniere.numero_serie,
    )

    return {
        "query":              query,
        "found":              True,
        "numero_serie":       derniere.numero_serie,
        "machine_type":       derniere.machine_type,
        "nombre_reparations": len(reparations),
        "reparations":        historique,
        "machine_info":       machine_info,
    }


def get_machine_info(machine_type: str, numero_serie: str) -> dict | None:
    """
    Appelle le registre machines/ et retourne un dict sérialisable
    avec description, specs et vue éclatée.
    Retourne None si aucun handler ne reconnaît la machine.
    """
    from app.machines import resolve_machine_info

    # On passe machine_type dans brand ET model car le snapshot
    # peut contenir les deux ("Santos 40A"). Chaque handler filtre
    # via son propre regex dans can_handle().
    info = resolve_machine_info(
        brand=machine_type,
        model=machine_type,
        numero_serie=numero_serie,
    )

    if info is None:
        return None

    return {
        "description":    info.description,
        "specs":          info.specs,
        "exploded_view":  {
            "label":   info.exploded_view.label,
            "pdf_url": info.exploded_view.pdf_url,
            "note":    info.exploded_view.note,
        } if info.exploded_view else None,
    }