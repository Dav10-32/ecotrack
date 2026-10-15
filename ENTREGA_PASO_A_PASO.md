# Guía de entrega – EcoTrack

## ¿Hay que subir a un repositorio?
**Sí.** El entregable 1 pide "URL del Repositorio o Repl". Lo más sólido es entregar **los dos**: GitHub (código) + Replit (app funcionando), conectados entre sí.

## Paso 1 – Cursor (entorno local)
1. Instala Cursor desde cursor.com y abre la carpeta `ecotrack`.
2. Verifica que `.cursorrules` esté en la raíz (si no lo ves, activa archivos ocultos).
3. En el chat/Composer elige el mejor modelo disponible (Claude Sonnet o GPT-4o, o sus versiones más nuevas).
4. **Para tu captura:** pídele al Composer algo real, p. ej. *"Agrega un campo para registrar cuántas veces tomé agua embotellada y súmalo al total, con su test"*. Así la captura muestra al agente trabajando.

## Paso 2 – GitHub
```bash
cd ecotrack
git init
git add .
git commit -m "EcoTrack MVP"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/ecotrack.git
git push -u origin main
```
(Crea antes el repositorio vacío `ecotrack` en github.com, público.)

## Paso 3 – Replit
1. Crea cuenta en replit.com → **Create App → Import from GitHub** → pega tu URL.
2. Pulsa **Run** y comprueba que la app abre.
3. Pulsa **Deploy** para obtener la URL pública.

## Paso 4 – Captura de pantalla
Una sola imagen (o dos pegadas) con **Cursor** (chat del agente + código) y **Replit** (la app corriendo) visibles.

## Paso 5 – Personaliza el Vibe Report
`VIBE_REPORT.md` es un borrador (≈390 palabras, límite 500). **Ajústalo con tu experiencia real** (qué te costó, cómo te sentiste): se evalúa tu reflexión, y se nota cuando es propia.

## Checklist final
- [ ] URL de GitHub y/o Replit abre sin errores
- [ ] `.cursorrules` en la raíz del repo
- [ ] `VIBE_REPORT.md` personalizado (< 500 palabras)
- [ ] Captura con Cursor + Replit
- [ ] `pytest` pasa (11 pruebas)

## Texto para pegar en el campo de respuesta
```
Repositorio: https://github.com/TU_USUARIO/ecotrack
App desplegada (Replit): https://TU-REPL.replit.app

Entregables:
1. Código fuente: repositorio anterior (app Streamlit + motor de cálculo + 11 tests).
2. .cursorrules: en la raíz del repositorio.
3. Vibe Report: VIBE_REPORT.md en el repositorio.
4. Captura de Cursor y Replit: adjunta.

Resumen: EcoTrack convierte frases como "Hoy comí carne y viajé 20km en bus"
en un estimado de CO₂e (8,28 kg) con desglose, sugerencia y comparación
con una referencia diaria.
```
