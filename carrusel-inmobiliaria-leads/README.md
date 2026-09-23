# HEXA · ¿Cuánto te cuesta una consulta sin responder?

Carrusel Instagram de 9 slides (1080×1350 PNG) para inmobiliarias.

Tema: la inmediatez en la gestión de leads. Tono B2B, directo, sin hype tecnológico.

## Estructura

| # | Rol | Slide |
|---|-----|--------|
| 01 | Hook | Cover. Palabra héroe *consulta.* + retrato full-bleed |
| 02 | Dato | **80%** de las ventas se pierden por falta de seguimiento |
| 03 | Error #01 | *tarde.* — responder 16 h después |
| 04 | Error #02 | *genérica.* — 0 personalización, 0 contexto |
| 05 | Regla | **5 min** es la ventana de respuesta |
| 06 | Pérdida | Anatomy callouts: Tiempo · Comisión · Reputación |
| 07 | Error #03 | *fantasma.* — 0 llamadas, 0 WhatsApp después de la visita |
| 08 | Sistema | 3 reglas que separan a quien vende de quien espera |
| 09 | CTA | *no más suerte.* · «Quiero mi auditoría gratuita» |

## Diseño

- Tokens HEXA (`design-tokens.json`): fondo off-white `#F5F4F1`, grafito `#2F343A`, cobre `#C46A32` (acción + palabra héroe), azul `#2F90C9` (dato).
- Estética de referencia: feed Organizagram (palabra gigante en serif itálica, foto full-bleed con overlay, pills, anatomy-callouts).
- Tipografía: **Manrope** títulos · **Inter** cuerpo · **Playfair Display Italic** palabra héroe.
- Handle: `@hexa.inmo`

## Archivos

- `output/slide-01.png` … `slide-09.png` — slides listos para publicar
- `output/feed-grid.png` — vista 3×3 del carrusel
- `copy.json` — copy editable
- `caption.txt` — texto para el post de Instagram
- `assets/portrait.jpg` — retrato de estudio (headshot, brazos cruzados)
- `render.py` — renderer Pillow

## Regenerar

```bash
cd carrusel-inmobiliaria-leads
.venv/bin/python render.py
```

Edita `copy.json` y vuelve a ejecutar.
