import CLIENT_API_IMP, { getCookie } from 'app/src/api/client.api'
import { AuctionNew } from 'src/types/market';

export type APIData = Record<any, any>;

// No data action
type NoDataOP = () => ReturnType<typeof CLIENT_API_IMP.get>
// Auction actions
type AuctionPage = (page: number) => ReturnType<typeof CLIENT_API_IMP.get>
type AuctionGet = (id: string) => ReturnType<typeof CLIENT_API_IMP.get>
type AuctionFilter = (filter_method: string, userText: string) => ReturnType<typeof CLIENT_API_IMP.get>
type AuctionPost = (auctionData: AuctionNew) => ReturnType<typeof CLIENT_API_IMP.auth_post>
type AuctionPut = (auctionId: string, auctionData: AuctionNew) => ReturnType<typeof CLIENT_API_IMP.auth_put>
// Bid actions
type BidGet = (bidId: string) => ReturnType<typeof CLIENT_API_IMP.auth_get>
type BidPost = (auctionId: string, params: APIData) => ReturnType<typeof CLIENT_API_IMP.auth_post>
// User actions
type NoDataAuthOP = () => ReturnType<typeof CLIENT_API_IMP.auth_get>
// Wallet actions
type CreateWallet = (data: APIData) => ReturnType<typeof CLIENT_API_IMP.e_auth_post>
type UpdateWalletAmmount = (data: APIData) => ReturnType<typeof CLIENT_API_IMP.e_auth_put>
// Processes actions
type BuysGet = () => ReturnType<typeof CLIENT_API_IMP.auth_get>
type SellsGet = () => ReturnType<typeof CLIENT_API_IMP.auth_get>

// Image uploads
type ImageData = any;
type ImagePost = (auctionId: string, image: ImageData) => ReturnType<typeof CLIENT_API_IMP.image_post>
type ImageGet = (auctionId: string) => ReturnType<typeof CLIENT_API_IMP.image_get>

interface MARKETPLACE_API {
  // Auctions
  getAuctions: AuctionPage,
  getAuction: AuctionGet,
  filterAuctions: AuctionFilter,
  postAuction: AuctionPost,
  putAuction: AuctionPut,
  // Bids
  getAuctionBidRef: BidGet,
  postBid: BidPost,
  // User market data
  getUserAuctions: NoDataAuthOP,
  getUserBids: NoDataAuthOP,
  getUserCanEditAuction: AuctionGet,
  // User wallets
  getUserWallets: NoDataAuthOP,
  postUserWallet: CreateWallet,
  putUserWalletAmmount: UpdateWalletAmmount,
  // User buy/sell processes
  getUserBuys: BuysGet,
  getUserSells: SellsGet,
  // Images
  postImage: ImagePost,
  getImage: ImageGet
}

const MARKETPLACE_API_IMP: MARKETPLACE_API = {
  // Auctions
  getAuctions(page) {
    return CLIENT_API_IMP.get(`/market/auction/?page=${page}&limit=10`);
  },
  getAuction(id) {
    return CLIENT_API_IMP.get(`/market/auction/${id}/`);
  },
  filterAuctions(filter_method, userText) {
    return CLIENT_API_IMP.get(`/market/auction/search/?filter_text=${userText}&method=${filter_method}`);
  },
  postAuction(auctionData) {
    return CLIENT_API_IMP.auth_post('/market/auction/', auctionData, getCookie('appforauctionsauth'));
  },
  putAuction(auctionId, auctionData) {
    return CLIENT_API_IMP.auth_put(`/market/auction/${auctionId}/`, auctionData, getCookie('appforauctionsauth'));
  },
  // Bids
  getAuctionBidRef(bidId) {
    return CLIENT_API_IMP.auth_get(`/market/bid/${bidId}/`, getCookie('appforauctionsauth'));
  },
  postBid(auctionId, params) {
    return CLIENT_API_IMP.auth_post(`/market/bid/${auctionId}/`, params, getCookie('appforauctionsauth'));
  },
  // User
  getUserAuctions() {
    return CLIENT_API_IMP.auth_get('/market/auctions/user/', getCookie('appforauctionsauth'));
  },
  getUserBids() {
    return CLIENT_API_IMP.auth_get('/market/bids/user/', getCookie('appforauctionsauth'));
  },
  getUserCanEditAuction(auctionId) {
    return CLIENT_API_IMP.auth_get(`/market/auction/user/owned/${auctionId}/`, getCookie('appforauctionsauth'));
  },
  // Wallets
  getUserWallets() {
    return CLIENT_API_IMP.auth_get('/wallet/', getCookie('appforauctionsauth'));
  },
  postUserWallet(data) {
    return CLIENT_API_IMP.e_auth_post(`/wallet/?currency=${data.currency}&ammount=${data.ammount}`, getCookie('appforauctionsauth'));
  },
  putUserWalletAmmount(data) {
    return CLIENT_API_IMP.e_auth_put(`/wallet/?wallet_id=${data.walletId}&ammount=${data.ammount}`, getCookie('appforauctionsauth'));
  },
  // Processes
  getUserBuys() {
    return CLIENT_API_IMP.auth_get('/market/process/buy/user/', getCookie('appforauctionsauth'));
  },
  getUserSells() {
    return CLIENT_API_IMP.auth_get('/market/process/sell/user/', getCookie('appforauctionsauth'));
  },
  // Images
  postImage(auctionId, image) {
    return CLIENT_API_IMP.image_post(`/market/auction/image/${auctionId}/`, image, getCookie('appforauctionsauth'));
  },
  getImage(auctionId) {
    return CLIENT_API_IMP.image_get(`/market/auction/image/${auctionId}/`);
  }
}

export default MARKETPLACE_API_IMP
