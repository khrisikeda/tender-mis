/**
 * Structured JSON Logger for Ingestion Worker
 */

export type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';

export class Logger {
  private context: string;

  constructor(context: string = 'IngestionWorker') {
    this.context = context;
  }

  private log(level: LogLevel, message: string, meta?: Record<string, unknown>) {
    const entry = {
      timestamp: new Date().toISOString(),
      level,
      context: this.context,
      message,
      ...(meta ? { meta } : {}),
    };
    if (level === 'ERROR') {
      console.error(JSON.stringify(entry));
    } else if (level === 'WARN') {
      console.warn(JSON.stringify(entry));
    } else {
      console.log(JSON.stringify(entry));
    }
  }

  debug(message: string, meta?: Record<string, unknown>) {
    this.log('DEBUG', message, meta);
  }

  info(message: string, meta?: Record<string, unknown>) {
    this.log('INFO', message, meta);
  }

  warn(message: string, meta?: Record<string, unknown>) {
    this.log('WARN', message, meta);
  }

  error(message: string, meta?: Record<string, unknown>) {
    this.log('ERROR', message, meta);
  }
}

export const defaultLogger = new Logger('WorkerRoot');
