/**
 * Open Contracting Data Standard (OCDS 1.1) Type Definitions
 * With Rwanda Umucyo e-Procurement specific extensions.
 */

export interface OCDSValue {
  amount: number;
  currency: string;
}

export interface OCDSEntity {
  id?: string;
  name: string;
  address?: {
    streetAddress?: string;
    locality?: string;
    region?: string;
    postalCode?: string;
    countryName?: string;
  };
  contactPoint?: {
    name?: string;
    email?: string;
    telephone?: string;
    faxNumber?: string;
    url?: string;
  };
}

export interface OCDSTenderPeriod {
  startDate?: string;
  endDate?: string;
  maxExtentDate?: string;
  durationInDays?: number;
}

export interface OCDSItem {
  id: string;
  description?: string;
  classification?: {
    scheme?: string;
    id?: string;
    description?: string;
    uri?: string;
  };
  additionalClassifications?: Array<{
    scheme?: string;
    id?: string;
    description?: string;
  }>;
  quantity?: number;
  unit?: {
    name?: string;
    value?: OCDSValue;
  } | string;
}

export interface OCDSDocument {
  id: string;
  documentType?: string;
  title?: string;
  description?: string;
  url?: string;
  datePublished?: string;
  dateModified?: string;
  format?: string;
  language?: string;
}

export interface OCDSTender {
  id: string;
  title?: string;
  description?: string;
  status?: string; // 'planning' | 'planned' | 'active' | 'cancelled' | 'unsuccessful' | 'complete' | 'withdrawn'
  procuringEntity?: OCDSEntity;
  value?: OCDSValue;
  minValue?: OCDSValue;
  procurementMethod?: string; // 'open' | 'selective' | 'limited' | 'direct'
  procurementMethodDetails?: string;
  procurementMethodRationale?: string;
  mainProcurementCategory?: 'goods' | 'works' | 'services';
  tenderPeriod?: OCDSTenderPeriod;
  enquiryPeriod?: OCDSTenderPeriod;
  hasEnquiries?: boolean;
  eligibilityCriteria?: string;
  awardPeriod?: OCDSTenderPeriod;
  numberOfTenderers?: number;
  items?: OCDSItem[];
  documents?: OCDSDocument[];
}

export interface OCDSRelease {
  ocid: string;
  id: string;
  date: string;
  tag?: string[];
  initiationType?: string;
  buyer?: OCDSEntity;
  tender?: OCDSTender;
  parties?: OCDSEntity[];
  language?: string;
  [key: string]: unknown;
}

export interface OCDSPagination {
  total?: number;
  offset?: number;
  limit?: number;
  next?: string;
  prev?: string;
}

export interface OCDSReleasePackage {
  uri?: string;
  version?: string;
  publishedDate?: string;
  publisher?: {
    name?: string;
    scheme?: string;
    uid?: string;
    uri?: string;
  };
  license?: string;
  publicationPolicy?: string;
  releases: OCDSRelease[];
  pagination?: OCDSPagination;
}
