/* app.js — Frontend Logic for Resilienz.AI */

const API_BASE = (window.API_BASE_URL || "http://127.0.0.1:5000/api");

// ── Tab Switching ────────────────────────────────────────────────────────────
let mapInitialized = false;
let currentMap = null;
let thoughtSource = null;

function showTab(tabName) {
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    
    document.getElementById(`tab-${tabName}`).classList.add('active');
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
    
    if (tabName === 'map' && !mapInitialized) {
        loadMapTab();
        mapInitialized = true;
    }
    
    if (tabName === 'map' && currentMap) {
        setTimeout(() => { currentMap.invalidateSize(); }, 100);
    }
}

// ── Dashboard Metrics ────────────────────────────────────────────────────────
async function loadSummary() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/summary`);
        const data = await res.json();
        
        document.getElementById('stat-suppliers').innerText = data.suppliers;
        document.getElementById('stat-orders').innerText = data.orders;
        document.getElementById('stat-delayed').innerText = data.delayed;
        document.getElementById('stat-parts').innerText = data.inventory;
    } catch (e) {
        console.error("Failed to load metrics", e);
    }
}

// ── Global Map ───────────────────────────────────────────────────────────────
async function loadMapTab() {
    const container = document.getElementById('map-container');
    
    if (!navigator.onLine) {
        container.innerHTML = '<div class="map-offline"><p>🌍 Map unavailable offline</p><p style="font-size:11px;color:var(--text-dim)">Connect to internet to view the Global Risk Map</p></div>';
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/map/data`);
        const data = await res.json();
        initMap(data);
    } catch (e) {
        container.innerHTML = '<div class="map-offline"><p>❌ Failed to load map data</p><p style="font-size:11px;color:var(--text-dim)">Is the API server running?</p></div>';
    }
}

function initMap(data) {
    const container = document.getElementById('map-container');
    
    const map = L.map('map-container', {
        center: [50, 10],
        zoom: 4,
        zoomControl: true,
    });
    currentMap = map;

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> © <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 18,
    }).addTo(map);

    const hub = data.hub;
    const suppliers = data.suppliers;
    const affectedIds = new Set();

    if (data.active_scenario) {
        fetch(`${API_BASE}/scenario/status`)
            .then(r => r.json())
            .then(s => {
                s.affected_suppliers.forEach(id => affectedIds.add(id));
                redrawMapWithAffected(data, map, affectedIds);
            })
            .catch(() => redrawMapWithAffected(data, map, affectedIds));
    } else {
        redrawMapWithAffected(data, map, affectedIds);
    }

    addMapLegend(map);

    if (typeof redrawMapWithAffected === 'undefined') {
        // inline
    }
}

function redrawMapWithAffected(data, map, affectedIds) {
    const hub = data.hub;
    const suppliers = data.suppliers;
    const hubLatLng = [hub.lat, hub.lon];

    const hubIcon = L.divIcon({
        html: '<div style="background:#818cff;width:16px;height:16px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 12px #818cff;"></div>',
        className: '',
        iconSize: [16, 16],
        iconAnchor: [8, 8],
    });

    L.marker(hubLatLng, { icon: hubIcon })
        .addTo(map)
        .bindPopup(`<div class="map-popup-name">${hub.name}</div><div class="map-popup-row"><span>Type</span><span>Factory HQ</span></div>`);

    const riskColors = {
        HIGH: '#ff4d4d',
        MEDIUM: '#ffc14d',
        LOW: '#2ed573',
    };

    suppliers.forEach(s => {
        const isAffected = affectedIds.has(s.supplier_id);
        const color = isAffected ? '#ff6b35' : riskColors[s.risk_category] || '#ffc14d';
        const isPulsing = isAffected || s.risk_category === 'HIGH';

        const markerHtml = isPulsing
            ? `<div style="background:${color};width:12px;height:12px;border-radius:50%;border:2px solid rgba(255,255,255,0.3);box-shadow:0 0 ${isAffected ? '12px' : '8px'} ${color};animation:pulse-hotspot 1.5s infinite;"></div>`
            : `<div style="background:${color};width:10px;height:10px;border-radius:50%;border:2px solid rgba(255,255,255,0.3);box-shadow:0 0 6px ${color};"></div>`;

        const marker = L.marker([s.lat, s.lon], {
            icon: L.divIcon({ html: markerHtml, className: '', iconSize: [14, 14], iconAnchor: [7, 7] }),
        }).addTo(map);

        const delayText = s.current_delay_days > 0 ? `<div class="map-popup-row"><span>Delay</span><span style="color:#ff4d4d">+${s.current_delay_days}d</span></div>` : '';
        const affectedText = isAffected ? `<div class="map-popup-row"><span>Status</span><span style="color:#ff6b35;font-weight:600;">⚡ Affected</span></div>` : '';

        marker.bindPopup(`
            <div class="map-popup-name">${s.name}</div>
            <div class="map-popup-row"><span>Location</span><span>${s.city}, ${s.country}</span></div>
            <div class="map-popup-row"><span>Risk</span><span style="color:${riskColors[s.risk_category]}">${s.risk_category}</span></div>
            <div class="map-popup-row"><span>Reliability</span><span>${(s.reliability_score * 100).toFixed(0)}%</span></div>
            <div class="map-popup-row"><span>Active POs</span><span>${s.active_pos}</span></div>
            ${delayText}
            ${affectedText}
        `);

        const lineColor = isAffected ? 'rgba(255, 107, 53, 0.5)' : 'rgba(255, 255, 255, 0.15)';
        const lineWeight = isAffected ? 2 : 1;
        L.polyline([hubLatLng, [s.lat, s.lon]], {
            color: lineColor,
            weight: lineWeight,
            dashArray: isAffected ? '5, 8' : null,
        }).addTo(map);
    });
}

