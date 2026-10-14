"""Route de monitoring : affiche le rapport de dérive généré par le notebook."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from ..config import DOSSIER_MONITORING

router = APIRouter(tags=["Monitoring"])


@router.get("/monitoring/derive", response_class=HTMLResponse,
            summary="Rapport de dérive des données (Evidently)")
def rapport_derive():
    """Affiche le dernier rapport de dérive généré par le notebook, tel quel (page HTML).

    C'est un **instantané** : il n'est pas recalculé à chaque visite. Pour le mettre à jour,
    relance la section monitoring du notebook et remplace `rapport_derive_test.html`
    dans le dossier `monitoring/`."""
    chemin = DOSSIER_MONITORING / "rapport_derive_test.html"
    if not chemin.is_file():
        raise HTTPException(
            status_code=404,
            detail="Rapport introuvable : génère-le avec le notebook (section monitoring) "
                   "et dépose-le dans le dossier monitoring/.")
    return FileResponse(chemin, media_type="text/html")
