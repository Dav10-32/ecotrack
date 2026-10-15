# 🌱 EcoTrack

MVP web que estima tu huella de carbono diaria a partir de una frase en español:

> "Hoy comí carne y viajé 20km en bus" → **8,28 kg CO₂e**

Construido con *vibe coding*: Cursor como copiloto, Streamlit para la interfaz y Replit para el despliegue.

## Ejecutar en local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Pruebas
```bash
pip install pytest
pytest
```

## Desplegar en Replit
1. En Replit: **Create App → Import from GitHub** y pega la URL de este repositorio.
2. Pulsa **Run** (el archivo `.replit` ya trae el comando de Streamlit).
3. Para URL pública: **Deploy**.

## Estructura
```
app.py                    # Interfaz Streamlit
ecotrack/calculator.py    # Interpretación del texto + factores de emisión
tests/test_calculator.py  # Pruebas unitarias
.cursorrules              # Reglas del agente de IA
VIBE_REPORT.md            # Reflexión del proceso
```

## Qué entiende hoy
| Tipo | Ejemplos | Factor aprox. |
|---|---|---|
| Transporte | bus, carro, moto, metro, taxi, avión (con "N km") | 0,04 – 0,26 kg/km |
| Sin emisión | bici, caminar | 0 |
| Alimentación | res, cerdo, pollo, pescado, huevo, lácteos, vegetariano, vegano | 0,4 – 6,5 kg/ración |
| Energía | "10 kWh" | 0,126 kg/kWh |

## Límites
- Los factores son **aproximaciones orientativas**, no cifras oficiales.
- El intérprete usa reglas simples de texto; lo que no entiende se muestra en pantalla en vez de inventarse un valor.
- Próximo paso natural: usar un modelo de lenguaje para interpretar frases más libres.
