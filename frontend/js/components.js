/**
 * Reusable UI Components — shared across all pages.
 */
const Components = (() => {

    // ── Data Type Badge ──────────────────────────
    function dataBadge(type) {
        if (!type) return '';
        const t = type.toUpperCase();
        const cls = {
            'REAL': 'badge-real', 'SIMULATED': 'badge-simulated',
            'FALLBACK': 'badge-fallback', 'PREDICTED': 'badge-predicted',
        }[t] || 'badge-real';
        const label = { 'REAL': '● Real Data', 'SIMULATED': '◉ Simulated',
                        'FALLBACK': '◌ Fallback', 'PREDICTED': '◈ Predicted' }[t] || t;
        return `<span class="badge ${cls}">${label}</span>`;
    }

    // ── AQI Badge ────────────────────────────────
    function aqiBadge(aqi, category) {
        if (aqi === null || aqi === undefined) return '<span class="aqi-badge" style="opacity:0.5">N/A</span>';
        let cls = 'aqi-good';
        if (aqi > 400) cls = 'aqi-severe';
        else if (aqi > 300) cls = 'aqi-verypoor';
        else if (aqi > 200) cls = 'aqi-poor';
        else if (aqi > 100) cls = 'aqi-moderate';
        else if (aqi > 50) cls = 'aqi-satisfactory';
        return `<span class="aqi-badge ${cls}">${aqi} — ${category || 'Unknown'}</span>`;
    }

    function aqiColor(aqi) {
        if (aqi === null || aqi === undefined) return '#5a7085';
        if (aqi <= 50) return '#009966';
        if (aqi <= 100) return '#58a84b';
        if (aqi <= 200) return '#ffde33';
        if (aqi <= 300) return '#ff9933';
        if (aqi <= 400) return '#cc0033';
        return '#7e0023';
    }

    // ── AQI Ring ─────────────────────────────────
    function aqiRing(aqi, category) {
        const color = aqiColor(aqi);
        const val = aqi !== null && aqi !== undefined ? aqi : '—';
        const cat = category || '';
        return `
        <div class="aqi-card">
            <div class="aqi-ring" style="border-color: ${color}; box-shadow: 0 0 20px ${color}33;">
                <span class="aqi-value" style="color: ${color}">${val}</span>
            </div>
            <div class="aqi-label" style="color: ${color}">${cat}</div>
        </div>`;
    }

    // ── Pollutant Cards ──────────────────────────
    function pollutantCards(pollutants) {
        if (!pollutants) return '<p class="empty-state">No pollutant data available</p>';
        const icons = { pm25: '🌫️', pm10: '💨', no2: '🟤', so2: '🟡', co: '⚫', o3: '🔵' };
        const names = { pm25: 'PM2.5', pm10: 'PM10', no2: 'NO₂', so2: 'SO₂', co: 'CO', o3: 'O₃' };
        let html = '<div class="grid grid-3">';
        for (const [key, data] of Object.entries(pollutants)) {
            const val = data && data.value !== null && data.value !== undefined ? data.value : null;
            const unit = data ? data.unit || '' : '';
            html += `
            <div class="stat-card">
                <div class="stat-label">${icons[key] || '📊'} ${names[key] || key}</div>
                <div class="stat-value">${val !== null ? val : '<span style="color:var(--text-muted)">—</span>'}
                    <span class="stat-unit">${val !== null ? unit : ''}</span>
                </div>
            </div>`;
        }
        html += '</div>';
        return html;
    }

    // ── Stat Card ────────────────────────────────
    function statCard(label, value, unit = '') {
        const display = value !== null && value !== undefined ? value : '—';
        return `
        <div class="stat-card">
            <div class="stat-label">${label}</div>
            <div class="stat-value">${display}<span class="stat-unit">${unit}</span></div>
        </div>`;
    }

    // ── Intelligence Summary Card ────────────────
    function intelligenceCard(intelSummary) {
        if (!intelSummary) return '';
        return `
        <div class="card" style="margin-bottom:var(--spacing-lg); border-left: 4px solid var(--accent-primary);">
            <div class="card-header"><span class="card-title">🧠 Pollution Intelligence</span></div>
            <p style="font-size:var(--font-md); color:var(--text-primary); line-height:1.6;">
                ${intelSummary}
            </p>
        </div>`;
    }

    // ── Loading / Error / Empty ──────────────────
    function loading(msg = 'Loading data...') {
        return `<div class="loading-screen"><div class="loader-spinner"></div><p>${msg}</p></div>`;
    }
    function error(msg = 'Something went wrong') {
        return `<div class="error-state"><div class="error-icon">⚠️</div><p>${msg}</p>
            <button class="btn btn-secondary btn-sm" onclick="location.reload()">Retry</button></div>`;
    }
    function empty(msg = 'No data available', icon = '📭') {
        return `<div class="empty-state"><div class="empty-icon">${icon}</div><p>${msg}</p></div>`;
    }

    // ── Page Header ──────────────────────────────
    function pageHeader(title, subtitle = '', breadcrumbs = []) {
        let bc = '';
        if (breadcrumbs.length) {
            bc = '<div class="breadcrumb">' +
                breadcrumbs.map((b, i) =>
                    i < breadcrumbs.length - 1
                        ? `<a href="${b.href}">${b.label}</a> <span>/</span>`
                        : `<span>${b.label}</span>`
                ).join(' ') + '</div>';
        }
        return `
        <div class="page-header">
            ${bc}
            <h1>${title}</h1>
            ${subtitle ? `<p class="subtitle">${subtitle}</p>` : ''}
        </div>`;
    }

    // ── Severity Badge ───────────────────────────
    function severityBadge(severity) {
        const icons = { WARNING: '⚠️', DANGER: '🔶', SEVERE: '🔴' };
        const cls = { WARNING: 'severity-warning', DANGER: 'severity-danger', SEVERE: 'severity-severe' };
        return `<span class="${cls[severity] || ''}">${icons[severity] || '❓'} ${severity}</span>`;
    }

    // ── Sensor Status ────────────────────────────
    function sensorStatus(status) {
        const s = (status || 'unknown').toLowerCase();
        return `<div class="sensor-status">
            <span class="sensor-dot ${s}"></span> ${s.charAt(0).toUpperCase() + s.slice(1)}
        </div>`;
    }

    // ── Time formatting ──────────────────────────
    function formatTime(iso) {
        if (!iso) return '—';
        try {
            const d = new Date(iso);
            return d.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', hour12: true,
                day: 'numeric', month: 'short', year: 'numeric',
                hour: '2-digit', minute: '2-digit' });
        } catch { return iso; }
    }
    function formatTimeShort(iso) {
        if (!iso) return '—';
        try {
            const d = new Date(iso);
            return d.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', hour12: true,
                day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
        } catch { return iso; }
    }

    // ── Chart helpers ────────────────────────────
    let _charts = {};
    function destroyChart(id) {
        if (_charts[id]) { _charts[id].destroy(); delete _charts[id]; }
    }
    function createLineChart(canvasId, labels, datasets, opts = {}) {
        destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        _charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: { labels, datasets },
            options: {
                responsive: true, maintainAspectRatio: false,
                interaction: { intersect: false, mode: 'index' },
                plugins: {
                    legend: { labels: { color: '#8fa3b8', font: { family: 'Inter' } } },
                    tooltip: { backgroundColor: '#1e2d3d', titleColor: '#e8edf2', bodyColor: '#8fa3b8',
                               borderColor: '#2a3f52', borderWidth: 1 },
                },
                scales: {
                    x: { grid: { color: '#1e3044' }, ticks: { color: '#5a7085', maxTicksLimit: 8, font: { size: 10 } } },
                    y: { grid: { color: '#1e3044' }, ticks: { color: '#5a7085', font: { size: 10 } },
                         title: { display: !!opts.yLabel, text: opts.yLabel || '', color: '#5a7085' } },
                },
                ...opts,
            },
        });
        return _charts[canvasId];
    }
    function createBarChart(canvasId, labels, datasets, opts = {}) {
        destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        _charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: { labels, datasets },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#8fa3b8', font: { family: 'Inter' } } },
                },
                scales: {
                    x: { grid: { color: '#1e3044' }, ticks: { color: '#5a7085', font: { size: 10 } } },
                    y: { grid: { color: '#1e3044' }, ticks: { color: '#5a7085', font: { size: 10 } } },
                },
                ...opts,
            },
        });
        return _charts[canvasId];
    }

    return {
        dataBadge, aqiBadge, aqiColor, aqiRing, pollutantCards, statCard,
        intelligenceCard,
        loading, error, empty, pageHeader, severityBadge, sensorStatus,
        formatTime, formatTimeShort, createLineChart, createBarChart, destroyChart,
    };
})();
