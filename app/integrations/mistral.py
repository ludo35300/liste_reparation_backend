# app/integrations/mistral.py
import os, re, json, time
import requests


def _headers() -> dict:
    """Lit la clé à chaque appel pour respecter le chargement lazy du .env."""
    return {
        "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}",
        "Content-Type":  "application/json",
    }


def analyser_image_json(image_b64: str, refs_connues: str, prompt: str) -> dict:
    """
    Analyse une image de fiche en 2 appels Mistral séquentiels :
      1. /v1/ocr  (mistral-ocr-latest)  → extraction du texte brut en markdown
      2. /v1/chat/completions (mistral-small-latest) → structuration en JSON
    """
    print("\n" + "=" * 60)
    print("[MISTRAL] Début analyse image")
    print(f"[MISTRAL] Taille image base64 : {len(image_b64):,} caractères "
          f"(~{len(image_b64) * 3 // 4 / 1024:.0f} Ko)")

    texte_ocr = _extraire_texte_ocr(image_b64)

    if not texte_ocr:
        print("[MISTRAL] ❌ OCR vide — arrêt du traitement")
        return {}

    return _extraire_json_structure(texte_ocr, refs_connues, prompt)


def _extraire_texte_ocr(image_b64: str) -> str:
    print("\n[OCR] ── Étape 1 : extraction texte brut ──────────────────")

    payload = {
        "model": "mistral-ocr-latest",
        "document": {
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{image_b64}",
        },
    }

    for tentative in range(3):
        print(f"[OCR] Tentative {tentative + 1}/3 → POST /v1/ocr ...")
        try:
            r = requests.post(
                "https://api.mistral.ai/v1/ocr",
                headers=_headers(),
                json=payload,
                timeout=30,
            )
            print(f"[OCR] Réponse HTTP : {r.status_code}")
            r.raise_for_status()

            data = r.json()
            pages = data.get("pages", [])
            print(f"[OCR] Nombre de pages reçues : {len(pages)}")

            if not pages:
                print("[OCR] ❌ Aucune page retournée par l'API")
                return ""

            texte = pages[0].get("markdown", "")
            print(f"[OCR] ✅ Texte extrait ({len(texte)} caractères) :")
            print("-" * 40)
            print(texte[:1500])
            if len(texte) > 1500:
                print(f"... [tronqué, {len(texte) - 1500} caractères supplémentaires]")
            print("-" * 40)
            return texte

        except requests.exceptions.HTTPError:
            print(f"[OCR] ❌ Erreur HTTP {r.status_code} : {r.text[:300]}")
            if r.status_code == 429:
                attente = 15 * (tentative + 1)
                print(f"[OCR] Rate limit — attente {attente}s avant retry...")
                time.sleep(attente)
            else:
                raise

    print("[OCR] ❌ Échec après 3 tentatives")
    return ""


def _extraire_json_structure(texte_ocr: str, refs_connues: str, prompt: str) -> dict:
    print("\n[JSON] ── Étape 2 : structuration JSON ────────────────────")

    prompt_final = prompt.format(texte_ocr=texte_ocr, refs_connues=refs_connues)
    print(f"[JSON] Taille du prompt envoyé : {len(prompt_final)} caractères")

    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {
                "role": "user",
                "content": prompt_final,
            }
        ],
    }

    for tentative in range(3):
        print(f"[JSON] Tentative {tentative + 1}/3 → POST /v1/chat/completions ...")
        try:
            r = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=_headers(),
                json=payload,
                timeout=30,
            )
            print(f"[JSON] Réponse HTTP : {r.status_code}")
            r.raise_for_status()

            texte_brut = r.json()["choices"][0]["message"]["content"].strip()
            print("[JSON] Réponse brute de Mistral :")
            print("-" * 40)
            print(texte_brut[:2000])
            print("-" * 40)

            texte = re.sub(r"^```(?:json)?\s*", "", texte_brut)
            texte = re.sub(r"\s*```$", "", texte)

            match = re.search(r"\{.*\}", texte, re.DOTALL)
            if not match:
                print("[JSON] ❌ Aucun bloc JSON trouvé dans la réponse")
                return {}

            try:
                data = json.loads(match.group())
                print("[JSON] ✅ JSON parsé avec succès :")
                print(f"  nom         = {repr(data.get('nom', ''))}")
                print(f"  date        = {repr(data.get('date', ''))}")
                print(f"  numero      = {repr(data.get('numero', ''))}")
                print(f"  machine     = {repr(data.get('machine', ''))}")
                pieces = data.get("pieces", [])
                print(f"  pieces      = {len(pieces)} ligne(s) avec quantité")
                for p in pieces:
                    print(
                        f"    → ref={repr(p.get('ref', ''))} "
                        f"qte={p.get('quantite', '')} "
                        f"désig={repr(p.get('designation', '')[:40])}"
                    )
                print("=" * 60)
                return data

            except json.JSONDecodeError as e:
                print(f"[JSON] ❌ Erreur JSON decode : {e}")
                print(f"[JSON] Texte qui a échoué : {repr(texte[:300])}")
                return {}

        except requests.exceptions.HTTPError:
            print(f"[JSON] ❌ Erreur HTTP {r.status_code} : {r.text[:300]}")
            if r.status_code == 429:
                attente = 15 * (tentative + 1)
                print(f"[JSON] Rate limit — attente {attente}s avant retry...")
                time.sleep(attente)
            else:
                raise

    print("[JSON] ❌ Échec après 3 tentatives")
    return {}