/**
 * Page Renderers — each function renders one page into the #page-container.
 * All pages follow: loading → fetch data → render (or error/empty state).
 */
const Pages = (() => {

// ═══════════════════════════════════════════════════
// 1. DASHBOARD
// ═══════════════════════════════════════════════════
async function dashboard(container) {
    container.innerHTML = Components.pageHeader('Dashboard',
        'Real-time air quality overview across Indian cities') + Components.loading('Loading dashboard...');

    try {
        const [readingsResp, alertsResp] = await Promise.all([
            API.getAllReadings(), API.getAlerts()
        ]);
        const readings = readingsResp.readings || [];
        const alerts = (alertsResp.alerts || []).slice(0, 5);

        if (!readings.length) {
            container.innerHTML = Components.pageHeader('Dashboard') + Components.empty('No data available from any city.');
            return;
        }

        // Pick first city with data for featured card
        const featured = readings[0];
        const otherReadings = readings.slice(1, 7);
        
        // Fetch intelligence for featured city
        let intelHtml = '';
        try {
            const summaryResp = await API.getSummary(featured.city_id, 1);
            if (summaryResp.intelligence) {
                intelHtml = Components.intelligenceCard(summaryResp.intelligence);
            }
        } catch (e) { /* ignore */ }

        let alertsHtml = '';
        if (alerts.length) {
            alertsHtml = `<div class="card" style="margin-bottom:var(--spacing-lg)">
                <div class="card-header"><span class="card-title">🔔 Active Alerts</span>
                    <a href="#/alerts" class="btn btn-sm btn-secondary">View All</a></div>
                ${alerts.map(a => `
                    <div class="alert-card ${a.severity.toLowerCase()}" style="margin-bottom:8px">
                        <div class="alert-icon">${{WARNING:'⚠️',DANGER:'🔶',SEVERE:'🔴'}[a.severity]||'❓'}</div>
                        <div class="alert-body">
                            <div class="alert-title">${a.message}</div>
                            <div class="alert-meta">${a.city} • ${a.station} • ${Components.formatTimeShort(a.timestamp)}</div>
                        </div>
                        ${Components.dataBadge(a.data_type)}
                    </div>
                `).join('')}
            </div>`;
        }

        container.innerHTML = `
        ${Components.pageHeader('Dashboard', 'Real-time air quality overview across Indian cities')}

        <div class="refresh-bar">
            <span class="last-updated">Last updated: ${Components.formatTime(readingsResp.timestamp)}</span>
            ${Components.dataBadge(readingsResp.data_type)}
            <button class="btn btn-sm btn-secondary" onclick="Router.reload()">🔄 Refresh</button>
        </div>

        ${intelHtml}
        ${alertsHtml}

        <!-- Featured City AQI -->
        <div class="grid grid-2" style="margin-bottom:var(--spacing-lg)">
            <div class="card" style="cursor:pointer" onclick="Router.navigate('/city/${featured.city_id}')">
                <div class="card-header">
                    <span class="card-title">📍 ${featured.city}</span>
                    ${Components.dataBadge(featured.data_type)}
                </div>
                ${Components.aqiRing(featured.aqi, featured.aqi_category)}
                <p style="text-align:center;color:var(--text-muted);font-size:var(--font-sm);margin-top:8px">
                    ${featured.station_name || ''} • ${Components.formatTimeShort(featured.reading_timestamp)}
                </p>
            </div>
            <div>
                <div class="card-title" style="margin-bottom:var(--spacing-md)">Key Pollutants — ${featured.city}</div>
                ${Components.pollutantCards(featured.pollutants)}
            </div>
        </div>

        <!-- City Comparison -->
        <div class="card" style="margin-bottom:var(--spacing-lg)">
            <div class="card-header">
                <span class="card-title">🏙️ City Comparison</span>
                <a href="#/cities" class="btn btn-sm btn-secondary">View All Cities</a>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead><tr>
                        <th>City</th><th>AQI</th><th>Status</th>
                        <th>PM2.5</th><th>PM10</th><th>Source</th><th>Updated</th>
                    </tr></thead>
                    <tbody>
                        ${readings.map(r => `<tr style="cursor:pointer" onclick="Router.navigate('/city/${r.city_id}')">
                            <td><strong>${r.city}</strong></td>
                            <td><span style="color:${Components.aqiColor(r.aqi)};font-weight:700">${r.aqi ?? '—'}</span></td>
                            <td>${Components.aqiBadge(r.aqi, r.aqi_category)}</td>
                            <td>${r.pollutants?.pm25?.value ?? '—'}</td>
                            <td>${r.pollutants?.pm10?.value ?? '—'}</td>
                            <td>${Components.dataBadge(r.data_type)}</td>
                            <td style="font-size:var(--font-sm);color:var(--text-muted)">${Components.formatTimeShort(r.reading_timestamp)}</td>
                        </tr>`).join('')}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- AQI Bar Chart -->
        <div class="card">
            <div class="card-title" style="margin-bottom:var(--spacing-md)">📊 AQI Comparison Chart</div>
            <div class="chart-container"><canvas id="dash-aqi-chart"></canvas></div>
        </div>`;

        // Render AQI bar chart
        const chartCities = readings.map(r => r.city);
        const chartAQI = readings.map(r => r.aqi || 0);
        const chartColors = readings.map(r => Components.aqiColor(r.aqi));
        Components.createBarChart('dash-aqi-chart', chartCities, [{
            label: 'AQI', data: chartAQI, backgroundColor: chartColors,
            borderColor: chartColors, borderWidth: 1, borderRadius: 6,
        }]);

    } catch (err) {
        container.innerHTML = Components.pageHeader('Dashboard') + Components.error(err.message);
    }
}


// ═══════════════════════════════════════════════════
// 2. LIVE MONITORING
// ═══════════════════════════════════════════════════
async function live(container) {
    container.innerHTML = Components.pageHeader('Live Monitoring',
        'Current air quality readings with real-time data') + Components.loading();

    try {
        const citiesResp = await API.getCities();
        const cities = citiesResp.cities || [];
        const defaultCity = cities[0]?.id || 'delhi';

        container.innerHTML = `
        ${Components.pageHeader('Live Monitoring', 'Current air quality readings')}
        <div class="form-row">
            <div class="form-group">
                <label>City</label>
                <select class="form-control" id="live-city">
                    ${cities.map(c => `<option value="${c.id}" ${c.id === defaultCity ? 'selected' : ''}>${c.name}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Source</label>
                <select class="form-control" id="live-source">
                    <option value="real">Real Data</option>
                    <option value="simulated">Simulated (IoT)</option>
                </select>
            </div>
            <button class="btn btn-primary" id="live-refresh">🔄 Refresh</button>
        </div>
        <div id="live-content">${Components.loading()}</div>`;

        const loadLive = async () => {
            const cityId = document.getElementById('live-city').value;
            const source = document.getElementById('live-source').value;
            const target = document.getElementById('live-content');
            target.innerHTML = Components.loading();

            try {
                let data;
                if (source === 'simulated') {
                    data = await API.getIoTLatest(cityId);
                } else {
                    data = await API.getLatestReading(cityId);
                }
                const reading = data.reading;
                if (!reading) {
                    target.innerHTML = Components.empty(`No ${source} data available for this city.`);
                    return;
                }
                target.innerHTML = `
                <div class="refresh-bar">
                    <span class="last-updated">Reading from: ${Components.formatTime(reading.reading_timestamp)}</span>
                    ${Components.dataBadge(reading.data_type)}
                </div>
                <div class="grid grid-2" style="margin-bottom:var(--spacing-lg)">
                    <div>${Components.aqiRing(reading.aqi, reading.aqi_category)}</div>
                    <div class="card">
                        <div class="card-title" style="margin-bottom:var(--spacing-md)">Station Details</div>
                        <p><strong>City:</strong> ${reading.city}</p>
                        <p><strong>Station:</strong> ${reading.station_name || reading.station_id}</p>
                        <p><strong>Provider:</strong> ${reading.provider || '—'}</p>
                        <p><strong>Source:</strong> ${reading.source || '—'}</p>
                        <p><strong>Dominant Pollutant:</strong> ${reading.dominant_pollutant || '—'}</p>
                        <p><strong>Coordinates:</strong> ${reading.lat ? reading.lat.toFixed(4) + ', ' + reading.lon.toFixed(4) : '—'}</p>
                    </div>
                </div>
                <div class="card-title" style="margin-bottom:var(--spacing-md)">Pollutant Readings</div>
                ${Components.pollutantCards(reading.pollutants)}`;
            } catch (err) {
                target.innerHTML = Components.error(err.message);
            }
        };

        document.getElementById('live-city').addEventListener('change', loadLive);
        document.getElementById('live-source').addEventListener('change', loadLive);
        document.getElementById('live-refresh').addEventListener('click', loadLive);
        loadLive();
    } catch (err) {
        container.innerHTML = Components.pageHeader('Live Monitoring') + Components.error(err.message);
    }
}


// ═══════════════════════════════════════════════════
// 3. CITIES LIST
// ═══════════════════════════════════════════════════
async function cities(container) {
    container.innerHTML = Components.pageHeader('Cities',
        'Air quality across major Indian cities') + Components.loading();

    try {
        const [citiesResp, readingsResp] = await Promise.all([
            API.getCities(), API.getAllReadings()
        ]);
        const cityList = citiesResp.cities || [];
        const readings = readingsResp.readings || [];
        const readingMap = {};
        readings.forEach(r => { readingMap[r.city_id] = r; });

        container.innerHTML = `
        ${Components.pageHeader('Cities', 'Air quality across major Indian cities')}
        <div class="search-bar" style="margin-bottom:var(--spacing-lg)">
            <span>🔍</span>
            <input type="text" id="city-search" placeholder="Search cities...">
        </div>
        <div class="grid grid-auto" id="cities-grid">
            ${cityList.map(c => {
                const r = readingMap[c.id];
                return `
                <div class="city-card" onclick="Router.navigate('/city/${c.id}')" data-name="${c.name.toLowerCase()}">
                    <div class="city-name">${c.name}</div>
                    <div class="city-state">${c.state}${c.note ? ' • ' + c.note : ''}</div>
                    <div class="city-stats">
                        <div class="city-stat-item">
                            <span class="city-stat-label">AQI</span>
                            <span class="city-stat-value" style="color:${Components.aqiColor(r?.aqi)}">${r?.aqi ?? '—'}</span>
                        </div>
                        <div class="city-stat-item">
                            <span class="city-stat-label">PM2.5</span>
                            <span class="city-stat-value">${r?.pollutants?.pm25?.value ?? '—'}</span>
                        </div>
                        <div class="city-stat-item">
                            <span class="city-stat-label">Source</span>
                            <span class="city-stat-value" style="font-size:var(--font-sm)">${Components.dataBadge(r?.data_type)}</span>
                        </div>
                    </div>
                </div>`;
            }).join('')}
        </div>`;

        document.getElementById('city-search').addEventListener('input', (e) => {
            const q = e.target.value.toLowerCase();
            document.querySelectorAll('.city-card').forEach(card => {
                card.style.display = card.dataset.name.includes(q) ? '' : 'none';
            });
        });
    } catch (err) {
        container.innerHTML = Components.pageHeader('Cities') + Components.error(err.message);
    }
}


// ═══════════════════════════════════════════════════
// 4. CITY DETAILS (dynamic route)
// ═══════════════════════════════════════════════════
async function cityDetail(container, cityId) {
    container.innerHTML = Components.pageHeader('City Details', '', [
        { label: 'Cities', href: '#/cities' }, { label: cityId }
    ]) + Components.loading();

    try {
        const [readingResp, stationsResp, summaryResp] = await Promise.all([
            API.getLatestReading(cityId),
            API.getStations(cityId),
            API.getSummary(cityId, 7),
        ]);

        const reading = readingResp.reading;
        const stations = stationsResp.stations || [];
        const summary = summaryResp.summary || {};
        const cityName = reading?.city || cityId;

        container.innerHTML = `
        ${Components.pageHeader(cityName, `Air quality details • ${stations.length} monitoring station(s)`, [
            { label: 'Dashboard', href: '#/dashboard' },
            { label: 'Cities', href: '#/cities' },
            { label: cityName }
        ])}

        ${reading ? `
        <div class="refresh-bar">
            <span class="last-updated">Last reading: ${Components.formatTime(reading.reading_timestamp)}</span>
            ${Components.dataBadge(reading.data_type)}
        </div>

        <div class="grid grid-2" style="margin-bottom:var(--spacing-lg)">
            <div>${Components.aqiRing(reading.aqi, reading.aqi_category)}</div>
            <div>
                <div class="card-title" style="margin-bottom:var(--spacing-md)">Station Info</div>
                <div class="card">
                    <p><strong>Station:</strong> ${reading.station_name || '—'}</p>
                    <p><strong>Provider:</strong> ${reading.provider || '—'}</p>
                    <p><strong>Source:</strong> ${reading.source || '—'}</p>
                    <p><strong>Dominant Pollutant:</strong> ${reading.dominant_pollutant || '—'}</p>
                    <p><strong>Coordinates:</strong> ${reading.lat ? reading.lat.toFixed(4) + ', ' + reading.lon.toFixed(4) : '—'}</p>
                </div>
            </div>
        </div>

        <div class="card-title" style="margin-bottom:var(--spacing-md)">Current Pollutant Readings</div>
        ${Components.pollutantCards(reading.pollutants)}
        ` : Components.empty('No current reading available for this city.')}

        <!-- 7-day Summary -->
        <div class="card" style="margin-top:var(--spacing-lg)">
            <div class="card-header">
                <span class="card-title">📊 7-Day Summary Statistics</span>
            </div>
            ${Object.keys(summary).length ? `
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>Pollutant</th><th>Min</th><th>Avg</th><th>Max</th><th>Readings</th><th>Unit</th></tr></thead>
                    <tbody>
                        ${Object.entries(summary).map(([k, v]) => `
                        <tr>
                            <td><strong>${{pm25:'PM2.5',pm10:'PM10',no2:'NO₂',so2:'SO₂',co:'CO',o3:'O₃'}[k] || k}</strong></td>
                            <td>${v.min ?? '—'}</td>
                            <td>${v.avg ?? '—'}</td>
                            <td>${v.max ?? '—'}</td>
                            <td>${v.count ?? 0}</td>
                            <td>${v.unit || ''}</td>
                        </tr>`).join('')}
                    </tbody>
                </table>
            </div>` : Components.empty('No summary data available yet.')}
        </div>

        <!-- Stations list -->
        <div class="card" style="margin-top:var(--spacing-lg)">
            <div class="card-header">
                <span class="card-title">📡 Monitoring Stations (${stations.length})</span>
            </div>
            ${stations.length ? `
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>Station</th><th>ID</th><th>Provider</th><th>Lat</th><th>Lon</th></tr></thead>
                    <tbody>
                        ${stations.map(s => `
                        <tr>
                            <td><strong>${s.name}</strong></td>
                            <td style="font-size:var(--font-sm);color:var(--text-muted)">${s.station_id}</td>
                            <td>${s.provider || '—'}</td>
                            <td>${s.lat?.toFixed(4) ?? '—'}</td>
                            <td>${s.lon?.toFixed(4) ?? '—'}</td>
                        </tr>`).join('')}
                    </tbody>
                </table>
            </div>` : Components.empty('No stations found via OpenAQ for this city.')}
        </div>

        <!-- Trend chart -->
        <div class="card" style="margin-top:var(--spacing-lg)">
            <div class="card-header">
                <span class="card-title">📈 PM2.5 Trend (7 days)</span>
            </div>
            <div class="chart-container"><canvas id="city-trend-chart"></canvas></div>
        </div>`;

        // Load trend chart
        try {
            const histResp = await API.getHistory(cityId, { pollutant: 'pm25', days: 7 });
            const readings = histResp.readings || [];
            if (readings.length) {
                const labels = readings.map(r => {
                    try { return new Date(r.timestamp).toLocaleDateString('en-IN', {day:'numeric',month:'short'}); }
                    catch { return r.timestamp; }
                });
                Components.createLineChart('city-trend-chart', labels, [{
                    label: 'PM2.5 (µg/m³)', data: readings.map(r => r.value),
                    borderColor: '#4fc3f7', backgroundColor: 'rgba(79,195,247,0.1)',
                    fill: true, tension: 0.3, pointRadius: 2,
                }], { yLabel: 'µg/m³' });
            }
        } catch (e) { /* Chart is non-critical */ }

    } catch (err) {
        container.innerHTML = Components.pageHeader('City Details') + Components.error(err.message);
    }
}


// ═══════════════════════════════════════════════════
// 5. HISTORICAL ANALYTICS
// ═══════════════════════════════════════════════════
async function history(container) {
    container.innerHTML = Components.pageHeader('Historical Analytics',
        'Explore pollution trends over time') + Components.loading();

    try {
        const citiesResp = await API.getCities();
        const cityList = citiesResp.cities || [];

        container.innerHTML = `
        ${Components.pageHeader('Historical Analytics', 'Explore pollution trends over time')}
        <div class="form-row">
            <div class="form-group">
                <label>City</label>
                <select class="form-control" id="hist-city">
                    ${cityList.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Pollutant</label>
                <select class="form-control" id="hist-pollutant">
                    <option value="pm25">PM2.5</option>
                    <option value="pm10">PM10</option>
                    <option value="no2">NO₂</option>
                    <option value="so2">SO₂</option>
                    <option value="co">CO</option>
                    <option value="o3">O₃</option>
                </select>
            </div>
            <div class="form-group">
                <label>Period (Days)</label>
                <select class="form-control" id="hist-days">
                    <option value="3">3 days</option>
                    <option value="7" selected>7 days</option>
                    <option value="14">14 days</option>
                    <option value="30">30 days</option>
                </select>
            </div>
            <button class="btn btn-primary" id="hist-load">📈 Load Data</button>
        </div>
        <div id="hist-content">${Components.empty('Select options and click Load Data', '📈')}</div>`;

        const loadHistory = async () => {
            const cityId = document.getElementById('hist-city').value;
            const pollutant = document.getElementById('hist-pollutant').value;
            const days = document.getElementById('hist-days').value;
            const target = document.getElementById('hist-content');
            target.innerHTML = Components.loading('Loading historical data...');

            try {
                const [histResp, summaryResp] = await Promise.all([
                    API.getHistory(cityId, { pollutant, days }),
                    API.getSummary(cityId, days),
                ]);
                const readings = histResp.readings || [];
                const summary = summaryResp.summary || {};
                const pollSummary = summary[pollutant] || {};

                if (!readings.length) {
                    target.innerHTML = Components.empty('No historical data available for this selection.');
                    return;
                }

                target.innerHTML = `
                <div class="refresh-bar">
                    <span class="last-updated">${readings.length} data points • ${histResp.city_name}</span>
                    ${Components.dataBadge(histResp.data_type)}
                </div>

                <div class="grid grid-4" style="margin-bottom:var(--spacing-lg)">
                    ${Components.statCard('Average', pollSummary.avg, pollSummary.unit || '')}
                    ${Components.statCard('Minimum', pollSummary.min, pollSummary.unit || '')}
                    ${Components.statCard('Maximum', pollSummary.max, pollSummary.unit || '')}
                    ${Components.statCard('Data Points', pollSummary.count)}
                </div>

                <div class="card">
                    <div class="card-title" style="margin-bottom:var(--spacing-md)">
                        ${histResp.pollutant_name || pollutant} Trend — ${histResp.city_name} (${days} days)
                    </div>
                    <div class="chart-container"><canvas id="hist-chart"></canvas></div>
                </div>`;

                const labels = readings.map(r => {
                    try { return new Date(r.timestamp).toLocaleDateString('en-IN', {day:'numeric',month:'short',hour:'2-digit'}); }
                    catch { return r.timestamp; }
                });
                Components.createLineChart('hist-chart', labels, [{
                    label: `${histResp.pollutant_name || pollutant} (${histResp.unit || ''})`,
                    data: readings.map(r => r.value),
                    borderColor: '#4fc3f7', backgroundColor: 'rgba(79,195,247,0.1)',
                    fill: true, tension: 0.3, pointRadius: 1,
                }], { yLabel: histResp.unit || '' });

            } catch (err) {
                target.innerHTML = Components.error(err.message);
            }
        };

        document.getElementById('hist-load').addEventListener('click', loadHistory);
        // Auto-load on dropdown change
        ['hist-city', 'hist-pollutant', 'hist-days'].forEach(id => {
            document.getElementById(id).addEventListener('change', loadHistory);
        });
    } catch (err) {
        container.innerHTML = Components.pageHeader('Historical Analytics') + Components.error(err.message);
    }
}


// ═══════════════════════════════════════════════════
// 6. FORECAST 
// ═══════════════════════════════════════════════════
async function forecast(container) {
    container.innerHTML = Components.pageHeader('Air Quality Forecast',
        'AI-powered pollution predictions using machine learning') + Components.loading();

    try {
        const citiesResp = await API.getCities();
        const cityList = citiesResp.cities || [];
        const defaultCity = cityList[0]?.id || 'delhi';

        container.innerHTML = `
        ${Components.pageHeader('Air Quality Forecast', 'AI-powered pollution predictions')}
        <div class="form-row">
            <div class="form-group">
                <label>City</label>
                <select class="form-control" id="fc-city">
                    ${cityList.map(c => `<option value="${c.id}" ${c.id === defaultCity ? 'selected' : ''}>${c.name}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Pollutant</label>
                <select class="form-control" id="fc-pollutant">
                    <option value="pm25">PM2.5</option>
                    <option value="pm10">PM10</option>
                </select>
            </div>
            <div class="form-group">
                <label>Forecast Horizon</label>
                <select class="form-control" id="fc-horizon">
                    <option value="24" selected>Short-term (24 hours)</option>
                    <option value="72">Medium-term (3 days)</option>
                    <option value="168">Long-term (7 days)</option>
                </select>
            </div>
            <button class="btn btn-primary" id="fc-load">🔮 Generate Forecast</button>
        </div>
        
        <div class="alert-card warning" style="margin-bottom:var(--spacing-lg)">
            <div class="alert-icon">⚠️</div>
            <div class="alert-body">
                <div class="alert-title">Estimates Only</div>
                <div class="alert-meta">Forecasts are model-generated estimates based on historical trends. They are not guaranteed future measurements.</div>
            </div>
        </div>

        <div id="fc-content">${Components.empty('Select options and click Generate Forecast', '🔮')}</div>`;

        const loadForecast = async () => {
            const cityId = document.getElementById('fc-city').value;
            const pollutant = document.getElementById('fc-pollutant').value;
            const horizon = document.getElementById('fc-horizon').value;
            const target = document.getElementById('fc-content');
            
            target.innerHTML = Components.loading('Training model and generating forecast...');

            try {
                // Get historical data for the chart context
                const histResp = await API.getHistory(cityId, { pollutant, days: 3 });
                const history = histResp.readings || [];
                
                // Get forecast
                const fcResp = await API.getForecast(cityId, { pollutant, horizon });
                const forecastData = fcResp.forecast || [];
                const metrics = fcResp.metrics || {};
                
                if (!forecastData.length) {
                    target.innerHTML = Components.empty('Insufficient historical data to generate a forecast.');
                    return;
                }

                target.innerHTML = `
                <div class="refresh-bar">
                    <span class="last-updated">Generated: ${Components.formatTime(fcResp.timestamp)}</span>
                    ${Components.dataBadge(fcResp.data_type)}
                </div>

                <div class="grid grid-3" style="margin-bottom:var(--spacing-lg)">
                    ${Components.statCard('Model', fcResp.model || 'Random Forest')}
                    ${Components.statCard('MAE (Error)', metrics.mae ?? '—', fcResp.unit)}
                    ${Components.statCard('RMSE', metrics.rmse ?? '—', fcResp.unit)}
                </div>

                <div class="card">
                    <div class="card-title" style="margin-bottom:var(--spacing-md)">
                        ${fcResp.pollutant_name} Forecast — ${fcResp.city_name}
                    </div>
                    <div class="chart-container"><canvas id="fc-chart"></canvas></div>
                </div>`;

                // Render Chart with historical and predicted
                const labels = [];
                const histValues = [];
                const predValues = [];
                
                // Add historical data
                history.forEach(r => {
                    labels.push(Components.formatTimeShort(r.timestamp));
                    histValues.push(r.value);
                    predValues.push(null);
                });
                
                // If there's data, connect the lines
                if (history.length && forecastData.length) {
                    const lastHist = history[history.length-1];
                    labels.push(Components.formatTimeShort(lastHist.timestamp) + ' (Now)');
                    histValues.push(lastHist.value);
                    predValues.push(lastHist.value);
                }

                // Add forecast data
                forecastData.forEach(r => {
                    labels.push(Components.formatTimeShort(r.timestamp));
                    histValues.push(null);
                    predValues.push(r.value);
                });

                Components.createLineChart('fc-chart', labels, [
                    {
                        label: `Historical ${fcResp.pollutant_name} (${fcResp.unit})`,
                        data: histValues,
                        borderColor: '#8fa3b8', 
                        backgroundColor: 'rgba(143,163,184,0.1)',
                        fill: true, tension: 0.3, pointRadius: 2,
                    },
                    {
                        label: `Predicted ${fcResp.pollutant_name} (${fcResp.unit})`,
                        data: predValues,
                        borderColor: '#ab47bc', 
                        backgroundColor: 'rgba(171,71,188,0.1)',
                        borderDash: [5, 5],
                        fill: true, tension: 0.3, pointRadius: 2,
                    }
                ], { yLabel: fcResp.unit });

            } catch (err) {
                target.innerHTML = Components.error(err.message);
            }
        };

        document.getElementById('fc-load').addEventListener('click', loadForecast);
        
        // Auto load initial
        loadForecast();

    } catch (err) {
        container.innerHTML = Components.pageHeader('Forecast') + Components.error(err.message);
    }
}


// ═══════════════════════════════════════════════════
// 7. ALERTS
// ═══════════════════════════════════════════════════
async function alerts(container) {
    container.innerHTML = Components.pageHeader('Alerts',
        'Pollution threshold breach notifications') + Components.loading();

    try {
        const alertsResp = await API.getAlerts();
        const alertList = alertsResp.alerts || [];
        const thresholds = alertsResp.thresholds || {};

        container.innerHTML = `
        ${Components.pageHeader('Alerts', 'Pollution threshold breach notifications')}

        <div class="refresh-bar">
            <span class="last-updated">${alertList.length} active alert(s)</span>
            <button class="btn btn-sm btn-secondary" onclick="Router.reload()">🔄 Refresh</button>
        </div>

        ${alertList.length ? `
        <div style="margin-bottom:var(--spacing-xl)">
            ${alertList.map(a => `
            <div class="alert-card ${a.severity.toLowerCase()}" style="margin-bottom:var(--spacing-sm)">
                <div class="alert-icon">${{WARNING:'⚠️',DANGER:'🔶',SEVERE:'🔴'}[a.severity] || '❓'}</div>
                <div class="alert-body">
                    <div class="alert-title">${a.message}</div>
                    <div class="alert-meta">
                        📍 ${a.city} • ${a.station} •
                        ${a.pollutant_name}: <strong>${a.value}${a.unit}</strong> (threshold: ${a.threshold}${a.unit}) •
                        ${Components.formatTimeShort(a.timestamp)}
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px">
                    ${Components.severityBadge(a.severity)}
                    ${Components.dataBadge(a.data_type)}
                </div>
            </div>`).join('')}
        </div>` : Components.empty('No active alerts. All readings are within safe limits.', '✅')}

        <!-- Threshold Reference -->
        <div class="card">
            <div class="card-title" style="margin-bottom:var(--spacing-md)">📋 Configured Thresholds</div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>Pollutant</th><th>Warning</th><th>Danger</th><th>Severe</th><th>Unit</th></tr></thead>
                    <tbody>
                        ${Object.entries(thresholds).map(([k, t]) => `
                        <tr>
                            <td><strong>${{pm25:'PM2.5',pm10:'PM10',no2:'NO₂',so2:'SO₂',co:'CO',o3:'O₃',aqi:'AQI'}[k] || k}</strong></td>
                            <td class="severity-warning">${t.warning}</td>
                            <td class="severity-danger">${t.danger}</td>
                            <td class="severity-severe">${t.severe}</td>
                            <td>${t.unit || '—'}</td>
                        </tr>`).join('')}
                    </tbody>
                </table>
            </div>
        </div>`;
    } catch (err) {
        container.innerHTML = Components.pageHeader('Alerts') + Components.error(err.message);
    }
}


// ═══════════════════════════════════════════════════
// 8. IOT SENSORS
// ═══════════════════════════════════════════════════
async function sensors(container) {
    container.innerHTML = Components.pageHeader('IoT Sensors',
        'Simulated sensor network for IoT concept demonstration') + Components.loading();

    try {
        const sensorsResp = await API.getSensors();
        const sensorList = sensorsResp.sensors || [];

        container.innerHTML = `
        ${Components.pageHeader('IoT Sensors',
            'Simulated sensor network — demonstrates IoT concepts without physical hardware')}

        <div class="alert-card info" style="margin-bottom:var(--spacing-lg)">
            <div class="alert-icon">ℹ️</div>
            <div class="alert-body">
                <div class="alert-title">IoT Simulation Mode Active</div>
                <div class="alert-meta">All sensors listed below are virtual. They simulate realistic hardware behavior, drift, and failures for assessment purposes.</div>
            </div>
        </div>

        <div class="refresh-bar">
            <span class="last-updated">${sensorList.length} virtual sensor(s) deployed</span>
            ${Components.dataBadge('SIMULATED')}
            <button class="btn btn-sm btn-primary" id="sensors-refresh">⚡ Generate Readings</button>
        </div>

        <div class="grid grid-auto" id="sensors-grid">
            ${sensorList.map(s => `
            <div class="card" id="sensor-card-${s.sensor_id}">
                <div class="card-header">
                    <span class="card-title">📟 ${s.sensor_id}</span>
                    ${Components.sensorStatus(s.status)}
                </div>
                <p><strong>City:</strong> ${s.city}</p>
                <p><strong>Station:</strong> ${s.station_name}</p>
                <p><strong>Last Seen:</strong> ${Components.formatTimeShort(s.last_seen)}</p>
                <p><strong>Interval:</strong> ${s.interval_seconds}s</p>
                ${Components.dataBadge('SIMULATED')}
                <div id="sensor-reading-${s.sensor_id}" style="margin-top:var(--spacing-md)">
                    <button class="btn btn-sm btn-secondary" onclick="Pages._loadSensorReading('${s.sensor_id}')">
                        📊 Get Reading
                    </button>
                </div>
            </div>`).join('')}
        </div>`;

        document.getElementById('sensors-refresh').addEventListener('click', async () => {
            for (const s of sensorList) {
                await Pages._loadSensorReading(s.sensor_id);
            }
        });
    } catch (err) {
        container.innerHTML = Components.pageHeader('IoT Sensors') + Components.error(err.message);
    }
}

async function _loadSensorReading(sensorId) {
    const target = document.getElementById(`sensor-reading-${sensorId}`);
    if (!target) return;
    target.innerHTML = '<div class="loader-spinner" style="width:20px;height:20px;border-width:2px"></div>';
    try {
        const resp = await API.getSensorReading(sensorId);
        const r = resp.reading;
        if (!r) { target.innerHTML = 'No reading'; return; }
        const pollutantHtml = Object.entries(r.pollutants || {}).map(([k, v]) => {
            if (v.value === null) return '';
            return `<span style="margin-right:12px"><strong>${k.toUpperCase()}:</strong> ${v.value} ${v.unit}</span>`;
        }).filter(Boolean).join('');
        target.innerHTML = `
            <div style="font-size:var(--font-sm);color:var(--text-secondary);margin-top:4px">
                <div>AQI: <strong style="color:${Components.aqiColor(r.aqi)}">${r.aqi ?? '—'}</strong>
                    ${r.aqi_category ? `(${r.aqi_category})` : ''}</div>
                <div style="margin-top:4px">${pollutantHtml}</div>
                <div style="margin-top:4px;color:var(--text-muted)">${Components.formatTimeShort(r.reading_timestamp)}</div>
            </div>
            <button class="btn btn-sm btn-secondary" style="margin-top:8px"
                onclick="Pages._loadSensorReading('${sensorId}')">🔄 Refresh</button>`;
    } catch (err) {
        target.innerHTML = `<span class="error-state" style="min-height:auto;padding:4px">${err.message}</span>`;
    }
}


// ═══════════════════════════════════════════════════
// 9. ABOUT / METHODOLOGY
// ═══════════════════════════════════════════════════
async function about(container) {
    container.innerHTML = `
    ${Components.pageHeader('About & Methodology', 'Understanding the Smart Air Pollution Monitoring Portal')}

    <div class="about-section">
        <h2>🌍 The Problem</h2>
        <p>Air pollution is one of the most pressing environmental challenges facing Indian cities.
           Particulate matter (PM2.5, PM10), nitrogen dioxide (NO₂), sulfur dioxide (SO₂),
           carbon monoxide (CO), and ground-level ozone (O₃) affect millions of people daily.
           The Air Quality Index (AQI) provides a standardized way to communicate how polluted
           the air currently is.</p>
        <p>This portal makes real-time, official air quality data accessible through
           a clean, modern dashboard — helping citizens, researchers, and decision-makers
           understand pollution patterns across major Indian cities.</p>
    </div>

    <div class="about-section">
        <h2>🎯 Project Objective</h2>
        <p>Build a <strong>Smart Air Pollution Monitoring Portal</strong> that demonstrates
           two key computing concepts:</p>
        <div class="feature-grid">
            <div class="feature-item">
                <div class="feat-icon">📟</div>
                <div class="feat-title">IoT (Internet of Things)</div>
                <div class="feat-desc">Simulated sensor network generating realistic pollution readings</div>
            </div>
            <div class="feature-item">
                <div class="feat-icon">📊</div>
                <div class="feat-title">Dashboards</div>
                <div class="feat-desc">Interactive data visualization with charts, cards, and tables</div>
            </div>
            <div class="feature-item">
                <div class="feat-icon">🔗</div>
                <div class="feat-title">REST APIs</div>
                <div class="feat-desc">Clean separation between data layer and presentation</div>
            </div>
            <div class="feature-item">
                <div class="feat-icon">🔮</div>
                <div class="feat-title">Forecasting (Future)</div>
                <div class="feat-desc">ML-based AQI prediction using historical data</div>
            </div>
        </div>
    </div>

    <div class="about-section">
        <h2>📡 IoT Concept</h2>
        <p>Physical IoT sensors for air quality (such as those using SDS011 particulate sensors)
           are expensive and require specific hardware. This project <strong>simulates</strong>
           the IoT data pipeline entirely in software:</p>
        <ul>
            <li><strong>Virtual Sensors:</strong> One simulated sensor per city, each with a unique ID (SIM-SENSOR-XX)</li>
            <li><strong>Realistic Data:</strong> Generated values use statistical baselines derived from real city pollution profiles, with time-of-day variation</li>
            <li><strong>Clearly Labelled:</strong> Every simulated reading is tagged <strong>SIMULATED</strong> — never mistaken for official government data</li>
            <li><strong>IoT Flow:</strong> Simulated Sensor → Backend → REST API → Dashboard (same as a real sensor would follow)</li>
        </ul>
    </div>

    <div class="about-section">
        <h2>🗄️ Data Sources</h2>
        <h3>Primary: OpenAQ API v3</h3>
        <p>OpenAQ is a non-profit platform that aggregates air quality data from government monitoring
           networks worldwide. For India, it sources data from the <strong>Central Pollution Control Board (CPCB)</strong>,
           the statutory authority under the Ministry of Environment.</p>
        <ul>
            <li>API: <code>https://api.openaq.org/v3/</code></li>
            <li>Data provider: CPCB (Government of India)</li>
            <li>Coverage: 100+ Indian cities with reference-grade monitors</li>
            <li>Free API key required (registration at explore.openaq.org)</li>
        </ul>

        <h3>Secondary: Open Government Data (OGD) India</h3>
        <p>India's official open data platform (data.gov.in) provides historical bulk datasets
           used for fallback data when the live API is unavailable.</p>

        <h3>IoT Simulator</h3>
        <p>Internal software module generating synthetic readings — clearly marked
           <strong>SIMULATED</strong> at every level.</p>
    </div>

    <div class="about-section">
        <h2>🏗️ Architecture</h2>
        <pre style="background:var(--bg-tertiary);padding:var(--spacing-lg);border-radius:var(--radius-md);overflow-x:auto;color:var(--text-secondary);font-size:var(--font-sm);line-height:1.8">
┌───────────────────────────────────────────────────┐
│               DATA SOURCES                        │
│  OpenAQ API (CPCB)  │  OGD India  │  IoT Sim     │
└──────────┬──────────────────┬──────────┬──────────┘
           │                  │          │
           ▼                  ▼          ▼
┌───────────────────────────────────────────────────┐
│                  BACKEND (Flask)                  │
│  Ingestion → Cache → AQI Calc → REST API         │
└─────────────────────┬─────────────────────────────┘
                      │  JSON
                      ▼
┌───────────────────────────────────────────────────┐
│                FRONTEND (HTML/JS)                 │
│  Dashboard │ Live │ Cities │ History │ Alerts     │
└───────────────────────────────────────────────────┘</pre>
        <p>The frontend <strong>never</strong> contacts external APIs directly.
           All data flows through the Flask backend, which handles caching, error recovery,
           and data-type tagging.</p>
    </div>

    <div class="about-section">
        <h2>🔬 Pollutants Monitored</h2>
        <div class="table-wrapper">
            <table>
                <thead><tr><th>Pollutant</th><th>Full Name</th><th>Unit</th><th>Health Impact</th></tr></thead>
                <tbody>
                    <tr><td><strong>PM2.5</strong></td><td>Fine Particulate Matter</td><td>µg/m³</td><td>Penetrates deep into lungs; major health risk</td></tr>
                    <tr><td><strong>PM10</strong></td><td>Coarse Particulate Matter</td><td>µg/m³</td><td>Causes respiratory irritation</td></tr>
                    <tr><td><strong>NO₂</strong></td><td>Nitrogen Dioxide</td><td>µg/m³</td><td>Irritates airways; from vehicle emissions</td></tr>
                    <tr><td><strong>SO₂</strong></td><td>Sulfur Dioxide</td><td>µg/m³</td><td>Causes acid rain; from industrial activity</td></tr>
                    <tr><td><strong>CO</strong></td><td>Carbon Monoxide</td><td>mg/m³</td><td>Reduces oxygen in blood; from combustion</td></tr>
                    <tr><td><strong>O₃</strong></td><td>Ground-level Ozone</td><td>µg/m³</td><td>Causes breathing problems; formed by sunlight + pollution</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <div class="about-section">
        <h2>🏷️ Data Integrity</h2>
        <p>This project <strong>never fabricates real pollution measurements</strong>.
           Every data point is clearly tagged:</p>
        <div style="display:flex;gap:var(--spacing-lg);flex-wrap:wrap;margin-top:var(--spacing-md)">
            <div>${Components.dataBadge('REAL')} — Official CPCB data via OpenAQ</div>
            <div>${Components.dataBadge('SIMULATED')} — IoT simulator (software-generated)</div>
            <div>${Components.dataBadge('FALLBACK')} — Pre-downloaded static dataset</div>
            <div>${Components.dataBadge('PREDICTED')} — ML forecast (future)</div>
        </div>
    </div>

    <div class="about-section">
        <h2>🛠️ Technology Stack</h2>
        <div class="table-wrapper">
            <table>
                <thead><tr><th>Layer</th><th>Technology</th><th>Reason</th></tr></thead>
                <tbody>
                    <tr><td>Backend</td><td>Python + Flask</td><td>Lightweight, college-friendly</td></tr>
                    <tr><td>Data Source</td><td>OpenAQ API v3</td><td>Official CPCB data aggregator</td></tr>
                    <tr><td>Frontend</td><td>HTML + CSS + JS</td><td>No build step needed</td></tr>
                    <tr><td>Charts</td><td>Chart.js (CDN)</td><td>Zero-install charting</td></tr>
                    <tr><td>Cache</td><td>File-based JSON</td><td>No database needed</td></tr>
                    <tr><td>ML (Future)</td><td>scikit-learn</td><td>Standard ML library</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <div class="about-section" style="text-align:center">
        <p style="color:var(--text-muted);font-size:var(--font-sm)">
            Smart Air Pollution Monitoring Portal — College Assessment Project<br>
            Concepts: IoT and Dashboards • Individual Vibe Coding Assessment
        </p>
    </div>`;
}

    return {
        dashboard, live, cities, cityDetail, history, forecast, alerts, sensors, about,
        _loadSensorReading,
    };
})();
