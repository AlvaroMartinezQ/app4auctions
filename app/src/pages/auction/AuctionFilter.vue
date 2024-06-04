<template>
  <q-page padding>
    <div class="fit wrap self-center justify-center row">
      <q-card>
        <q-card-section class="text-h6 q-mx-sm q-py-md">
          {{ $t('auction.search') }}
        </q-card-section>
        <q-card-section class="q-py-sm">
          <q-input
            dense
            v-model="userText"
            :label="$t('forms.user_search')"
            class="col-6"
            :error="emptySearch"
            :error-message="$t('forms.input_value')"
            autogrow
          />
          <q-select
            v-model="searchMethod"
            :options="searchOptions"
            :error="emptySearch"
            :label="$t('forms.search_method')"
            :error-message="$t('forms.input_value')"
          />
        </q-card-section>
        <q-card-actions class="q-mx-sm">
          <q-btn
            :label="$t('forms.clear_search')"
            color="red"
            @click="clearSearch"
            no-caps
            icon="clear"
            :disable="auctions.length === 0"
          />
          <q-space />
          <q-btn
            :label="$t('forms.search')"
            color="primary"
            @click="search"
            no-caps
            icon="search"
            :disable="auctions.length !== 0"
          />
        </q-card-actions>
      </q-card>
    </div>
    <div
      v-if="loading"
      class="self-center justify-center row q-pt-md text-overline"
    >
      <q-spinner size="2em" />
    </div>
    <div v-else>
      <div
        v-if="auctions.length === 0 && !apiError"
        class="self-center justify-center row q-pt-md text-red text-overline"
      >
        {{ $t('nothing') }}
      </div>
      <div v-else class="q-my-md">
        <span v-if="searchMethod === FilterMethods.TFIDF">
          <!-- <div class="self-center justify-center row q-py-md">
            <q-btn
              outline
              label="Clear results that equal to 0"
              color="secondary"
              @click="clearEqualToCero"
              no-caps
            />
          </div> -->
          <span v-for="entry in auctions" :key="entry.auction.id">
            <q-card>
              <q-card-section class="row q-py-xs">
                {{ $t('auction.search_relevance') }}:
                {{ formatNumber(entry.similarity) }}/1.0
              </q-card-section>
            </q-card>
            <auction-card
              :auction="entry.auction"
              :info="false"
              :canPerformBid="false"
              class="q-mb-md q-mt-xs"
            />
          </span>
        </span>
        <span v-else>
          <span v-for="entry in auctions" :key="entry.id">
            <auction-card
              :auction="entry as Auction"
              :info="false"
              :canPerformBid="false"
              class="q-mb-md q-mt-xs"
            />
          </span>
        </span>
      </div>
      <div
        v-if="apiError"
        class="self-center justify-center row q-pt-md text-red text-overline"
      >
        {{ $t('api.error') }}
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useQuasar } from 'quasar';
import { useI18n } from 'vue-i18n';
import { FilterMethods } from 'src/types/market';
import AuctionCard from 'src/components/auction/AuctionCard.vue';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';
import { SEVERITY } from 'src/types/severity';
import { Auction } from 'src/types/market';

const $q = useQuasar();
const { t } = useI18n();
const auctions = ref([] as Record<string, any>[]);
const userText = ref(null as null | string);
const searchMethod = ref(null as null | string);
const emptySearch = ref(false);
const loading = ref(false);
const apiError = ref(false);

const searchOptions = [
  FilterMethods.TFIDF,
  FilterMethods.SVM,
  FilterMethods.LSI,
];

const search = async () => {
  emptySearch.value = false;
  if (
    userText.value === null ||
    userText.value === '' ||
    searchMethod.value === null ||
    searchMethod.value === ''
  ) {
    // invalid value
    emptySearch.value = true;
    apiError.value = false;
  } else {
    loading.value = true;
    auctions.value.length = 0;
    let res = await MARKETPLACE_API_IMP.filterAuctions(
      searchMethod.value,
      userText.value
    );
    if (res.data) {
      // data ok
      auctions.value = res.data.auctions;
      apiError.value = false;
    } else {
      // api error
      apiError.value = true;
    }
    loading.value = false;
  }
};
const clearSearch = () => {
  auctions.value.length = 0;
  userText.value = null;
  searchMethod.value = null;
  notifyAction(t('modal.search_clear'));
};
const formatNumber = (n: number, places = 4) => {
  // Round number based on the decimal places desired
  return (Math.round(n * Math.pow(10, places)) / Math.pow(10, places)).toFixed(
    places
  );
};
const notifyAction = (msg: string) => {
  $q.notify({
    type: SEVERITY.POSITIVE,
    message: msg,
    timeout: 2000,
  });
};
</script>
