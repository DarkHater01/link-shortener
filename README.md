# Link Shortener (GitHub como backend)

Un acortador de URLs sin servidor, sin base de datos y sin hosting de pago:

| Pieza | Es |
|-------|-----|
| **Base de datos** | los issues con la etiqueta `link` |
| **Panel de admin + moderacion** | la lista de issues (poner la etiqueta = publicar) |
| **Compilador** | un Action que corre `bin/build.py` |
| **Hosting** | GitHub Pages (coste 0) |

## Instalar

1. Copia a tu repo: `bin/build.py`, `.github/workflows/build.yml` y `.github/ISSUE_TEMPLATE/`.
2. En *Settings → Pages*, pon **Source: GitHub Actions** (no "Deploy from a branch").
3. Crea una etiqueta llamada `link` en *Issues → Labels*.
4. Haz push a `main` (el workflow se dispara solo).

El sitio queda en `https://<usuario>.github.io/<repo>/` y cada enlace en `.../s/<slug>/`.

## Usar

Abre un issue:
- **Titulo** = el slug (`mi-video`).
- **Cuerpo** = la URL (`https://...`).
- Ponle la etiqueta **`link`** → en segundos aparece publicado.

Puedes autoservirte del formulario en *Issues → New issue → Proponer un enlace*.

## Gotchas y limites

- **Paginas publicas**: Pages solo sirve desde repos publicos (salvo plan de pago). O sea, tu lista de enlaces es publica.
- **Sin estadisticas de clics**: no las hay porque no hay servidor que resuelva. Para eso necesitarias un servicio real.
- **Es tu reputacion**: si publicas enlaces a phishing, el problema es tuyo. Por eso el diseño exige que **tu pongas la etiqueta**: cualquiera propone, tu decides.
- La redireccion es un `meta refresh` instantaneo; algunos clientes raros podrian no seguirlo.

## Por que no te banean

No usa los runners para nada ajeno al repositorio, ni para minar, ni como proxy/VPN, ni como almacenamiento en masa. Solo usa issues y Pages, que es exactamente para lo que existen. El consumo de CI es de milisegundos por build.
