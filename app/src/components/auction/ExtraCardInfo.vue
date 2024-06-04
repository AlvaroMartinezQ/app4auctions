<template>
  <div>
    <q-card-section class="row justify-center q-my-none infoSection">
      <q-chip color="secondary" text-color="white">
        {{ $t('auction.ref') }}: {{ props.auction.id }}
      </q-chip>
    </q-card-section>
    <q-card-section class="row justify-center q-my-none infoSection">
      <q-chip
        color="deep-orange-7"
        text-color="white"
        icon="local_offer"
        class="q-py-md"
        outline
      >
        {{ $t('auction.init_price') }}: {{ auction.init_price }}
        <q-icon :name="getCurrencyIcon(auction.price_currency)" />
      </q-chip>
      <span v-if="auction.highest_offer !== null">
        <q-chip
          color="deep-orange-7"
          text-color="white"
          icon="keyboard_double_arrow_up"
          class="q-py-md"
          outline
        >
          {{ $t('auction.highest_bid') }}:&nbsp;<b>{{
            auction.highest_offer
          }}</b>
          <q-icon :name="getCurrencyIcon(auction.price_currency)" />
        </q-chip>
      </span>
      <span v-else>
        <q-chip
          color="deep-orange-7"
          text-color="white"
          icon="keyboard_double_arrow_up"
          class="q-py-md"
          outline
        >
          {{ $t('auction.highest_bid') }}:&nbsp;<b>{{ $t('none') }}</b>
        </q-chip>
      </span>
    </q-card-section>
    <q-card-section v-if="canBid" class="row justify-center">
      <bid-list v-if="bids.length !== 0" :bids="bids" class="col-5 q-mx-md" />
      <q-card
        class="bidCard col-5 q-mx-md"
        square
        v-if="!auctionFinished() && auctionStarted()"
      >
        <q-form @submit.prevent="performBid">
          <q-card-section align="center" class="q-pb-none">
            <div class="text-h6">{{ $t('bid.perform') }}</div>
          </q-card-section>
          <q-card-section class="q-pb-sm">
            <q-input
              filled
              v-model="bid"
              :label="$t('bid.quantity')"
              :error="$v.bid.$error"
              type="number"
              class="q-mx-md"
            />
          </q-card-section>
          <q-card-actions vertical align="center" class="q-py-none">
            <q-btn
              no-caps
              outline
              icon-right="gavel"
              :label="$t('bid.perform')"
              type="submit"
              color="primary"
              class="q-mb-md"
              size="md"
              :loading="loading"
              :disable="loading"
            ></q-btn>
          </q-card-actions>
          <q-card-section
            v-if="error"
            align="center"
            class="q-ma-xs text-red bg-white"
          >
            <q-icon
              name="report_problem"
              style="font-size: 1.5em"
              class="q-mr-sm q-ml-md row"
            />
            {{ errorMsg }}
          </q-card-section>
        </q-form>
      </q-card>
    </q-card-section>
    <q-card-section
      v-if="!auctionStarted()"
      class="row justify-center q-py-none"
    >
      Auction has not started yet
    </q-card-section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { Auction, Bid } from 'src/types/market';
import { required, numeric } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import BidList from 'src/components/bid/BidList.vue';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';
import { authStore } from 'src/stores/auth-store';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { getDateNow } from 'src/utils/timedates';

interface Props {
  auction: Auction;
  canBid: boolean;
}

const props = defineProps<Props>();
const $r = useRouter();
const authS = authStore();
const { t } = useI18n();

const emit = defineEmits<{
  (e: 'reload-auction-data'): void;
}>();

const bids = ref([] as Bid[]);
const bid = ref(null as null | number);

const vRules = computed(() => ({
  bid: { required, numeric },
}));
const $v = useVuelidate(vRules, { bid });

const getCurrencyIcon = (currency: string) => {
  switch (currency) {
    case 'euro':
      return currency;
    case 'pound':
      return 'currency_' + currency;
    case 'dollar':
      return 'attach_money';
    default:
      return 'question_mark';
  }
};
const auctionFinished = () => {
  return Date.parse(getDateNow()) > Date.parse(props.auction.finish_date);
};
const auctionStarted = () => {
  return Date.parse(getDateNow()) > Date.parse(props.auction.start_date);
};

const loading = ref(false);
const error = ref(false);
const errorMsg = ref('');
const performBid = async () => {
  // If not logged in redirect to login
  if (!authS.logged) {
    $r.push({
      name: 'login',
      query: { redirect: `auction ${props.auction.id}` },
    });
    return;
  }
  error.value = false;
  loading.value = true;
  $v.value.bid.$touch();
  if (!$v.value.bid.$error) {
    if (
      bid.value &&
      props.auction.highest_offer &&
      bid.value <= props.auction.highest_offer
    ) {
      // Error - bid has to be bigger
      errorMsg.value = t('bid.bad_quantity');
      error.value = true;
    } else {
      let res = await MARKETPLACE_API_IMP.postBid(props.auction.id, {
        offer_ammount: bid.value,
      });
      if (res.data) {
        // All ok - bid performed
        bid.value = null;
        $v.value.bid.$reset();
      } else {
        // Alert about error
        errorMsg.value = t('api.error') + res.errorData.detail;
        error.value = true;
      }
    }
  }
  loading.value = false;
};

if (import.meta.env.VITE_WS_ON === 'on' && props.canBid) {
  const marketWS = new WebSocket(
    import.meta.env.VITE_WS_AUCTION_URL + `${props.auction.id}/`
  );

  marketWS.addEventListener('open', () => {
    // Open the ws connection
    console.log('[Auction ws] - connection started');
  });

  marketWS.addEventListener('message', function (event) {
    emit('reload-auction-data');
    // The following code ensures the reload of the `bid-table` values
    let newBid = JSON.parse(event.data) as Bid;
    newBid.creation_date = new Date(newBid.creation_date).toLocaleDateString();
    // Update the new Bid or if it is already in the bids array update it
    let inArray = false;
    bids.value.forEach((element) => {
      if (element.id === newBid.id) {
        // Already exists - update it
        Object.assign(element, newBid);
        inArray = true;
      }
    });
    if (!inArray) {
      // Add the bid
      bids.value.push(newBid);
    }
  });

  onUnmounted(() => {
    marketWS.close();
  });
}

onMounted(() => {
  bids.value = props.auction.bids;
});
</script>

<style>
.infoSection {
  padding: 5px;
}
.bidCard {
  max-width: 400px;
  max-height: 195px;
}
</style>
