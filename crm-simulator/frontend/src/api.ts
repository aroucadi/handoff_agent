/**
 * CRM Simulator — API Client
 */

import type { Deal, DealStage } from './types';

const API_BASE = '/api';

export async function fetchDeals(): Promise<Deal[]> {
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
    } catch (err) {
        console.error('❌ Network or Parsing Error in fetchDeals:', err);
        throw err;
    }
}

export async function changeDealStage(
    dealId: string,
    stage: DealStage
): Promise<{ webhook_fired: boolean; webhook_result?: Record<string, unknown> }> {
    const res = await fetch(`${API_BASE}/deals/${dealId}/stage?stage=${stage}`, {
        method: 'POST',
    });
    return res.json();
}

export async function resetData(): Promise<void> {
    await fetch(`${API_BASE}/reset`, { method: 'POST' });
}
