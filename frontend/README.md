# Frontend — Smart Air Pollution Monitoring Portal

This folder will contain the responsive dashboard web application.

## Planned Structure (Step 2–3)

```
frontend/
├── index.html           # Main dashboard page
├── css/
│   └── style.css        # All styles (responsive, dark/light mode)
├── js/
│   ├── api.js           # Wrapper around fetch() calls to the backend
│   ├── dashboard.js     # City selector, AQI cards, chart rendering
│   └── labels.js        # REAL / SIMULATED / FALLBACK badge logic
└── assets/
    └── icons/           # SVG icons for AQI categories
```

## Technology

- Pure HTML5, CSS3, Vanilla JavaScript (ES6+)
- Chart.js loaded from CDN (no install required)
- No build step — open index.html directly in a browser

## Design Targets

- Responsive: works on 320px mobile to 1920px desktop
- Dark theme with readable AQI colour coding
- Every data widget shows a visible data-source badge (REAL / SIMULATED / FALLBACK)
- No direct calls to OpenAQ — all data comes from the backend REST API

## Running (Step 2–3 onwards)

```
1. Start the backend: python backend/app.py
2. Open frontend/index.html in a browser
```

No npm, no webpack, no build step required.
