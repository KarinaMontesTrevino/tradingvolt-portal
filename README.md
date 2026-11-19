# TradingVolt Quantitative Research Portal

Portal web institucional para publicar y explorar investigaciones cuantitativas de trading, modelos de estrés de colateral y gestión de riesgo asimétrico.

---

## 🚀 Cómo Ejecutar el Sitio Web Localmente

Tienes dos formas inmediatas de verlo en tu máquina:

### Opción 1: Servidor Python con un solo comando (Recomendado)
Ejecuta en tu terminal PowerShell:
```powershell
python C:\Users\kim17\.gemini\antigravity\scratch\tradingvolt_portal\serve.py
```
Abrirá automáticamente tu navegador en `http://localhost:8080`.

### Opción 2: Abrir directamente el archivo HTML
Haz doble clic sobre:
`C:\Users\kim17\.gemini\antigravity\scratch\tradingvolt_portal\index.html`

---

## 🌐 Cómo Publicar el Sitio Web en Internet Gratis

Este portal está construido con estándares web estáticos modernos (HTML5, Tailwind CSS, JavaScript Vanilla, sin dependencias complejas de compilación). Puedes publicarlo en la nube en menos de 2 minutos:

### 1. Vercel (Recomendado, 1 clic)
1. Instala Vercel CLI: `npm i -g vercel` (o arrastra la carpeta a [vercel.com](https://vercel.com)).
2. Desde la carpeta `tradingvolt_portal`, ejecuta: `vercel` y sigue los pasos en pantalla.
3. Tu sitio estará en vivo en `https://tradingvolt.vercel.app`.

### 2. GitHub Pages
1. Sube esta carpeta a un repositorio de GitHub (ej. `tradingvolt-research`).
2. Ve a **Settings -> Pages**.
3. Selecciona la rama `main` y la carpeta raíz `/`.
4. Tu sitio estará en vivo en `https://tu-usuario.github.io/tradingvolt-research`.

### 3. Netlify
1. Ve a [app.netlify.com/drop](https://app.netlify.com/drop).
2. Arrastra la carpeta `tradingvolt_portal`.
3. Tu web se publica al instante con certificado SSL gratuito.

---

## 📂 Contenido Incluido en el Portal

- **Investigación 01**: Backtest cuantitativo de 1,312 rupturas CAN SLIM (2012–2025) y la regla del Stop Loss del 8%.
- **Investigación 02**: Modelo *Margin Call* aplicado a flotas de GPUs, deterioro de activos bajo IAS 36, CapEx en Microsoft Azure y efecto látigo en Nvidia.
- **Simulador Interactivo 01**: Calculadora en vivo de tamaño de posición asimétrica según el stop loss y riesgo de cuenta.
- **Simulador Interactivo 02**: Simulador en vivo 'Peter Sullivan' de deterioro contable e insolvencia por LTV.
- **Data Vault**: Descarga de todas las matrices y datasets en formato CSV.
