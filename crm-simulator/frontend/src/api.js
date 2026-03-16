/**
 * CRM Simulator — API Client
 */
const API_BASE = '/api';
export async function fetchDeals() {
    try {
        const res = await fetch(`${API_BASE}/deals`);
        if (!res.ok) {
            const errorText = await res.text();
            console.error(`❌ CRM API Error (${res.status}):`, errorText);
            throw new Error(`Failed to fetch deals: ${res.status}`);
        }
        const data = await res.json();
        console.log(`✅ Loaded ${data.deals?.length || 0} deals from CRM backend`);
        return data.deals;
    }
    catch (err) {
        console.error('❌ Network or Parsing Error in fetchDeals:', err);
        throw err;
    }
}
export async function changeDealStage(dealId, stage) {
    const res = await fetch(`${API_BASE}/deals/${dealId}/stage?stage=${stage}`, {
        method: 'POST',
    });
    return res.json();
}
export async function resetData() {
    await fetch(`${API_BASE}/reset`, { method: 'POST' });
}
export async function importTemplate(templateId, tenantId) {
    const url = tenantId
        ? `${API_BASE}/import-template?template_id=${templateId}&tenant_id=${tenantId}`
        : `${API_BASE}/import-template?template_id=${templateId}`;
    const res = await fetch(url, { method: 'POST' });
    if (!res.ok) {
        throw new Error(`Failed to import template: ${res.status}`);
    }
    return res.json();
}
