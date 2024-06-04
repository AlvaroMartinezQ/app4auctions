import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('src/pages/HomePage.vue'),
      },
      {
        path: 'market',
        name: 'market',
        component: () => import('src/pages/auction/AuctionMarket.vue'),
      },
      {
        path: '/login',
        name: 'login',
        component: () => import('src/pages/user/auth/LogIn.vue'),
      },
      {
        path: '/logout',
        name: 'logout',
        component: () => import('src/pages/user/auth/LogOut.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/account/new',
        name: 'new_account',
        component: () => import('src/pages/user/auth/CreateAccount.vue'),
      },
      {
        path: '/account/activate/:id',
        name: 'activate_account',
        component: () => import('src/pages/user/auth/ActivateAccount.vue'),
      },
      {
        path: '/account',
        name: 'account',
        component: () => import('src/pages/user/account/UserAccount.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/auction/:id',
        name: 'auction',
        component: () => import('src/pages/auction/AuctionInfo.vue'),
      },
      {
        path: '/auction/search',
        name: 'auction_filter',
        component: () => import('src/pages/auction/AuctionFilter.vue'),
      },
      {
        path: '/auction/new',
        name: 'auction_new',
        component: () => import('src/pages/auction/AuctionNew.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/auction/update/:id',
        name: 'auction_update',
        component: () => import('src/pages/auction/AuctionNew.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: '/user/auctions',
        name: 'user_auction_list',
        component: () => import('src/pages/user/account/UserAuctions.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/user/bids',
        name: 'user_bid_list',
        component: () => import('src/pages/user/account/UserBids.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/user/wallets',
        name: 'user_wallet_list',
        component: () => import('src/pages/user/wallet/WalletList.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/user/process/buys',
        name: 'user_buys',
        component: () => import('src/pages/user/process/GenericProcess.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/user/process/sells',
        name: 'user_sells',
        component: () => import('src/pages/user/process/GenericProcess.vue'),
        meta: { requiresAuth: true }
      },
      // Always leave this as last one | fallback
      {
        path: '/:catchAll(.*)*',
        component: () => import('src/pages/other/ErrorNotFound.vue'),
      },
    ],
  },
];

export default routes;