function addMapLegend(map) {
    const legend = L.control({ position: 'bottomleft' });
    legend.onAdd = function () {
        const div = L.DomUtil.create('div', 'map-legend');
        div.innerHTML = `
            <div class="map-legend-title">Risk Level</div>
            <div class="legend-item"><span class="legend-dot hub"></span>Factory HQ</div>
            <div class="legend-item"><span class="legend-dot high"></span>High Risk</div>
            <div class="legend-item"><span class="legend-dot medium"></span>Medium Risk</div>
            <div class="legend-item"><span class="legend-dot low"></span>Low Risk</div>
            <div class="map-legend-title" style="margin-top:10px;">Connection</div>
            <div class="legend-item"><span class="legend-line normal"></span>Normal Route</div>
            <div class="legend-item"><span class="legend-dot affected"></span>Affected Route</div>
        `;
        return div;
    };
    legend.addTo(map);
}

// ── Scenario Controls ────────────────────────────────────────────────────────
const scenarioSelector = document.getElementById('scenario-selector');
const triggerBtn = document.getElementById('trigger-scenario-btn');
const resetBtn = document.getElementById('reset-scenario-btn');
const scenarioBadge = document.getElementById('scenario-badge');
const scenarioNameEl = document.getElementById('scenario-name');

async function loadScenarioStatus() {
    try {
        const res = await fetch(`${API_BASE}/scenario/status`);
        const data = await res.json();
        if (data.active) {
            scenarioBadge.style.display = 'inline-flex';
            scenarioNameEl.textContent = data.active.replace(/_/g, ' ');
            scenarioSelector.value = data.active;
        }
    } catch (e) {
        // ignore
    }
}

async function triggerScenario() {
    const scenarioId = scenarioSelector.value;
    if (!scenarioId) {
        showToast('Select a scenario first', 'warning');
        return;
    }

    triggerBtn.disabled = true;
    triggerBtn.innerText = '⏳ Applying...';

    try {
        const res = await fetch(`${API_BASE}/scenario/trigger`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_id: scenarioId }),
        });
        const data = await res.json();

        if (!res.ok) {
            showToast(data.error || 'Failed to trigger scenario', 'error');
            return;
        }

        scenarioBadge.style.display = 'inline-flex';
        scenarioNameEl.textContent = data.scenario;
        showToast(`⚡ ${data.scenario} active — ${data.affected_suppliers} suppliers affected`, 'success');
        
        loadSummary();
        loadInventory();
        
        if (mapInitialized && currentMap) {
            loadMapTab();
        }
    } catch (e) {
        showToast('Connection error', 'error');
    } finally {
        triggerBtn.disabled = false;
        triggerBtn.innerHTML = '⚡ Trigger';
    }
}

async function resetScenario() {
    resetBtn.disabled = true;
    resetBtn.innerText = '⏳ Resetting...';

    try {
        const res = await fetch(`${API_BASE}/scenario/reset`, { method: 'POST' });
        const data = await res.json();

        if (!res.ok) {
            showToast(data.error || 'Nothing to reset', 'warning');
            return;
        }

        scenarioBadge.style.display = 'none';
        scenarioSelector.value = '';
        showToast('🔄 Data reset to baseline', 'success');
        
        loadSummary();
        loadInventory();
        
        if (mapInitialized && currentMap) {
            loadMapTab();
        }
    } catch (e) {
        showToast('Connection error', 'error');
    } finally {
        resetBtn.disabled = false;
        resetBtn.innerText = '🔄 Reset';
    }
}

