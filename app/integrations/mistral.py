# app/integrations/mistral.py
import os, re, json, time
import requests

PROMPT_JSON = ""

def _headers() -> dict:
    """Lit la clé à chaque appel pour respecter le chargement lazy du .env."""
    return {
        "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}",
        "Content-Type":  "application/json",
    }

def extraire_texte_ocr(image_b64: str) -> str:
    payload = {
        "model":    "mistral-ocr-latest",
        "document": {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_b64}"},
    }
    for tentative in range(3):
        try:
            r = requests.post("https://api.mistral.ai/v1/ocr",
                              headers=_headers(), json=payload, timeout=30)
            r.raise_for_status()
            pages = r.json().get("pages", [])
            return pages[0].get("markdown", "") if pages else ""
        except requests.exceptions.HTTPError:
            if r.status_code == 429:
                time.sleep(15 * (tentative + 1))
            else:
                raise
    return ""

def extraire_json_structure(texte_ocr: str, refs_connues: str, prompt: str) -> dict:
    payload = {
        "model":    "mistral-small-latest",
        "messages": [{"role": "user",
                      "content": prompt.format(texte_ocr=texte_ocr, refs_connues=refs_connues)}],
    }
    for tentative in range(3):
        try:
            r = requests.post("https://api.mistral.ai/v1/chat/completions",
                              headers=_headers(), json=payload, timeout=30)
            r.raise_for_status()
            texte = r.json()["choices"][0]["message"]["content"].strip()
            texte = re.sub(r"^```(?:json)?\s*", "", texte)
            texte = re.sub(r"\s*```$", "", texte)
            match = re.search(r"\{.*\}", texte, re.DOTALL)
            return json.loads(match.group()) if match else {}
        except requests.exceptions.HTTPError:
            if r.status_code == 429:
                time.sleep(15 * (tentative + 1))
            else:
                raise
    return {}