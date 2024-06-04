<template>
  <div class="full-width q-px-md q-py-md pa-md">
    <div class="row text-h6">
      <q-icon name="foundation" class="q-mr-sm" size="1.5em" />
      {{ $t('account.auctions') }}
    </div>
    <div class="row text-caption">{{ $t('account.auction_edit') }}</div>
    <br />
    <div class="row q-pa-xs">
      <q-space />
      <q-btn
        icon="add_circle"
        label="New auction"
        outline
        color="primary"
        no-caps
        :to="{ name: 'auction_new' }"
      />
    </div>
    <q-table
      title="Your auctions"
      :rows="props.auctions"
      :columns="columns"
      v-model:pagination="pagination"
      row-key="__index"
      bordered
      flat
      virtual-scroll
      class="auctions_table"
    >
      <template v-slot:top-left />
      <template #body-cell-start_date="props">
        <q-td :props="props">
          <q-chip
            color="light-green-7"
            text-color="white"
            dense
            class="text-weight-bolder"
            square
            >{{ formatQDate(props.row.start_date) }}</q-chip
          >
        </q-td>
      </template>
      <template #body-cell-finish_date="props">
        <q-td :props="props">
          <q-chip
            :color="
              nowIsGreater(props.row.finish_date) ? 'red-5' : 'light-green-5'
            "
            text-color="white"
            dense
            class="text-weight-bolder"
            square
            >{{ formatQDate(props.row.finish_date) }}</q-chip
          >
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            dense
            round
            flat
            color="primary"
            :icon="
              nowIsGreater(props.row.finish_date)
                ? 'visibility_off'
                : 'visibility'
            "
            :disable="nowIsGreater(props.row.finish_date)"
            @click="toView(props.row.id)"
          />
        </q-td>
      </template>
      <template v-slot:body-cell-edit="props">
        <q-td :props="props">
          <q-btn
            dense
            round
            flat
            color="amber-6"
            icon="edit"
            @click="toEdit(props.row.id)"
            :style="nowIsGreater(props.row.start_date) ? 'display: none' : ''"
          />
        </q-td>
      </template>
      <template v-slot:body-cell-image="props">
        <q-td :props="props">
          <q-btn
            dense
            round
            flat
            color="green-6"
            icon="image"
            @click="imageModal(props.row.id)"
            :style="nowIsGreater(props.row.start_date) ? 'display: none' : ''"
          />
        </q-td>
      </template>
    </q-table>
    <q-dialog v-model="alert">
      <q-card>
        <q-card-section>
          <div class="text-h6">Upload a new image for your auction</div>
          <div class="text">Only .png files are accepted</div>
        </q-card-section>
        <q-card-section>
          <q-file
            color="purple-12"
            v-model="image"
            label="Image"
            :error="imageError"
          >
            <template v-slot:prepend>
              <q-icon name="attach_file" />
            </template>
          </q-file>
        </q-card-section>
        <q-card-section v-if="imageError">
          <div class="text-red">File is not .png type!</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Upload" color="primary" @click="imageUpload()" />
          <q-btn
            flat
            label="Cancel"
            color="red"
            v-close-popup
            @click="alert = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { Auction } from 'src/types/market';
import { date } from 'quasar';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { ref } from 'vue';
import { getDateNow } from 'src/utils/timedates';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';
import { useQuasar, QSpinnerOrbit } from 'quasar';
import { SEVERITY } from 'src/types/severity';

const $q = useQuasar();
const { t } = useI18n();
const $r = useRouter();

interface Props {
  auctions: Auction[];
}

const props = defineProps<Props>();

const imageId = ref(null as string | null);
const alert = ref(false);
const image = ref(null as any);
const imageError = ref(false as boolean);

const columns = [
  {
    name: 'title',
    label: t('auction.title'),
    field: 'title',
    required: true,
    sortable: false,
    align: 'left',
  },
  {
    name: 'init_price',
    label: t('auction.init_price'),
    field: 'init_price',
    required: true,
    sortable: false,
    align: 'left',
  },
  {
    name: 'highest_offer',
    label: t('auction.highest_bid'),
    field: 'highest_offer',
    required: true,
    sortable: false,
    align: 'left',
    format: (value: string) => (value === null ? t('none') : value),
  },
  {
    name: 'price_currency',
    label: t('auction.price_currency'),
    field: 'price_currency',
    required: true,
    sortable: false,
    align: 'left',
  },
  {
    name: 'start_date',
    label: t('auction.start_time'),
    field: 'start_date',
    required: true,
    sortable: false,
    align: 'left',
  },
  {
    name: 'finish_date',
    label: t('auction.finish_time'),
    field: 'finish_date',
    required: true,
    sortable: false,
    align: 'left',
  },
  {
    name: 'actions',
    label: t('actions'),
    field: 'actions',
    required: false,
    sortable: false,
    align: 'center',
  },
  {
    name: 'edit',
    label: '',
    field: 'edit',
    required: false,
    sortable: false,
    align: 'center',
  },
  {
    name: 'image',
    label: '',
    field: 'image',
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

const toView = (auctionId: string) => {
  $r.push({
    name: 'auction',
    params: { id: auctionId },
  });
};

const toEdit = (auctionId: string) => {
  $r.push({
    name: 'auction_update',
    params: { id: auctionId },
  });
};

const imageModal = (auctionId: string) => {
  imageId.value = auctionId;
  alert.value = true;
};

const imageUpload = async () => {
  if (imageId.value === null || image.value === null) {
    return;
  }
  const fileName = image.value.name as string;
  if (!fileName.endsWith('.png')) {
    imageError.value = true;
    return;
  }
  imageError.value = false;
  $q.loading.show({
    spinner: QSpinnerOrbit,
    spinnerColor: 'primary',
    spinnerSize: 70,
    backgroundColor: 'white',
    message: 'Loading data',
    messageColor: 'black',
  });
  const bodyFormData = new FormData();
  bodyFormData.append('file', image.value);
  const r = await MARKETPLACE_API_IMP.postImage(imageId.value, bodyFormData);
  $q.loading.hide();
  if (r.status === 200 || r.status === 201) {
    $q.notify({
      type: SEVERITY.POSITIVE,
      message: 'Image uploaded!',
      timeout: 3500,
    });
    alert.value = false;
  } else {
    $q.notify({
      type: SEVERITY.NEGATIVE,
      message: 'Image could not be uploaded!',
      timeout: 3500,
    });
  }
};

const nowIsGreater = (auction_date: string) => {
  // Return true if the time now is greater compared to the time passed
  return Date.parse(getDateNow()) > Date.parse(auction_date);
};

const formatQDate = (d: string) => {
  // quasar `date.formatDate` adds 1 hour to dates (?)
  return date.formatDate(
    date.subtractFromDate(d, {
      hours: 2,
    }),
    'DD MMM YYYY HH:mm'
  );
};
</script>

<style lang="sass">
.auctions_table
  .q-table__top
    background-color: #5d9ad6
</style>
