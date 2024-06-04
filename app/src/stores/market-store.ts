import { defineStore } from 'pinia';
import { Auction } from 'src/types/market';
import { getDateNow } from 'src/utils/timedates';

export const marketStore = defineStore({
  id: 'marketStore',
  state: () => ({
    auction_list: [] as Auction[],
    last_query: null as null | string,
  }),
  getters: {
    getAuctions: (state) => state.auction_list,
  },
  actions: {
    set_auctions(auctions: Auction[]) {
      this.auction_list = auctions;
      // Set the last update of auctions
      this.last_query = getDateNow();
    },
    clear_auctions() {
      this.auction_list.length = 0;
    },
    get_auctions() {
      return this.auction_list;
    },
    auctions_length_valid() {
      return (this.auction_list.length > 0 ? true : false);
    },
    add_auction(data: Auction) {
      // Insert at the start to view the update
      this.auction_list.unshift(data);
    }
  }
})