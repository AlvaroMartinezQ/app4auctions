<template>
  <q-card>
    <q-card-section class="bg-primary text-white text-caption">
      <q-icon name="wallet" class="q-mr-sm" size="1.5em" />
      Wallet
    </q-card-section>
    <q-card-section>
      <div class="row">{{ $t('wallet.id') }}: {{ wallet.id }}</div>
      <div class="row text-caption">
        {{ $t('wallet.currency') }}: {{ wallet.currency }}
      </div>
      <div class="row text-caption">
        {{ $t('bid.quantity') }}: <b>{{ wallet.ammount }}</b>
      </div>
    </q-card-section>
    <q-separator size="0.15em" class="q-mx-sm" />
    <q-card-section class="col-12 q-pb-none">
      Add money to your balance
    </q-card-section>
    <q-form greedy @submit.prevent="addAmount" class="row">
      <q-card-section class="col-7">
        <q-input
          filled
          v-model="addAmountNumber"
          :label="$t('bid.quantity')"
          class="q-pa-xs col-4"
          type="number"
          :error="badAmount"
        />
      </q-card-section>
      <q-space />
      <q-card-actions class="col-4">
        <q-btn
          outline
          label="Add"
          color="green"
          type="submit"
          :loading="loading"
          :disable="loading"
          no-caps
          icon-right="price_check"
        />
      </q-card-actions>
    </q-form>
  </q-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Wallet } from 'src/types/market';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';

interface Props {
  wallet: Wallet;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'reload-wallet-data'): void;
}>();

const addAmountNumber = ref(null as null | number);
const loading = ref(false);
const badAmount = ref(false);

const addAmount = async () => {
  loading.value = true;
  badAmount.value = false;
  if (addAmountNumber.value === null || addAmountNumber.value <= 0) {
    badAmount.value = true;
  } else {
    const data = {
      walletId: props.wallet.id,
      ammount: addAmountNumber.value,
    };
    let res = await MARKETPLACE_API_IMP.putUserWalletAmmount(data);
    if (res.data) {
      // ok
      addAmountNumber.value = null;
      emit('reload-wallet-data');
    } else {
      // error
    }
  }
  loading.value = false;
};
</script>
