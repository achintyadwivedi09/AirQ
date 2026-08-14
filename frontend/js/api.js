/**
 * API Service Layer — all backend communication goes through here.
 * The frontend NEVER contacts OpenAQ or any external API directly.
 */
const API = (() => {
    const BASE = '/api';

    async function _fetch(endpoint, params = {}) {
        const url = new URL(endpoint, window.location.origin);
        Object.entries(params).forEach(([k, v]) => {
            if (v !== undefined && v !== null && v !== '') {
                url.searchParams.set(k, v);
            }
        });

        try {
            const resp = await fetch(url.toString());
            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                throw new Error(err.error || `HTTP ${resp.status}`);
            }
            return await resp.json();
        } catch (err) {
            if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
                throw new Error('Backend is not reachable. Make sure the server is running on http://localhost:5000');
            }
            throw err;
        }
    }

    return {
        getCities: ()                   => _fetch(`${BASE}/cities`),
        getStations: (city)             => _fetch(`${BASE}/stations`, { city }),
        getLatestReading: (city, opts={}) => _fetch(`${BASE}/readings/latest`, { city, ...opts }),
        getAllReadings: (city)           => _fetch(`${BASE}/readings`, { city }),
        getHistory: (city, opts={})     => _fetch(`${BASE}/history`, { city, ...opts }),
        getSummary: (city, days)        => _fetch(`${BASE}/summary`, { city, days }),
        getSensors: (city)              => _fetch(`${BASE}/sensors`, { city }),
        getSensorDetail: (id)           => _fetch(`${BASE}/sensors/${id}`),
        getSensorReading: (id)          => _fetch(`${BASE}/sensors/${id}/reading`),
        getIoTLatest: (city)            => _fetch(`${BASE}/iot/latest`, { city }),
        getAlerts: (city)               => _fetch(`${BASE}/alerts`, { city }),
        getForecast: (city, opts={})    => _fetch(`${BASE}/forecast`, { city, ...opts }),
        healthCheck: ()                 => _fetch(`${BASE}/health`),
    };
})();
