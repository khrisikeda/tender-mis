/**
 * Ingestion Storage & Repository
 * Handles idempotent upsert on ocid / reference_number and persists ingestion state.
 */
import fs from 'fs';
import path from 'path';
import { InternalTender } from '../types/internal.js';
import { Logger } from '../utils/logger.js';

const logger = new Logger('SyncRepository');

export class SyncRepository {
  private storageFile: string;

  constructor() {
    const storageDir = path.resolve(process.cwd(), '../../storage');
    if (!fs.existsSync(storageDir)) {
      fs.mkdirSync(storageDir, { recursive: true });
    }
    this.storageFile = path.join(storageDir, 'ingested_tenders.json');
    if (!fs.existsSync(this.storageFile)) {
      fs.writeFileSync(this.storageFile, JSON.stringify([], null, 2), 'utf-8');
    }
  }

  public getAll(): InternalTender[] {
    try {
      const data = fs.readFileSync(this.storageFile, 'utf-8');
      return JSON.parse(data || '[]') as InternalTender[];
    } catch {
      return [];
    }
  }

  /**
   * Idempotent upsert:
   * Matches by ocid OR reference_number OR portal_adv_no.
   * If existing, updates; otherwise inserts.
   */
  public upsertTender(tender: InternalTender): { action: 'created' | 'updated'; tender: InternalTender } {
    const list = this.getAll();
    const existingIndex = list.findIndex(
      t =>
        (tender.ocid && t.ocid === tender.ocid) ||
        (tender.reference_number && t.reference_number === tender.reference_number) ||
        (tender.portal_adv_no && t.portal_adv_no === tender.portal_adv_no)
    );

    if (existingIndex >= 0) {
      const existing = list[existingIndex];
      const updated: InternalTender = {
        ...existing,
        ...tender,
        items: tender.items && tender.items.length > 0 ? tender.items : existing.items,
        ocds_payload: tender.ocds_payload || existing.ocds_payload,
      };
      list[existingIndex] = updated;
      this.save(list);
      logger.info(`[UPSERT_UPDATE] ${tender.reference_number || tender.ocid} - ${tender.title.slice(0, 60)}`);
      return { action: 'updated', tender: updated };
    } else {
      list.push(tender);
      this.save(list);
      logger.info(`[UPSERT_CREATE] ${tender.reference_number || tender.ocid} - ${tender.title.slice(0, 60)}`);
      return { action: 'created', tender };
    }
  }

  private save(list: InternalTender[]) {
    try {
      fs.writeFileSync(this.storageFile, JSON.stringify(list, null, 2), 'utf-8');
    } catch (err) {
      logger.error('Could not save ingested tenders file', { error: String(err) });
    }
  }
}
