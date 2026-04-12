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

    texte_ocr = _extraire_texte_ocr(image_b64)

    if not texte_ocr:
        return {}

    return _extraire_json_structure(texte_ocr, refs_connues, prompt)


def _extraire_texte_ocr(image_b64: str) -> str:

    payload = {
        "model": "mistral-ocr-latest",
        "document": {
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{image_b64}",
        },
    }

    for tentative in range(3):
        try:
            r = requests.post(
                "https://api.mistral.ai/v1/ocr",
                headers=_headers(),
                json=payload,
                timeout=30,
            )
            r.raise_for_status()

            data = r.json()
            pages = data.get("pages", [])

            if not pages:
                return ""

            texte = pages[0].get("markdown", "")
            
            return texte

        except requests.exceptions.HTTPError:
            if r.status_code == 429:
                attente = 15 * (tentative + 1)
                time.sleep(attente)
            else:
                raise
    return ""


def _extraire_json_structure(texte_ocr: str, refs_connues: str, prompt: str) -> dict:

    prompt_final = prompt.format(texte_ocr=texte_ocr, refs_connues=refs_connues)

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
        try:
            r = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=_headers(),
                json=payload,
                timeout=30,
            )
            r.raise_for_status()

            texte_brut = r.json()["choices"][0]["message"]["content"].strip()

            texte = re.sub(r"^```(?:json)?\s*", "", texte_brut)
            texte = re.sub(r"\s*```$", "", texte)

            match = re.search(r"\{.*\}", texte, re.DOTALL)
            if not match:
                return {}

            try:
                data = json.loads(match.group())
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
                return {}

        except requests.exceptions.HTTPError:
            if r.status_code == 429:
                attente = 15 * (tentative + 1)
                time.sleep(attente)
            else:
                raise

    return {}