<template padding>
  <div v-if="loaded">
    <user-auction-list :auctions="userAuctions" />
  </div>
</template>

<script setup lang="ts">
import UserAuctionList from 'src/components/auction/user/UserAuctionList.vue';
import { onMounted, ref } from 'vue';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';
import { Auction } from 'src/types/market';

const loaded = ref(false);
const userAuctions = ref([] as Auction[]);

onMounted(async () => {
  const res = await MARKETPLACE_API_IMP.getUserAuctions();
  if (res.data) {
    userAuctions.value = res.data.auctions;
  }
  loaded.value = true;
});
</script>
