/**
 * CRM Simulator — TypeScript Types
 */

export type DealStage =
    | 'prospecting'
    | 'qualification'
    | 'negotiation'
    | 'closed_won'
    | 'closed_lost'
    | 'implemented';

export interface Contact {
    name: string;
    title: string;
    email: string;
    role: string;
    pain_point?: string;
    commitment?: string;
    notes?: string;
}

export interface DealProduct {
    name: string;
    annual_value?: number;
}

export interface Risk {
    description: string;
    severity: string;
    source: string;
}

export interface SuccessMetric {
    metric: string;
    current_value?: string;
    target_value?: string;
    timeframe?: string;
}

export interface Deal {
    deal_id: string;
    company_name: string;
    deal_value: number;
    stage: DealStage;
    products: DealProduct[];
    close_date?: string;
    sla_days?: number;
    csm_id?: string;
    industry: string;
    employee_count?: number;
    contacts: Contact[];
    risks: Risk[];
    success_metrics: SuccessMetric[];
    sales_transcript?: string;
    contract_pdf_url?: string;
    webhook_url?: string;
    webhook_fired: boolean;
    webhook_response?: string;
}

export const STAGE_LABELS: Record<DealStage, string> = {
    prospecting: 'Prospecting',
    qualification: 'Qualification',
    negotiation: 'Negotiation',
    closed_won: 'Closed Won',
    closed_lost: 'Closed Lost',
    implemented: 'Implemented',
};

export const PIPELINE_STAGES: DealStage[] = [
    'prospecting',
    'qualification',
    'negotiation',
    'closed_won',
    'closed_lost',
    'implemented',
];
