<template>
  <q-list bordered>
    <q-item class="row q-pb-none">
      <q-item-section class="col-12">{{ $t('bid.list') }}</q-item-section>
    </q-item>
    <q-separator size="0.15em" color="grey" class="q-mx-sm" />
    <q-item class="row q-py-xs">
      <q-item-section class="col-7">{{ $t('bid.ref') }}</q-item-section>
      <q-item-section class="col-2">{{ $t('bid.quantity') }}</q-item-section>
      <q-item-section class="col-3">{{ $t('created') }}</q-item-section>
    </q-item>
    <q-separator size="0.15em" color="grey" class="q-mx-sm" />
    <q-item v-for="bid in bids" :key="bid.id" class="row q-pt-xs">
      <q-item-section class="col-7">{{ bid.id }}</q-item-section>
      <q-item-section class="col-2">{{ bid.offer_ammount }}</q-item-section>
      <q-item-section class="col-3">{{
        new Date(bid.creation_date).toLocaleDateString()
      }}</q-item-section>
    </q-item>
  </q-list>
</template>

<script setup lang="ts">
import { Bid } from 'src/types/market';

interface Props {
  bids: Bid[];
}

defineProps<Props>();
</script>
