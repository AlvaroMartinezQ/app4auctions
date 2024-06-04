<template>
  <q-layout view="hHh lpR fFf">
    <!-- App header -->
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />
        <q-toolbar-title>
          <q-btn outline :to="{ name: 'home' }">
            <!-- {{ $t('apptitle') }} -->
            Home
          </q-btn>
        </q-toolbar-title>
        <q-space />
        <p v-if="loggedIn" class="q-mt-md q-mr-sm">
          Welcome, {{ authS.getEmail }}
        </p>
        <q-btn-dropdown
          outline
          icon="language"
          :label="$t('short_lang')"
          size="md"
          class="q-mx-xs"
        >
          <q-list>
            <q-item
              v-for="lang in locales"
              :key="lang.title"
              clickable
              v-close-popup
              @click="changeLocale(lang.locale)"
            >
              <q-item-section>
                <q-item-label>{{ lang.title }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
        <q-btn-dropdown
          outline
          icon="account_circle"
          :label="$t('account.title')"
          size="md"
          class="q-mx-xs"
        >
          <q-list>
            <q-item
              v-for="action in accountActions"
              :key="action.title"
              clickable
              v-close-popup
              :to="{ name: action.to }"
            >
              <q-item-section>
                <q-item-label>
                  <q-icon :name="action.icon" />
                  {{ action.title }}
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </q-toolbar>
    </q-header>
    <!-- Left side menu -->
    <q-drawer v-model="leftDrawerOpen" bordered elevated>
      <q-list>
        <!-- TODO fix scrolling of the side menu - keep it fixed -->
        <q-item-label header> Quick links </q-item-label>
        <EssentialLink
          v-for="link in sideMenuActions"
          :key="link.title"
          v-bind="link"
        />
      </q-list>
    </q-drawer>
    <!-- Componenets will be placed here -->
    <q-page-container>
      <router-view
        @reload-user-data="reloadUserData"
        @clean-data="logOut"
        v-if="loaded"
      />
    </q-page-container>
    <!-- App footer -->
    <q-footer>
      <q-toolbar>
        <q-toolbar-title class="text-overline">v0.0.1</q-toolbar-title>
        <q-space />
        <q-btn
          rounded
          outline
          icon="code"
          href="https://gitlab.com/AlvaroMartinezQ/app4auctions/"
          target="_blank"
        ></q-btn>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import EssentialLink, {
  EssentialLinkProps,
} from 'components/EssentialLink.vue';
import { useI18n } from 'vue-i18n';
import { getCookie } from 'src/api/client.api';
import AUTH_API_IMP from 'src/api/endpoints/auth';
import { authStore } from 'src/stores/auth-store';
import { marketStore } from 'src/stores/market-store';
import { Auction } from 'src/types/market';

const t = useI18n();
const authS = authStore();
const marketS = marketStore();
const loaded = ref(false);

const leftDrawerOpen = ref(false);
function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

const locales = [
  { title: 'English', locale: 'en-US' },
  { title: 'Español', locale: 'es-ES' },
];
const changeLocale = (locale: string) => {
  t.locale.value = locale;
};

const loggedIn = ref(null as null | boolean);
const accountActions = [] as Record<string, string>[];
const sideMenuActions = [] as EssentialLinkProps[];

const reloadUserData = async () => {
  let res = await AUTH_API_IMP.getUserData();
  if (res.data) {
    authS.setData(
      res.data.id,
      res.data.email,
      res.data.personal_name,
      res.data.personal_surname,
      res.data.n_auctions,
      res.data.n_bids,
      res.data.singup_date,
      res.data.address,
      res.data.phone,
      res.data.identification_number,
      res.data.country
    );
    loggedIn.value = true;
    loadLinks();
  }
  if ('statusCode' in res && res.statusCode === 401) {
    // Cookie is set but is invalid - it has expired
    document.cookie = 'appforauctionsauth=';
    loadLinks();
  }
};

const logOut = () => {
  loggedIn.value = false; // clean state after logout
  loadLinks();
};

const loadLinks = () => {
  accountActions.length = 0;
  sideMenuActions.length = 0;
  if (loggedIn.value) {
    // Logged in
    accountActions.push(
      { title: 'Profile', icon: 'account_box', to: 'account' },
      { title: 'Logout', icon: 'logout', to: 'logout' }
    );
    sideMenuActions.push(
      {
        title: 'Home',
        caption: 'Start page',
        icon: 'home',
        link: 'home',
      },
      {
        title: 'Market',
        caption: 'Browse all active auctions',
        icon: 'store',
        link: 'market',
      },
      {
        title: 'My auctions',
        caption: 'View your auctions',
        icon: 'summarize',
        link: 'user_auction_list',
      },
      {
        title: 'My bids',
        caption: 'View your bids',
        icon: 'gavel',
        link: 'user_bid_list',
      },
      {
        title: 'My wallets',
        caption: 'View your wallets',
        icon: 'wallet',
        link: 'user_wallet_list',
      },
      {
        title: 'My buy processes',
        caption: 'View your buys on the web',
        icon: 'shopping_basket',
        link: 'user_buys',
      },
      {
        title: 'My sell processes',
        caption: 'View your sells on the web',
        icon: 'sell',
        link: 'user_sells',
      },
      {
        title: 'New auction',
        caption: 'Create a new auction',
        icon: 'add_circle',
        link: 'auction_new',
      }
      /*
      {
        title: 'My account',
        caption: 'View your account',
        icon: 'account_circle',
        link: 'account',
      },
      {
        title: 'Logout',
        caption: 'Logout from your account',
        icon: 'logout',
        link: 'logout',
      }
      */
    );
  } else {
    // Not logged in
    accountActions.push(
      { title: 'Login', icon: 'login', to: 'login' },
      { title: 'Create account', icon: 'person_add', to: 'new_account' }
    );
    sideMenuActions.push(
      {
        title: 'Home',
        caption: 'Start page',
        icon: 'home',
        link: 'home',
      },
      {
        title: 'Login',
        caption: 'Login into your account',
        icon: 'account_circle',
        link: 'login',
      },
      {
        title: 'Market',
        caption: 'Browse all active auctions',
        icon: 'store',
        link: 'market',
      },
      {
        title: 'Create user',
        caption: 'Create a new user',
        icon: 'person_add',
        link: 'new_account',
      }
    );
  }
};

if (import.meta.env.VITE_WS_ON === 'on') {
  // WS link comes from .env
  const marketWS = new WebSocket(import.meta.env.VITE_WS_MARKETPLACE_URL);

  marketWS.addEventListener('open', () => {
    // Open the ws connection
    console.log('[Market ws] - connection started');
  });

  marketWS.addEventListener('message', function (event) {
    try {
      marketS.add_auction(JSON.parse(event.data) as Auction);
    } catch (e) {
      console.log('There was an error parsing a new auction into the store');
    }
  });
}

onMounted(async () => {
  if (
    getCookie('appforauctionsauth') !== null &&
    getCookie('appforauctionsauth') !== ''
  ) {
    // Try to request user info
    await reloadUserData();
  } else {
    loadLinks();
  }
  loaded.value = true;
});
</script>
