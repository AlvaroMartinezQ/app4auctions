<template>
  <q-page padding>
    <span v-if="processType === 'sell'">
      <SellProcessList />
    </span>
    <span v-else-if="processType === 'buy'">
      <BuyProcessList />
    </span>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import BuyProcessList from 'src/components/process/BuyProcessList.vue';
import SellProcessList from 'src/components/process/SellProcessList.vue';

const $route = useRoute();

const processType = ref('None');

const changeOP = (opType: string) => {
  if (opType.includes('sell')) processType.value = 'sell';
  else processType.value = 'buy';
};

watch(
  () => $route.name,
  () => {
    changeOP($route.name as string);
  }
);

onMounted(() => {
  changeOP($route.name as string);
});
</script>