triggerBtn.addEventListener('click', triggerScenario);
resetBtn.addEventListener('click', resetScenario);

function showToast(message, type) {
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        padding: 12px 24px;
        border-radius: 10px;
        font-size: 13px;
        font-family: 'Outfit', sans-serif;
        z-index: 9999;
        animation: fadeIn 0.3s ease;
        background: rgba(11, 14, 20, 0.95);
        border: 1px solid var(--border);
        color: var(--text-main);
        backdrop-filter: blur(10px);
    `;
    if (type === 'success') toast.style.borderColor = '#2ed573';
    if (type === 'error') toast.style.borderColor = '#ff4d4d';
    if (type === 'warning') toast.style.borderColor = '#ffc14d';

    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

// ── Thought Trace (SSE) ──────────────────────────────────────────────────────
function startThoughtTrace() {
    const trace = document.getElementById('thought-trace');
    const log = document.getElementById('thought-log');
    const header = document.getElementById('thought-header');
    
    trace.style.display = 'block';
    log.innerHTML = '';
    header.innerHTML = '<span class="pulse amber"></span>🧠 AI is reasoning...';
    
    thoughtSource = new EventSource(`${API_BASE}/stream/thoughts`);
    
    thoughtSource.onmessage = (e) => {
        const data = JSON.parse(e.data);
        addThoughtItem(data.step, data.detail || '');
        
        if (data.step === 'Done' || data.step === 'Error') {
            thoughtSource.close();
            thoughtSource = null;
            if (data.step === 'Done') {
                header.innerHTML = '<span class="pulse green"></span>✅ Reasoning complete';
            } else {
                header.innerHTML = '<span class="pulse" style="background:#ff4d4d;box-shadow:0 0 10px #ff4d4d;"></span>❌ Reasoning failed';
            }
        }
    };
    
    thoughtSource.onerror = () => {
        if (thoughtSource) {
            thoughtSource.close();
            thoughtSource = null;
        }
    };
}

function addThoughtItem(step, detail) {
    const log = document.getElementById('thought-log');
    const item = document.createElement('div');
    item.className = 'thought-item' + (step === 'Done' ? ' done' : '') + (step === 'Error' ? ' error' : '');
    const time = new Date().toLocaleTimeString();
    item.innerHTML = `<span class="t-time">${time}</span><b>${step}</b>${detail ? ' — ' + detail : ''}`;
    log.appendChild(item);
    log.scrollTop = log.scrollHeight;
}

// ── Audit Logic ──────────────────────────────────────────────────────────────
const runBtn = document.getElementById('run-audit-btn');
const auditPlaceholder = document.getElementById('audit-placeholder');
const auditResults = document.getElementById('audit-results');

runBtn.addEventListener('click', async () => {
    startThoughtTrace();
    
    auditPlaceholder.style.display = 'none';
    auditResults.style.display = 'none';
    
    runBtn.innerText = "🧠 R_agent is thinking...";
    runBtn.disabled = true;
    
    try {
        const res = await fetch(`${API_BASE}/agent/audit`, { method: 'POST' });
        const data = await res.json();
        
        auditResults.style.display = 'block';
        auditResults.innerHTML = parseMarkdown(data.report) || "<p>No results returned.</p>";
        
    } catch (e) {
        addThoughtItem('Error', 'Connection failed. Is the API server running?');
        auditResults.innerHTML = "<p>❌ Connection failed. Is the API server running?</p>";
        auditResults.style.display = 'block';
    } finally {
        runBtn.innerText = "🚀 Start Audit";
        runBtn.disabled = false;
        loadSummary();
    }
});

// ── Markdown Parser ───────────────────────────────────────────────────────────
function parseMarkdown(text) {
    if (!text) return '';
    
    let html = text;
    
    html = html.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
    
    html = html.replace(/^\*\*(.+?)\*\*:/g, '<strong>$1</strong>:');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    html = html.replace(/^(\|[^\n]+\|)\n(\|[-:|\s]+\|)\n((?:\|[^\n]+\|\n?)*)/gm, (match, header, separator, body) => {
        const headers = header.split('|').filter(c => c.trim());
        const rows = body.trim().split('\n').map(row => 
            row.split('|').filter(c => c.trim())
        );
        
        let tableHtml = '<table class="report-table"><thead><tr>';
        headers.forEach(h => { tableHtml += `<th>${h.trim()}</th>`; });
        tableHtml += '</tr></thead><tbody>';
        rows.forEach(row => {
            tableHtml += '<tr>';
            row.forEach(cell => { tableHtml += `<td>${cell.trim()}</td>`; });
            tableHtml += '</tr>';
        });
        tableHtml += '</tbody></table>';
        return tableHtml;
    });
    
    html = html.replace(/^-\s+(.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    
    html = html.replace(/^(\d+)\.\s+(.+)$/gm, '<li class="numbered">$2</li>');
    
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/`(.+?)`/g, '<code>$1</code>');
    
    html = html.replace(/^---\s*$/gm, '<hr>');
    
    html = html.replace(/^([^<\n].*)$/gm, (match) => {
        if (match.trim() === '') return '<br>';
        return `<p>${match}</p>`;
    });
    
    html = html.replace(/<\/h2>\s*<p>/g, '</h2>\n');
    html = html.replace(/<\/h3>\s*<p>/g, '</h3>\n');
    html = html.replace(/<\/table>\s*<p>/g, '</table>\n');
    html = html.replace(/<\/ul>\s*<p>/g, '</ul>\n');
    html = html.replace(/<p>\s*<\/p>/g, '');
    html = html.replace(/<br>\s*<br>/g, '<br>');
    
    return html;
}

// ── Inventory Logic ──────────────────────────────────────────────────────────
async function loadInventory() {
    const tableBody = document.querySelector('#inventory-table tbody');
    try {
        const res = await fetch(`${API_BASE}/inventory`);
        const data = await res.json();
        
        tableBody.innerHTML = data.map(item => `
            <tr>
                <td><b>${item.part_number}</b></td>
                <td>${item.warehouse_location || '-'}</td>
                <td>${item.stock_quantity ?? '-'}</td>
                <td style="color: ${item.days_of_cover < 3 ? '#ff4d4d' : '#2ed573'}">${item.days_of_cover ?? '-'}</td>
                <td><span class="badge ${item.daily_consumption > 5 ? 'HIGH' : item.daily_consumption > 2 ? 'MEDIUM' : 'LOW'}">${item.daily_consumption > 5 ? 'HIGH' : item.daily_consumption > 2 ? 'MEDIUM' : 'LOW'}</span></td>
            </tr>
        `).join('');
    } catch (e) {
        tableBody.innerHTML = "<tr><td colspan='5'>Error loading inventory data.</td></tr>";
    }
}

// ── Chat Logic ───────────────────────────────────────────────────────────────
const chatInput = document.getElementById('chat-input');
const chatBtn = document.getElementById('send-chat-btn');
const chatWindow = document.getElementById('chat-window');

async function sendChat() {
    const question = chatInput.value.trim();
    if (!question) return;
    
    appendMsg(question, 'user');
    chatInput.value = "";
    
    try {
        const res = await fetch(`${API_BASE}/agent/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        const data = await res.json();
        appendMsg(data.response || data.error, 'bot');
    } catch (e) {
        appendMsg("❌ API connection error.", 'bot');
    }
}

