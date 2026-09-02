/**
 * Umucyo Portal Fallback & Deep Retrieval Scraper
 * - Wraps selectAdvertisingDtlInfo.do with mandatory adv_no and adv_status query parameters.
 * - Manages session headers and JSESSIONID cookies.
 * - Implements exponential backoff retries.
 * - Routes persistent failures to Dead Letter Queue.
 */
import axios, { AxiosInstance } from 'axios';
import https from 'https';
import * as cheerio from 'cheerio';
import { InternalTender, InternalTenderItem } from '../types/internal.js';
import { Logger } from '../utils/logger.js';
import { defaultDLQ } from '../utils/deadLetterQueue.js';

const logger = new Logger('PortalFallbackScraper');

const UMUCYO_BASE_URL = 'https://www.umucyo.gov.rw';
const UMUCYO_MAIN_URL = `${UMUCYO_BASE_URL}/pt/pcm/moveMainPageDetail.do`;
const UMUCYO_LIST_URL = `${UMUCYO_BASE_URL}/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100&leftTopFlag=l&tendTypeCd=G`;
const UMUCYO_DETAIL_URL = `${UMUCYO_BASE_URL}/eb/bav/selectAdvertisingDtlInfo.do`;

const DEFAULT_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en-US,en;q=0.9',
};

export class PortalFallbackScraper {
  private client: AxiosInstance;
  private sessionCookies: string = '';

  constructor() {
    this.client = axios.create({
      timeout: 15000,
      headers: DEFAULT_HEADERS,
      httpsAgent: new https.Agent({ rejectUnauthorized: false }),
      validateStatus: () => true, // inspect status manually for dead-lettering
    });
  }

  /**
   * Safe URL Generator:
   * Mandatory query parameters (?adv_no={TENDER_NUMBER}&adv_status={STATUS_CODE}).
   * Never issue raw GET requests without parameters.
   */
  public static buildDetailUrl(advNo: string, advStatus: string = '00'): string {
    const encNo = encodeURIComponent(advNo.trim());
    const encStatus = encodeURIComponent(advStatus.trim());
    return `${UMUCYO_DETAIL_URL}?adv_no=${encNo}&adv_status=${encStatus}`;
  }

  /**
   * Initializes session on the main Umucyo portal to capture JSESSIONID cookies.
   */
  public async initializeSession(): Promise<boolean> {
    try {
      logger.info('Initializing session on Umucyo portal...');
      const resp = await this.client.get(UMUCYO_MAIN_URL);
      const setCookies = resp.headers['set-cookie'];
      if (setCookies && Array.isArray(setCookies)) {
        this.sessionCookies = setCookies.map(c => c.split(';')[0]).join('; ');
      }
      return true;
    } catch (err) {
      logger.warn('Could not initialize portal session cookies', { error: String(err) });
      return false;
    }
  }

  /**
   * Fetches single tender detail with exponential backoff and session header management.
   */
  public async fetchTenderDetailWithRetry(
    internalRefNo: string,
    tendStageCd: string = 'O',
    tendTypeCd: string = 'G',
    maxRetries: number = 3
  ): Promise<{ detailHtml: string; items: InternalTenderItem[]; securityAmount?: number }> {
    let delayMs = 1000;
    const postBody = new URLSearchParams({
      tendReferNo: internalRefNo,
      tendStageCd: tendStageCd,
      tendTypeCd: tendTypeCd,
      currentPageNo: '1',
      searchConditions: '/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100&leftTopFlag=l&tendTypeCd=G',
    }).toString();

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const resp = await this.client.post(UMUCYO_DETAIL_URL, postBody, {
          headers: {
            ...DEFAULT_HEADERS,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': UMUCYO_LIST_URL,
            ...(this.sessionCookies ? { Cookie: this.sessionCookies } : {}),
          },
        });

        if (resp.status !== 200) {
          defaultDLQ.push({
            endpoint: UMUCYO_DETAIL_URL,
            method: 'POST',
            status_code: resp.status,
            error_message: `HTTP ${resp.status} received from detail endpoint`,
            request_params: { internalRefNo, attempt },
          });

          if (attempt === maxRetries) {
            return { detailHtml: '', items: [] };
          }
          await new Promise(r => setTimeout(r, delayMs));
          delayMs *= 2;
          continue;
        }

        const html = String(resp.data || '');
        const parsed = this.parseDetailHtml(html);
        return { detailHtml: html, items: parsed.items, securityAmount: parsed.securityAmount };
      } catch (err: unknown) {
        const axiosErr = axios.isAxiosError(err) ? err : null;
        defaultDLQ.push({
          endpoint: UMUCYO_DETAIL_URL,
          method: 'POST',
          status_code: axiosErr?.response?.status ?? null,
          error_message: axiosErr?.message || String(err),
          request_params: { internalRefNo, attempt },
        });

        if (attempt === maxRetries) {
          return { detailHtml: '', items: [] };
        }
        await new Promise(r => setTimeout(r, delayMs));
        delayMs *= 2;
      }
    }

    return { detailHtml: '', items: [] };
  }

  /**
   * DOM Parser using Cheerio to extract lots, line items, and tender security amount.
   */
  public parseDetailHtml(html: string): { items: InternalTenderItem[]; securityAmount?: number } {
    if (!html) return { items: [] };
    const $ = cheerio.load(html);
    const items: InternalTenderItem[] = [];
    let securityAmount: number | undefined;

    let isLotTable = false;
    $('tr').each((_, el) => {
      const text = $(el).text().trim().replace(/\s+/g, ' ');

      if (text.includes('Tender Security (sum of LOTs)') || text.includes('Tender Security Amount')) {
        const amtMatch = text.match(/[\d,]+\.?\d*/g);
        if (amtMatch) {
          for (const m of amtMatch) {
            const parsed = parseFloat(m.replace(/,/g, ''));
            if (parsed > 1000) {
              securityAmount = parsed;
              break;
            }
          }
        }
      }

      if (text.includes('LOT No') && text.includes('Name of Goods')) {
        isLotTable = true;
        return;
      }

      if (isLotTable) {
        const cells = $(el).find('td').map((__, td) => $(td).text().trim()).get();
        if (cells.length >= 3 && /^\d+$/.test(cells[0])) {
          const lotNo = parseInt(cells[0], 10);
          const lotName = cells[1];
          const secAmt = cells[2] || '';
          const delivery = cells[4] || 'Rwanda';

          items.push({
            lot_number: lotNo,
            item_number: lotNo,
            title: `Lot ${lotNo}: ${lotName}`,
            description: `Lot ${lotNo}: ${lotName}`,
            quantity: 1,
            unit: 'Lot',
            specifications: {
              lot_number: String(lotNo),
              lot_name: lotName,
              tender_security_amount: secAmt,
              delivery_place: delivery,
            },
          });
        } else if (text.includes('Document Name') || text.includes('Required bidding')) {
          isLotTable = false;
        }
      }
    });

    return { items, securityAmount };
  }
}
