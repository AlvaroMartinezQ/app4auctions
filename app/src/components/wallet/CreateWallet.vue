<template>
  <q-card>
    <q-card-section class="bg-secondary q-py-xs text-white">
      Create a new wallet
    </q-card-section>
    <q-form greedy @submit.prevent="addWallet" class="row">
      <q-card-section class="bg-white col-5">
        <q-select
          v-model="selectedCurrency"
          :options="options"
          label="Currency"
          class="q-px-xs"
          :error="badCurrency"
        />
      </q-card-section>
      <q-card-section class="bg-white col-4">
        <q-input
          v-model="selectedAmmount"
          :label="$t('bid.quantity')"
          class="q-px-xs col-4"
          type="number"
          :error="badAmount"
        />
      </q-card-section>
      <q-space />
      <q-card-section class="bg-white col-2 q-my-md">
        <q-btn
          outline
          label="Create"
          color="green"
          type="submit"
          :loading="loading"
          :disable="loading"
          no-caps
          icon-right="add_circle"
        />
      </q-card-section>
    </q-form>
    <q-card-section
      div
      class="row col-12 justify-center q-pt-none"
      v-if="apiError"
    >
      <q-banner dense class="bg-grey-2">
        <q-icon name="priority_high" color="red" size="2em" />
        {{ $t('api.error') }}
      </q-banner>
    </q-card-section>
    <q-list bordered class="row justify-center">
      <q-expansion-item
        expand-separator
        icon="question_mark"
        label="How does this work?"
        class="col-10"
      >
        <ul class="q-mx-md">
          <li>Create wallets to create bids in the web</li>
          <li>Add new ammount to the wallet ammounts</li>
          <li>
            If you create a new wallet with a currency that you already have,
            the latter ammount will be included into the already existing wallet
          </li>
          <li>Once you create a bid the ammount is taken from your account</li>
          <li>
            If you win the auction the money is given to the user selling the
            product, in any other case, it's returned to you
          </li>
        </ul>
      </q-expansion-item>
    </q-list>
  </q-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';

const selectedCurrency = ref(null as null | string);
const options = ['euro', 'pound', 'dollar'];
const badCurrency = ref(false);
const selectedAmmount = ref(null as null | number);
const badAmount = ref(false);
const loading = ref(false);
const apiError = ref(false);

const emit = defineEmits<{
  (e: 'reload-wallet-data'): void;
}>();

const addWallet = async () => {
  loading.value = true;
  apiError.value = false;
  badAmount.value = false;
  if (selectedAmmount.value === null || selectedAmmount.value <= 0) {
    badAmount.value = true;
  } else {
    badAmount.value = false;
  }
  if (selectedCurrency.value === null) {
    badCurrency.value = true;
  } else {
    badCurrency.value = false;
  }
  if (!badCurrency.value && !badAmount.value) {
    const data = {
      currency: selectedCurrency.value,
      ammount: selectedAmmount.value,
    };
    let res = await MARKETPLACE_API_IMP.postUserWallet(data);
    if (res.data) {
      // Wallet created - update the parent
      selectedCurrency.value = null;
      selectedAmmount.value = null;
      emit('reload-wallet-data');
    } else {
      // Error on api
      apiError.value = true;
    }
  }
  loading.value = false;
};
</script>
