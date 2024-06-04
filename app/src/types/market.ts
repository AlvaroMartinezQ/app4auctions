export interface Auction {
  id: string;
  title: string;
  description: string;
  tags: string;
  init_price: number;
  price_currency: string;
  highest_offer: null | number;
  creation_date: string;
  start_date: string;
  finish_date: string;
  bids: Bid[];
}

export interface AuctionNew {
  init_price: number;
  price_currency: string;
  start_date: string;
  finish_date: string;
  title: string;
  description: string;
  tags: string;
}

export interface Bid {
  id: string;
  creation_date: string;
  offer_ammount: number;
}

export interface AuctionFilterTFIDF {
  auction: Auction;
  similarity: number;
}

export interface Wallet {
  id: string;
  ammount: number;
  currency: string;
}

export enum FilterMethods {
  TFIDF = 'tfidf',
  SVM = 'svm',
  LSI = 'lsi'
}
