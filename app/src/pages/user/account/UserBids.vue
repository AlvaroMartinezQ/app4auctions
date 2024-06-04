<template padding>
  <div v-if="loaded">
    <user-bid-list :bids="userBids" />
  </div>
</template>

<script setup lang="ts">
import UserBidList from 'src/components/bid/user/UserBidList.vue';
import { onMounted, ref } from 'vue';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';
import { Bid } from 'src/types/market';

const loaded = ref(false);
const userBids = ref([] as Bid[]);

onMounted(async () => {
  const res = await MARKETPLACE_API_IMP.getUserBids();
  if (res.data) {
    userBids.value = res.data.bids;
  }
  loaded.value = true;
});
</script>
