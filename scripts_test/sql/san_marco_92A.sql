// Ce script ajoute la marque SAN MARCO, le modèle 92A et les pièces associées à ce modèle.
// A utiliser avec: "docker compose -f docker-compose.prod.yml exec -T db psql -U tech_admin -d liste_reparation < scripts_test/sql/san_marco_92A.sql"
BEGIN;

INSERT INTO marques (nom)
VALUES ('SAN MARCO')
ON CONFLICT (nom) DO NOTHING;

INSERT INTO modeles (nom, type_machine, marque_id)
SELECT '92A', 'MOULIN', m.id
FROM marques m
WHERE m.nom = 'SAN MARCO'
ON CONFLICT (nom, marque_id) DO NOTHING;

INSERT INTO piece_refs (ref_piece, designation, marque_id, quantite)
SELECT v.ref_piece, v.designation, m.id, 0
FROM marques m
JOIN (
  VALUES
    ('MSD0166',   'FLEXIBLE GAZ'),
    ('SMD2297',   'COUVERCLE TREMIE GRAIN'),
    ('MSD2297',   'DOSEUR CAFE'),
    ('MSD16211',  'VERRE DOSEUR CAFE MOULU'),
    ('SMD496',    'COUVERCLE TREMIE'),
    ('MSD10420',  'TASSEUR DEM 57'),
    ('MSD202174', 'PAIRE DE MEULES DIAM 64'),
    ('MSD21504',  'PAIRE DE COLLIER DIAM 64'),
    ('MSD1500',   'COMPTEUR'),
    ('MSD108604', 'PLATINE')
) AS v(ref_piece, designation) ON TRUE
WHERE m.nom = 'SAN MARCO'
ON CONFLICT (ref_piece) DO NOTHING;

INSERT INTO modele_piece_refs (modele_id, piece_ref_id)
SELECT mo.id, p.id
FROM modeles mo
JOIN marques ma ON ma.id = mo.marque_id
JOIN piece_refs p ON p.marque_id = ma.id
WHERE ma.nom = 'SAN MARCO'
  AND mo.nom = '92A'
  AND p.ref_piece IN (
    'MSD0166','SMD2297','MSD2297','MSD16211','SMD496',
    'MSD10420','MSD202174','MSD21504','MSD1500','MSD108604'
  )
ON CONFLICT DO NOTHING;

COMMIT;