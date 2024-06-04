<template>
  <q-page padding>
    <div class="row text-h6">
      <q-icon name="account_balance" class="q-mr-sm" size="1.5em" />
      Your wallets
    </div>
    <span
      v-if="loaded"
      :class="$q.platform.is.mobile ? 'col-12' : 'row justify-center'"
    >
      <UserWallet
        v-for="w in userWallets"
        :key="w.id"
        :wallet="w"
        @reload-wallet-data="reloadData()"
        class="q-mx-sm q-my-sm"
      />
    </span>
    <div class="row q-px-md q-py-md">
      <CreateWallet @reload-wallet-data="reloadData()" class="full-width" />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useQuasar } from 'quasar';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';
import { Wallet } from 'src/types/market';
import UserWallet from 'src/components/wallet/UserWallet.vue';
import CreateWallet from 'src/components/wallet/CreateWallet.vue';

const $q = useQuasar();

const userWallets = ref([] as Wallet[]);
const loaded = ref(false);

const reloadData = async () => {
  loaded.value = false;
  let res = await MARKETPLACE_API_IMP.getUserWallets();
  if (res.data) {
    userWallets.value = res.data.wallets;
  }
  loaded.value = true;
};

onMounted(async () => {
  await reloadData();
  loaded.value = true;
});
</script>
