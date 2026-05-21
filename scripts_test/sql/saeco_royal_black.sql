BEGIN;

-- 1) Créer la marque si elle n'existe pas
INSERT INTO marques (nom)
VALUES ('SAECO')
ON CONFLICT (nom) DO NOTHING;

-- 2) Créer le modèle si besoin
-- Adapte type_machine si tu veux autre chose que 'Expresso'
INSERT INTO modeles (nom, type_machine, marque_id)
SELECT 'ROYAL BLACK', 'Expresso', m.id
FROM marques m
WHERE m.nom = 'SAECO'
ON CONFLICT (nom, marque_id) DO NOTHING;

-- 3) Insérer les pièces si elles n'existent pas déjà
INSERT INTO piece_refs (ref_piece, designation, marque_id, quantite)
SELECT v.ref_piece, v.designation, m.id, 0
FROM marques m
JOIN (
  VALUES
    ('263666', 'COUVERCLE BAC EAU-NOIR-'),
    ('263668', 'RECIPIENT CAFE'),
    ('263669', 'GRILLE RECIPIENT CAFE- PROTEGE DOIGTS'),
    ('263684', 'bac eau usee Royal'),
    ('266229', 'ENSEMBLE MOULINS SUPERIEUR ET INFERIEUR'),
    ('264407', 'GROUP.CAF. ROYAL NER.'),
    ('263690', 'BACC D''EAU A'),
    ('12000140', 'pompe vibrante'),
    ('NV99.099', 'DEBITMETRE D=1,2'),
    ('12000182', 'POMPE ULKA MF 230V-50HZ'),
    ('9161.434', 'PIPETTE CHAUDIERE'),
    ('11005099', 'CURSEUR DE CHAUDIERE P119'),
    ('9011.132', 'RESSORT POUR EPINGLE'),
    ('11026413', 'BOUCHON PIVOT'),
    ('11009019', 'ENS PISTON'),
    ('263909', 'ENSEMBLE DE DISTRIBUTION DE CAFE RYL BLK MABS'),
    ('11001985', 'CABLE ALIM'),
    ('263692', 'ÉLECTROVANNE 2VOIES'),
    ('9161.064.050', 'PIPETTE ENTREE EAU'),
    ('263685', 'MASQUE RECUPERATION LIQUIDES (carter)'),
    ('11003796', 'UNITE D''INFUSION'),
    ('263402', 'CONDENSATEUR AVEC CABLAGE'),
    ('11026258', 'carter moto-reducteur'),
    ('266230', 'meules acier'),
    ('263665', 'grille')
) AS v(ref_piece, designation) ON TRUE
WHERE m.nom = 'SAECO'
ON CONFLICT (ref_piece) DO NOTHING;

-- 4) Associer ces pièces au modèle ROYAL BLACK
INSERT INTO modele_piece_refs (modele_id, piece_ref_id)
SELECT mo.id, p.id
FROM modeles mo
JOIN marques ma
  ON ma.id = mo.marque_id
JOIN piece_refs p
  ON p.marque_id = ma.id
WHERE ma.nom = 'SAECO'
  AND mo.nom = 'ROYAL BLACK'
  AND p.ref_piece IN (
    '263666','263668','263669','263684','266229','264407','263690',
    '12000140','NV99.099','12000182','9161.434','11005099','9011.132',
    '11026413','11009019','263909','11001985','263692','9161.064.050',
    '263685','11003796','263402','11026258','266230','263665'
  )
ON CONFLICT DO NOTHING;

COMMIT;