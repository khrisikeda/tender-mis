/**
 * Internal Tender MIS Schema & Ingestion Types
 */

export type InternalTenderStatus =
  | 'new'
  | 'review'
  | 'interested'
  | 'qualification_check'
  | 'bid_preparation'
  | 'submitted'
  | 'awarded'
  | 'lost'
  | 'cancelled'
  | 'not_eligible';

export interface InternalTenderItem {
  id?: string;
  lot_number?: number;
  item_number?: number;
  title?: string;
  description: string;
  quantity?: number;
  unit?: string;
  specifications?: Record<string, unknown>;
  specifications_raw?: string;
  evidence_status?: string;
}

export interface InternalTender {
  id?: string;
  reference_number?: string;
  ocid?: string;
  ocds_release_id?: string;
  portal_adv_no?: string;
  portal_adv_status?: string;
  title: string;
  procuring_entity?: string;
  country: string;
  location?: string;
  category?: string;
  subcategory?: string;
  published_at?: string | null;
  deadline_at?: string | null;
  opening_at?: string | null;
  timezone: string;
  procurement_method?: string;
  tender_value?: number | null;
  currency?: string;
  description?: string;
  source_url?: string;
  tender_document_url?: string;
  status: InternalTenderStatus;
  relevance_score?: number;
  notes?: string;
  ocds_payload?: Record<string, unknown>;
  items?: InternalTenderItem[];
}

export interface DeadLetterRecord {
  id: string;
  timestamp: string;
  endpoint: string;
  method: string;
  status_code?: number | null;
  error_message: string;
  request_params?: Record<string, unknown>;
  attempt_count: number;
  last_retry_at: string;
  resolved: boolean;
}

export interface SyncReport {
  tier: string;
  source: string;
  timestamp: string;
  scanned_count: number;
  created_count: number;
  updated_count: number;
  failed_count: number;
  synced_items: Array<{
    identifier: string;
    title: string;
    action: 'created' | 'updated' | 'failed';
  }>;
  errors: DeadLetterRecord[];
}
