# 📰 proyecto-noticias

Un proyecto de scraping, análisis y visualización de titulares para estudiar cómo los medios de comunicación construyen el discurso sobre la guerra en Ucrania.

## 🎯 Objetivo

Analizar los titulares de 8 medios de comunicación internacionales y agruparlos por **escala ideológica** (de pro-Rusia a pro-Ucrania), identificando:
- Qué medios publican más sobre el conflicto
- Las palabras más utilizadas según la línea editorial
- Cambios en el lenguaje y tendencias

## 🧠 ¿Qué incluye?

- ✔️ **Scraper en Python** con `requests`, `feedparser`, `BeautifulSoup` y `MySQL`
- ✔️ Almacenamiento de titulares en una base de datos relacional (`MySQL`)
- ✔️ Análisis de frecuencia de palabras por **escala ideológica**
- ✔️ Gráficos en `matplotlib` y `seaborn` para visualización clara
- ✔️ **Dashboard interactivo** con `Streamlit` para explorar los datos dinámicamente

## 📊 Escalas ideológicas

| Escala | Medio                          | Tendencia |
|--------|--------------------------------|-----------|
| 1️⃣     | RT                             | Super pro-Rusia |
| 2️⃣     | Sputnik News                  | Pro-Rusia |
| 3️⃣     | Al Jazeera                    | Leve pro-Rusia |
| 4️⃣     | Reuters                        | Neutral (ligera pro-Rusia) |
| 5️⃣     | The New York Times            | Neutral (ligera pro-Ucrania) |
| 6️⃣     | BBC News                      | Leve pro-Ucrania |
| 7️⃣     | The Guardian                  | Pro-Ucrania |
| 8️⃣     | Kyiv Independent              | Super anti-Rusia |

## 🖥️ Capturas

### Distribución de titulares por medio
![Gráfico de medios](grafico2.png)

### Dashboard interactivo
![Dashboard](dashboard.png) <!-- Puedes hacer una captura y guardarla como 'dashboard.png' para que aparezca aquí -->

## 🛠️ Tecnologías usadas

- `Python 3.10`
- `MySQL`
- `matplotlib`, `seaborn`
- `pandas`, `re`, `collections`
- `Streamlit`

## 🏁 Cómo ejecutar

```bash
git clone https://github.com/Martin-d-abloh/proyecto-noticias.git
cd proyecto-noticias
streamlit run dashboard.py




