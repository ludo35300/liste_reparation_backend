BEGIN;

INSERT INTO marques (nom)
VALUES ('CONTI')
ON CONFLICT (nom) DO NOTHING;

INSERT INTO modeles (nom, type_machine, marque_id)
SELECT 'CC102', 'MACHINE', m.id
FROM marques m
WHERE m.nom = 'CONTI'
ON CONFLICT (nom, marque_id) DO NOTHING;

INSERT INTO piece_refs (ref_piece, designation, marque_id, quantite)
SELECT v.ref_piece, v.designation, m.id, 0
FROM marques m
JOIN (
  VALUES
    ('4250301', 'Résistance 3600W (2G) + jt'),
    ('408714',  'Joint Résistance'),
    ('408898',  'Dépresseur 1/4 Gaz'),
    ('404326',  'Soupape sécurité 1,5 Bar 3/8'),
    ('4106282', 'Sonde de température'),
    ('410634',  'Thermostat secu 160°(klixon)'),
    ('470161',  'EV 2 voies Bloc Entrée Eau'),
    ('219100',  'Joint clapet anti retour Bloc Entrée Eau'),
    ('409774',  'Valve expansion 12 BARS'),
    ('407239',  'EV 3 voies Groupe Café'),
    ('403457',  'Joint Gicleur/ Robinet'),
    ('403458',  'Filtre gicleur'),
    ('411374',  'campana'),
    ('173100',  'Joint campana'),
    ('2713',    'joint porte filtre'),
    ('355900',  'Douchette à grille'),
    ('405621',  'Tube silicone 6X9'),
    ('4153111', 'Porte-Filtre 1T noir compl.S/S filtre'),
    ('4153121', 'Porte-Filtre 2T noir compl.S/S filtre'),
    ('415687',  'Filtre 1 tasse embossé'),
    ('16780',   'Filtre 2T'),
    ('16795',   'Filtre de nettoyage'),
    ('CD632',   'Brosse Nylon'),
    ('411812',  'Tuyau vidange annelé'),
    ('470167',  'Condensateur 8µF pour moteur RPM'),
    ('CDVD300', 'Pompe 200L (tête)'),
    ('411861',  'Filtre 3/8 entrée pompe'),
    ('462313',  'Flexible entrée d''eau 1,5 mètre'),
    ('55200',   'Joint axe robinet'),
    ('407502',  'Joint plat robinet'),
    ('470832',  'Display CC100'),
    ('470205',  'Centrale CC100 display')
) AS v(ref_piece, designation) ON TRUE
WHERE m.nom = 'CONTI'
ON CONFLICT (ref_piece) DO NOTHING;

INSERT INTO modele_piece_refs (modele_id, piece_ref_id)
SELECT mo.id, p.id
FROM modeles mo
JOIN marques ma ON ma.id = mo.marque_id
JOIN piece_refs p ON p.marque_id = ma.id
WHERE ma.nom = 'CONTI'
  AND mo.nom = 'CC102'
  AND p.ref_piece IN (
    '4250301','408714','408898','404326','4106282','410634','470161',
    '219100','409774','407239','403457','403458','411374','173100',
    '2713','355900','405621','4153111','4153121','415687','16780',
    '16795','CD632','411812','470167','CDVD300','411861','462313',
    '55200','407502','470832','470205'
  )
ON CONFLICT DO NOTHING;

COMMIT;