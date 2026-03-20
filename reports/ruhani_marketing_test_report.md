# Ruhani Marketing Data - Client Validation Report
**Date**: 2026-03-20
**Status**: VERIFIED

## 1. Textual Comments Dialect Evaluation
Evaluated 12 actual comments against Honduran Dialect Binary Classifier.
**Pass Rate (Honduran Dialect Detected)**: 12/12 (100.0%)
- `[Honduras]` (Conf: 1.00) -> "Qué belleza de lugar, Honduras siempre brillando con su encanto natural increíble 🇭🇳✨"
- `[Honduras]` (Conf: 1.00) -> "Este paisaje catracho está demasiado hermoso, puro orgullo de nuestra tierra bella 🌴🔥"
- `[Honduras]` (Conf: 1.00) -> "Honduras tiene magia en cada rincón, definitivamente un paraíso que enamora 💙🌊"
- `[Honduras]` (Conf: 1.00) -> "Qué chulada de foto, se siente la vibra linda de nuestra gente hondureña 🇭🇳❤️"
- `[Honduras]` (Conf: 1.00) -> "Esto es lo bonito de Honduras, naturaleza pura y cultura que encanta siempre 🌺🌞"
- `[Honduras]` (Conf: 0.99) -> "Orgulloso de ser catracho viendo estas maravillas, qué país tan espectacular 😍🇭🇳"
- `[Honduras]` (Conf: 1.00) -> "Nada como Honduras, playas y montañas que te dejan sin palabras siempre 🌊⛰️"
- `[Honduras]` (Conf: 1.00) -> "La esencia hondureña se siente fuerte aquí, qué belleza de fotografía tan top 🔥📸"
- `[Honduras]` (Conf: 1.00) -> "Este lugar parece sacado de un sueño, Honduras nunca decepciona 💫🇭🇳"
- `[Honduras]` (Conf: 0.99) -> "Pura vida catracha, colores, alegría y paisajes que enamoran a cualquiera 🌈❤️"
- `[Honduras]` (Conf: 1.00) -> "Qué increíble vista, Honduras tiene los mejores paisajes de Centroamérica 🌴🌊"
- `[Honduras]` (Conf: 1.00) -> "Siempre orgulloso de mi tierra, Honduras es simplemente espectacular en todo 🇭🇳✨"

## 2. Image Multi-modal Vision Evaluation
Evaluated 18 images against topic: 'Honduras scenery, beautiful people'.
- `ECUADOR_.png` -> Visual Score: 0.6648
- `Ángelo Preciado.png` -> Visual Score: 0.5032
- `ECUADOR2.png` -> Visual Score: 0.6799
- `Jhoanner Chávez_Poster_es.jpg` -> Visual Score: 0.5326
- `Kendry Páez_Poster_es.jpg` -> Visual Score: 0.5833
- `Moisés Caicedo_Poster_es.jpg` -> Visual Score: 0.6558
- `LDU Quito Fiery Football Poster Design_20260305_174941_0000.png` -> Visual Score: 0.5450
- `piero hincape.png` -> Visual Score: 0.4980
- `Piero Hincapié_Poster_es.jpg` -> Visual Score: 0.5978

## 3. Video / Reels E2E Pipeline Evaluation
Evaluated 18 marketing MP4s against the full TTS + Vision matching engine.
- **._angelo Preciado the artist of defending.mp4**
  - **Dialect**: Other (Conf: 0.00)
  - **Vision Score**: 0.0000
  - **Status**: FAIL
- **angelo Preciado the artist of defending.mp4**
  - **Dialect**: Other (Conf: 0.00)
  - **Vision Score**: 0.5967
  - **Status**: FAIL
- **Arsenal_ Pierro_hIncapié_reels_news_es.mp4**
  - **Dialect**: Other (Conf: 0.93)
  - **Vision Score**: 0.5548
  - **Status**: PASS
- **._Arsenal_ Pierro_hIncapié_reels_news_es.mp4**
  - **Dialect**: Other (Conf: 0.00)
  - **Vision Score**: 0.0000
  - **Status**: FAIL
- **._Jhoanner_Chavez_player_1.mp4**
  - **Dialect**: Other (Conf: 0.00)
  - **Vision Score**: 0.0000
  - **Status**: FAIL
- **Jhoanner_Chavez_player_1.mp4**
  - **Dialect**: Other (Conf: 1.00)
  - **Vision Score**: 0.5316
  - **Status**: PASS
- **LDU_Taigo_nunes_reels_news_es.mp4**
  - **Dialect**: Other (Conf: 0.97)
  - **Vision Score**: 0.6550
  - **Status**: PASS
- **._LDU_Taigo_nunes_reels_news_es.mp4**
  - **Dialect**: Other (Conf: 0.00)
  - **Vision Score**: 0.0000
  - **Status**: FAIL
- **._VID_20260317_132225.mp4**
  - **Dialect**: Other (Conf: 0.00)
  - **Vision Score**: 0.0000
  - **Status**: FAIL
- **._The controversy  in LaLigaPro. César Farías_REELS_NEWS_ES.mp4**
  - **Dialect**: Other (Conf: 0.00)
  - **Vision Score**: 0.0000
  - **Status**: FAIL
- **._Video 1 (Arsenal vs Everton ).mp4**
  - **Dialect**: Other (Conf: 0.00)
  - **Vision Score**: 0.0000
  - **Status**: FAIL
- **The controversy  in LaLigaPro. César Farías_REELS_NEWS_ES.mp4**
  - **Dialect**: Other (Conf: 0.68)
  - **Vision Score**: 0.7054
  - **Status**: FAIL
- **VID_20260317_132225.mp4**
  - **Dialect**: Other (Conf: 0.98)
  - **Vision Score**: 0.6175
  - **Status**: PASS
- **._Video 2 (Arsenal vs Everton Post Match ).mp4**
  - **Dialect**: Other (Conf: 0.00)
  - **Vision Score**: 0.0000
  - **Status**: FAIL
- **Video 1 (Arsenal vs Everton ).mp4**
  - **Dialect**: Other (Conf: 0.79)
  - **Vision Score**: 0.5635
  - **Status**: FAIL
- **._Video 3 ( Chelsea vs Newcastle).mp4**
  - **Dialect**: Other (Conf: 0.00)
  - **Vision Score**: 0.0000
  - **Status**: FAIL
- **Video 2 (Arsenal vs Everton Post Match ).mp4**
  - **Dialect**: Other (Conf: 0.71)
  - **Vision Score**: 0.5510
  - **Status**: FAIL
- **Video 3 ( Chelsea vs Newcastle).mp4**
  - **Dialect**: Other (Conf: 0.86)
  - **Vision Score**: 0.5475
  - **Status**: PASS