function appendMsg(text, sender) {
    const div = document.createElement('div');
    div.className = `msg ${sender}`;
    if (sender === 'bot') {
        div.innerHTML = parseMarkdown(text);
    } else {
        div.textContent = text;
    }
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

chatBtn.addEventListener('click', sendChat);
chatInput.addEventListener('keypress', (e) => { if(e.key === 'Enter') sendChat(); });

// ── Initialization ───────────────────────────────────────────────────────────
window.onload = () => {
    loadSummary();
    loadInventory();
    loadScenarioStatus();
};

// ── Detail Panel ──────────────────────────────────────────────────────────────
function openDetailPanel(type) {
    const panel = document.getElementById('detail-panel');
    const overlay = document.getElementById('panel-overlay');
    const title = document.getElementById('panel-title');
    const content = document.getElementById('panel-content');

    content.innerHTML = '<div class="panel-loading">Loading...</div>';
    panel.classList.add('open');
    overlay.classList.add('open');

    const configs = {
        suppliers: {
            title: 'Active Suppliers',
            endpoint: `${API_BASE}/suppliers`,
            countKey: null,
            render: renderSuppliers
        },
        orders: {
            title: 'In-Transit Orders',
            endpoint: `${API_BASE}/orders/in-transit`,
            countKey: null,
            render: renderOrders
        },
        delayed: {
            title: 'Delayed Orders',
            endpoint: `${API_BASE}/orders/delayed`,
            countKey: null,
            render: renderDelayed
        },
        parts: {
            title: 'Parts in Catalog',
            endpoint: `${API_BASE}/inventory`,
            countKey: null,
            render: renderParts
        }
    };

    const config = configs[type];
    if (!config) return;

    title.innerText = config.title;

    fetch(config.endpoint)
        .then(res => res.json())
        .then(data => {
            if (!data || data.length === 0) {
                content.innerHTML = '<div class="panel-empty">No data available.</div>';
            } else {
                content.innerHTML = config.render(data);
            }
        })
        .catch(() => {
            content.innerHTML = '<div class="panel-empty">Failed to load data.</div>';
        });
}

function closeDetailPanel() {
    document.getElementById('detail-panel').classList.remove('open');
    document.getElementById('panel-overlay').classList.remove('open');
}

function renderSuppliers(data) {
    const reliabilityColor = (r) => r >= 0.90 ? '#2ed573' : r >= 0.80 ? '#ffc14d' : '#ff4d4d';
    return `
        <div class="panel-count">${data.length} supplier${data.length !== 1 ? 's' : ''}</div>
        <table class="panel-table">
            <thead>
                <tr>
                    <th>Supplier</th>
                    <th>Location</th>
                    <th>Reliability</th>
                    <th>Risk</th>
                    <th>Avg Delay</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(s => `
                    <tr>
                        <td><b>${s.supplier_name}</b><br><span style="font-size:10px;color:var(--text-dim)">${s.supplier_id}</span></td>
                        <td>${s.city}, ${s.country}</td>
                        <td style="color:${reliabilityColor(s.reliability_score)}">${(s.reliability_score * 100).toFixed(0)}%</td>
                        <td><span class="panel-badge ${s.risk_category}">${s.risk_category}</span></td>
                        <td>${s.avg_delay_days}d</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderOrders(data) {
    return `
        <div class="panel-count">${data.length} order${data.length !== 1 ? 's' : ''} in transit</div>
        <table class="panel-table">
            <thead>
                <tr>
                    <th>PO #</th>
                    <th>Part</th>
                    <th>Supplier</th>
                    <th>Qty</th>
                    <th>Expected</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(o => `
                    <tr>
                        <td><b>${o.po_id}</b><br><span class="panel-badge ${o.criticality}">${o.criticality}</span></td>
                        <td>${o.part_number}<br><span style="font-size:10px;color:var(--text-dim)">${o.part_description}</span></td>
                        <td>${o.supplier_name}</td>
                        <td>${o.quantity_ordered}</td>
                        <td>${o.expected_delivery}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderDelayed(data) {
    const delayColor = (d) => d >= 7 ? '#ff4d4d' : d >= 4 ? '#ffc14d' : '#f9ca24';
    const confidenceColor = (c) => c === 'HIGH' ? '#2ed573' : c === 'MEDIUM' ? '#ffc14d' : '#ff4d4d';
    return `
        <div class="panel-count">${data.length} delayed order${data.length !== 1 ? 's' : ''}</div>
        <table class="panel-table">
            <thead>
                <tr>
                    <th>PO #</th>
                    <th>Part</th>
                    <th>Delay</th>
                    <th>Reason</th>
                    <th>Confirmed</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(o => `
                    <tr>
                        <td><b>${o.po_id}</b><br><span class="panel-badge ${o.criticality}">${o.criticality}</span></td>
                        <td>${o.part_number}</td>
                        <td style="color:${delayColor(o.delay_days)}"><b>+${o.delay_days}d</b></td>
                        <td style="font-size:11px">${o.delay_reason || '-'}</td>
                        <td>${o.confirmed_delivery || '-'}<br><span style="font-size:10px;color:${confidenceColor(o.confidence_level)}">${o.confidence_level} confidence</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderParts(data) {
    const coverColor = (c) => c < 3 ? '#ff4d4d' : c < 5 ? '#ffc14d' : '#2ed573';
    const usageLevel = (d) => d > 5 ? 'HIGH' : d > 2 ? 'MEDIUM' : 'LOW';
    return `
        <div class="panel-count">${data.length} part${data.length !== 1 ? 's' : ''} in catalog</div>
        <table class="panel-table">
            <thead>
                <tr>
                    <th>Part #</th>
                    <th>Stock</th>
                    <th>Days Cover</th>
                    <th>Daily Use</th>
                    <th>Usage</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(p => `
                    <tr>
                        <td><b>${p.part_number}</b><br><span style="font-size:10px;color:var(--text-dim)">${p.part_description}</span></td>
                        <td>${p.stock_quantity}</td>
                        <td style="color:${coverColor(p.days_of_cover)}"><b>${p.days_of_cover}d</b></td>
                        <td>${p.daily_consumption}</td>
                        <td><span class="panel-badge ${usageLevel(p.daily_consumption)}">${usageLevel(p.daily_consumption)}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}
