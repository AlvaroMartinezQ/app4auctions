<template>
  <q-page padding>
    <auction-card
      v-if="status === APIStatus.OK"
      :auction="(auctionData as Auction)"
      :info="true"
      :canPerformBid="true"
      @reload-auction="loadAuction()"
    />
    <div
      class="row text-red self-center justify-center text-h6"
      v-else-if="status === APIStatus.NOT_FOUND"
    >
      {{ $t('auction.not_found', { id: $route.params.id }) }}
    </div>
    <div
      class="row text-red self-center justify-center text-h6"
      v-else-if="status === APIStatus.ERROR"
    >
      {{ $t('api.error') }}
    </div>
    <div
      class="row self-center justify-center"
      v-else-if="status === APIStatus.WORKING"
    >
      <q-spinner-orbit color="primary" size="5em" />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import AuctionCard from 'src/components/auction/AuctionCard.vue';
import { Auction } from 'src/types/market';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';
import { APIStatus } from 'src/enums/api';

const $route = useRoute();

const auctionData = ref(null as null | Auction);

const status = ref(APIStatus.WORKING);

const loadAuction = async () => {
  let res = await MARKETPLACE_API_IMP.getAuction($route.params.id as string);
  if (res.data) {
    auctionData.value = res.data as Auction;
    status.value = APIStatus.OK;
  } else {
    if ('statusCode' in res && res.statusCode === 404) {
      // Not found
      status.value = APIStatus.NOT_FOUND;
    } else {
      // Another error
      status.value = APIStatus.ERROR;
    }
  }
};

onMounted(async () => {
  await loadAuction();
});
</script>
