<template>
  <q-page padding v-if="loaded">
    <div class="row full-width self-center justify-center text-h4">
      {{ $t('auction.desc') }}
    </div>
    <q-separator class="q-mt-sm" size="0.1em" color="black"></q-separator>
    <div class="row full-width self-end justify-end q-ma-md">
      <q-btn
        outline
        color="primary"
        label="Filter auctions"
        icon="search"
        class="q-ma-xs"
        no-caps
        :to="{ name: 'auction_filter' }"
      />
    </div>
    <q-pagination
      v-model="page"
      :max="100"
      :max-pages="6"
      :boundary-numbers="false"
      boundary-links
      class="row full-width self-center justify-center text-subtitle2 q-mt-md"
    />
    <auction-list
      :auctions="marketS.get_auctions()"
      v-if="marketS.auctions_length_valid()"
    />
    <div v-else>
      <div
        class="row full-width self-center justify-center text-subtitle2 q-mt-md"
      >
        {{ $t('auction.no_active') }}
      </div>
      <div class="row full-width self-center justify-center">
        <q-icon name="sentiment_dissatisfied" size="8em" />
      </div>
    </div>
    <q-pagination
      v-model="page"
      :max="100"
      :max-pages="6"
      :boundary-numbers="false"
      boundary-links
      class="row full-width self-center justify-center text-subtitle2 q-mt-md"
    />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import MARKETPLACE_API_IMP from 'app/src/api/endpoints/marketplace';
import AuctionList from 'src/components/auction/AuctionList.vue';
import { Auction } from 'src/types/market';
import { marketStore } from 'src/stores/market-store';
import { useRouter } from 'vue-router';

const $r = useRouter();
const marketS = marketStore();

const activeAuctions = ref([] as Auction[]);

const loaded = ref(false); // To avoid not showing the 'no auctions' part until all has loaded
const page = ref(1); // Current page

watch(page, async (newVal) => {
  loaded.value = false;
  await queryData(newVal);
  loaded.value = true;
});

const queryData = async (page: number) => {
  $r.replace({ name: 'market', query: { page: page } });
  let res = await MARKETPLACE_API_IMP.getAuctions(page);
  if (res.data) {
    marketS.set_auctions(res.data.auctions as Auction[]);
    activeAuctions.value = res.data.auctions as Auction[];
  }
};

onMounted(async () => {
  await queryData(1);
  loaded.value = true;
});
</script>
