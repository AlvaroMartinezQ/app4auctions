<template>
  <div class="full-width q-px-md q-py-md pa-md">
    <div class="row text-h6">
      <q-icon name="foundation" class="q-mr-sm" size="1.5em" />
      {{ $t('account.bids') }}
    </div>
    <div class="row text-caption">{{ $t('account.bid_detail') }}</div>
    <br />
    <q-table
      :rows="props.bids"
      :columns="columns"
      v-model:pagination="pagination"
      row-key="__index"
      bordered
      flat
      virtual-scroll
      class="auctions_table"
    >
      <template v-slot:top-left />
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            dense
            round
            flat
            color="primary"
            icon="visibility"
            @click="toView(props.row.id)"
          />
        </q-td>
      </template>
    </q-table>

    <q-dialog
      v-model="dialog"
      persistent
      :maximized="true"
      transition-show="slide-up"
      transition-hide="slide-down"
    >
      <q-card class="bg-primary text-white">
        <q-bar>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup />
        </q-bar>
        <q-card-section class="q-pt-none" v-if="!loading">
          <auction-card
            :auction="(auctionData as Auction)"
            :info="true"
            :canPerformBid="false"
            :fromUserBidList="true"
            class="q-mt-md"
          />
        </q-card-section>
        <q-card-section class="q-pt-none" v-else>
          {{ $t('api.loading') }}
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { date } from 'quasar';
import { Auction, Bid } from 'src/types/market';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';
import AuctionCard from '../../auction/AuctionCard.vue';
import { SEVERITY } from 'src/types/severity';

const $q = useQuasar();

interface Props {
  bids: Bid[];
}

const props = defineProps<Props>();

const { t } = useI18n();

const dialog = ref(false);
const auctionData = ref(null as null | Auction);
const loading = ref(false);

const columns = [
  {
    name: 'reference',
    label: t('bid.ref'),
    field: 'id',
    required: true,
    sortable: false,
    align: 'left',
  },
  {
    name: 'offer_ammount',
    label: t('bid.quantity'),
    field: 'offer_ammount',
    required: true,
    sortable: false,
    align: 'left',
  },
  {
    name: 'creation_date',
    label: t('created'),
    field: 'creation_date',
    required: true,
    sortable: false,
    align: 'left',
    format: (value: string) => formatQDate(value),
  },
  {
    name: 'actions',
    label: t('auction.view_data'),
    field: 'actions',
    required: false,
    sortable: false,
    align: 'center',
  },
];

const pagination = ref({
  descending: false,
  page: 1,
  rowsPerPage: 10,
});

const formatQDate = (d: string) => {
  // quasar `date.formatDate` adds 1 hour to dates (?)
  return date.formatDate(
    date.subtractFromDate(d, {
      hours: 1,
    }),
    'DD MMM YYYY HH:mm'
  );
};

const toView = async (bidRef: string) => {
  loading.value = true;
  let res = await MARKETPLACE_API_IMP.getAuctionBidRef(bidRef);
  if (res.data) {
    auctionData.value = res.data as Auction;
    dialog.value = true;
  } else {
    $q.notify({
      type: SEVERITY.NEGATIVE,
      message: t('api.error'),
      timeout: 2000,
    });
  }
  loading.value = false;
};
</script>
