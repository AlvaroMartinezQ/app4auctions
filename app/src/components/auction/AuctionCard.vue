<template>
  <q-intersection transition="jump-up" transition-duration="1500" once>
    <q-card>
      <q-card-section
        v-if="!auctionStarted"
        class="row justify-center"
        style="background-color: grey"
      >
        <q-icon
          class="col-12 q-ma-none q-pa-none"
          name="alarm"
          size="5em"
          color=""
        />
        <p class="row text-h6">{{ $t('auction.not_started') }}</p>
      </q-card-section>
      <div v-if="auctionStarted">
        <q-card-section class="row">
          <q-icon name="gavel" size="3em" color="primary" class="col-2" />
          <q-separator vertical size="0.05em" color="grey" />
          <div class="col-1"></div>
          <div class="col-8">
            <q-badge
              multi-line
              class="text-subtitle1 text-weight-bold q-mt-sm"
              color="white"
              text-color="black"
              :label="props.auction.title"
            ></q-badge>
          </div>
        </q-card-section>
        <q-separator size="0.15em" color="grey" class="q-mx-sm" />
        <q-card-section v-if="auctionStarted">
          <div class="col-12 q-mb-xs">
            <q-img
              :src="`${backend}/market/auction/image/${props.auction.id}/`"
              spinner-color="white"
              style="height: 100px; max-width: 200px"
            />
          </div>
        </q-card-section>
        <q-card-section class="row">
          <div class="col-12 q-mb-xs">
            <span v-if="auction.tags.length > 0">
              <q-badge
                v-for="label in auction.tags.split(' ')"
                rounded
                color="blue-10"
                :label="label"
                :key="label"
                class="q-mx-xs"
                outline
                align="middle"
              />
            </span>
            <q-badge
              rounded
              color="deep-orange-7"
              :label="$t('bid.title') + 's: ' + auction.bids.length"
              class="q-mx-xs"
              outline
              align="middle"
            />
          </div>
          <q-badge
            multi-line
            class="text-body2"
            color="white"
            text-color="black"
            :label="auction.description"
            style="word-break: normal"
          ></q-badge>
        </q-card-section>
        <q-card-section class="row" v-if="info">
          <q-badge
            multi-line
            class="text-overline col-5 q-my-xs q-mx-sm justify-center"
            color="green-3"
            text-color="white"
            :label="`Active since: ${formatDate(auction.start_date)}`"
            style="word-break: normal"
          ></q-badge>
          <q-space />
          <q-badge
            multi-line
            class="text-overline col-5 q-my-xs q-mx-sm justify-center"
            color="red-3"
            text-color="white"
            :label="`Ends at: ${formatDate(auction.finish_date)}`"
          ></q-badge>
        </q-card-section>
        <q-card-section>
          <time-left :timeLeft="auction.finish_date" />
        </q-card-section>
        <q-separator v-if="info" size="0.05em" color="grey" class="q-mx-sm" />
        <extra-card-info-vue
          v-if="info"
          :auction="props.auction"
          :canBid="canPerformBid"
          @reload-auction-data="emitToParent()"
        />
        <q-card-actions v-if="canViewAuction()" align="right" class="q-mr-sm">
          <q-btn
            outline
            color="primary"
            v-if="!info || fromUserBidList"
            :to="{
              name: 'auction',
              params: { id: auction.id },
            }"
          >
            <q-icon color="primary" name="preview" class="q-mr-sm" />
            See auction
          </q-btn>
        </q-card-actions>
      </div>
    </q-card>
  </q-intersection>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import TimeLeft from 'src/components/common/TimeLeft.vue';
import ExtraCardInfoVue from 'src/components/auction/ExtraCardInfo.vue';
import { Auction } from 'src/types/market';
import { getDateNow, formatDate } from 'src/utils/timedates';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';

interface Props {
  auction: Auction;
  info: boolean;
  canPerformBid: boolean;
  fromUserBidList?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  fromUserBidList: false,
});

const auctionStarted = ref(false);

const image = ref(null as any);
const backend = ref(import.meta.env.VITE_BACKEND_URL);

const emit = defineEmits<{
  (e: 'reload-auction'): void;
}>();

const emitToParent = () => {
  emit('reload-auction');
};

const canViewAuction = () => {
  // If true, auction can be accessed (seen)
  return Date.parse(getDateNow()) < Date.parse(props.auction.finish_date);
};

onMounted(async () => {
  if (
    Date.parse(getDateNow()) > Date.parse(formatDate(props.auction.start_date))
  )
    auctionStarted.value = true;
  if (auctionStarted.value === true) {
    const r = await MARKETPLACE_API_IMP.getImage(props.auction.id);
    if (r.status === 200) {
      image.value = r.data;
    }
  }
});
</script>
