<template>
  <q-table
    :title="t('bid.list')"
    :rows="rows"
    :columns="columns"
    row-key="id"
    :loading="loading"
    icon-next-page="arrow_forward_ios"
    icon-prev-page="arrow_back_ios"
    icon-first-page="first_page"
    icon-last-page="last_page"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { QTableProps } from 'quasar';
import { useI18n } from 'vue-i18n';
import { Bid } from 'src/types/market';

const { t } = useI18n();

interface Props {
  bids: Bid[];
}

const props = defineProps<Props>();

const columns: QTableProps['columns'] = [
  {
    name: 'id',
    required: true,
    label: t('bid.ref'),
    align: 'left',
    field: 'id',
    sortable: false,
  },
  {
    name: 'offer',
    align: 'center',
    label: t('bid.offer_quantity'),
    field: 'offer_ammount',
    sortable: false,
  },
  {
    name: 'date',
    align: 'right',
    label: t('created'),
    field: 'creation_date',
    sortable: false,
  },
];

const rows = ref([] as Bid[]);
const loading = ref(true);

onMounted(() => {
  props.bids.forEach((bid) => {
    // Parse the bid creation date to a more human readable string
    let auxBid = bid;
    auxBid.creation_date = new Date(auxBid.creation_date).toLocaleDateString();
    rows.value.push(auxBid);
  });
  loading.value = false;
});
</script>
