# ── Reverse-proxy nginx avec configuration intégrée ─────────────────────────────
# La config est copiée dans l'image (pas de bind mount), ce qui permet de
# déployer le compose en mode « raw » sur Dokploy sans avoir le dépôt sur l'hôte.
FROM nginx:1.27-alpine

# Remplace la conf par défaut par celle du projet.
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8000
