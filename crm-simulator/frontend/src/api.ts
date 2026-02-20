/**
 * CRM Simulator — API Client
 */

import type { Deal, DealStage } from './types';

const API_BASE = '/api';

export async function fetchDeals(): Promise<Deal[]> {
    const res = await fetch(`${API_BASE}/deals`);
    const data = await res.json();
    return data.deals;
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
