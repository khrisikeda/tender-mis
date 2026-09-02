import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { DeadLetterRecord } from '../types/internal.js';
import { Logger } from './logger.js';

const logger = new Logger('DeadLetterQueue');

export class DeadLetterQueue {
  private filePath: string;

  constructor(customPath?: string) {
    if (customPath) {
      this.filePath = customPath;
    } else {
      const baseDir = path.resolve(process.cwd(), '../../storage');
      this.filePath = path.join(baseDir, 'dead_letters.json');
    }
  }

  private ensureFileExists(): void {
    const dir = path.dirname(this.filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    if (!fs.existsSync(this.filePath)) {
      fs.writeFileSync(this.filePath, JSON.stringify([], null, 2), 'utf-8');
    }
  }

  public getAll(): DeadLetterRecord[] {
    try {
      this.ensureFileExists();
      const content = fs.readFileSync(this.filePath, 'utf-8');
      return JSON.parse(content || '[]') as DeadLetterRecord[];
    } catch (err) {
      logger.error('Failed to read dead-letter file', { error: String(err) });
      return [];
    }
  }

  public push(record: Omit<DeadLetterRecord, 'id' | 'timestamp' | 'attempt_count' | 'last_retry_at' | 'resolved'>): DeadLetterRecord {
    this.ensureFileExists();
    const records = this.getAll();
    const now = new Date().toISOString();

    const fullRecord: DeadLetterRecord = {
      ...record,
      id: crypto.randomUUID(),
      timestamp: now,
      attempt_count: 1,
      last_retry_at: now,
      resolved: false,
    };

    logger.warn(`[DLQ_PUSH] ${record.endpoint} - ${record.error_message}`, {
      status_code: record.status_code,
      params: record.request_params,
    });

    records.push(fullRecord);
    // Keep last 500 records
    const trimmed = records.slice(-500);

    try {
      fs.writeFileSync(this.filePath, JSON.stringify(trimmed, null, 2), 'utf-8');
    } catch (err) {
      logger.error('Failed to write to dead-letter file', { error: String(err) });
    }

    return fullRecord;
  }
}

export const defaultDLQ = new DeadLetterQueue();
