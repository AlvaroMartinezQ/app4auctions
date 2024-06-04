<template>
  <div class="fit row self-center justify-center">
    <auction-card
      v-for="auction in props.auctions"
      :key="auction.id"
      :auction="auction"
      :info="false"
      :canPerformBid="false"
      class="col-8 q-my-md"
    />
  </div>
</template>

<script setup lang="ts">
import AuctionCard from 'src/components/auction/AuctionCard.vue';
import { Auction } from 'src/types/market';

interface Props {
  auctions: Auction[];
}

const props = defineProps<Props>();
</script>
