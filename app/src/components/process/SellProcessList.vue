<template>
  <div>
    <p class="text-h5 q-my-sm">Your sell processes</p>
    <p class="text-caption">All dates shown are in YYYY/mm/dd hh:mm format!</p>
    <q-card v-for="entry in records" :key="entry.id" class="q-my-md">
      <q-card-section class="bg-secondary text-white">
        Sell process unique number identifier {{ entry.id }}
      </q-card-section>
      <q-card-section class="q-pb-xs">
        <div class="row">
          <div class="col-6">
            Created at {{ formatDate(entry.creation_date) }}.
          </div>
          <div class="col-6" align="right">
            <q-btn
              color="primary"
              @click="getAuctionData(entry.auction_id)"
              size="sm"
            >
              <q-icon name="visibility" />
              &nbsp;Auction data
            </q-btn>
          </div>
        </div>
        <ul>
          <li>Buyer profile ID: {{ entry.buyer_id }}.</li>
          <li>Seller profile ID (yours): {{ entry.seller_id }}.</li>
          <li>Auction ID: {{ entry.auction_id }}.</li>
        </ul>
      </q-card-section>
    </q-card>
    <q-dialog
      v-model="dialog"
      persistent
      transition-show="flip-down"
      transition-hide="flip-up"
    >
      <q-card style="max-height: 50vh; max-width: 100vh">
        <q-bar class="bg-secondary">
          <q-space />
          <q-btn
            dense
            flat
            icon="close"
            v-close-popup
            @click="dialog = false"
            color="white"
          >
            <q-tooltip class="bg-primary text-white">Close</q-tooltip>
          </q-btn>
        </q-bar>
        <q-card-section>
          <div class="row text-h6">
            {{ $t('auction.title') }} {{ $t('auction.new.title') }}:
            {{ openedAuction.title }}
          </div>
          <ul>
            <li>
              {{ $t('auction.new.description') }}:
              {{ openedAuction.description }}
            </li>
            <li>
              {{ $t('auction.price_currency') }}:
              {{ openedAuction.price_currency }}
            </li>
            <li>
              {{ $t('auction.init_price') }}: {{ openedAuction.init_price }}
              {{ openedAuction.price_currency }}
            </li>
            <li v-if="openedAuction.highest_offer !== null">
              {{ $t('auction.highest_bid') }}: {{ openedAuction.highest_offer }}
              {{ openedAuction.price_currency }}
            </li>
            <li v-else>
              {{ $t('auction.highest_bid') }}: {{ $t('api.error') }}
            </li>
            <li>
              {{ $t('auction.start_time') }}:
              {{ formatDate(openedAuction.start_date) }}
            </li>
            <li>
              {{ $t('auction.finish_time') }}:
              {{ formatDate(openedAuction.finish_date) }}
            </li>
          </ul>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';
import { formatDate } from 'src/utils/timedates';
import { SEVERITY } from 'src/types/severity';

const $q = useQuasar();

const loaded = ref(false);
const apiError = ref(false);
const records = ref([] as any[]);
const dialog = ref(false);
const openedAuction = ref({} as any);

const getAuctionData = async (auctionId: string) => {
  $q.loading.show();
  const res = await MARKETPLACE_API_IMP.getAuction(auctionId);
  if (res.data) {
    openedAuction.value = res.data;
    dialog.value = true;
  } else {
    $q.notify({
      type: SEVERITY.NEGATIVE,
      message: 'Something went wrong, Please try again.',
      timeout: 2000,
    });
  }
  $q.loading.hide();
};

onMounted(async () => {
  apiError.value = false;
  loaded.value = false;
  const res = await MARKETPLACE_API_IMP.getUserSells();
  if (res.data) {
    records.value = res.data.processes;
  } else {
    apiError.value = true;
  }
  loaded.value = true;
});
</script>
