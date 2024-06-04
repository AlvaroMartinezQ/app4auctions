<template>
  <q-form greedy @submit.prevent="createAuction">
    <q-card class="row border-primary">
      <q-card-section class="row col-12">
        <q-item>
          <q-item-section avatar>
            <q-avatar>
              <img src="~/assets/icon.jpg" />
            </q-avatar>
          </q-item-section>
          <q-item-section class="non-selectable">
            <q-item-label v-if="!isEdit" class="text-h5 text-weight-bold">
              {{ $t('auction.new.create') }}
            </q-item-label>
            <q-item-label v-else class="text-h5 text-weight-bold">
              {{ $t('auction.update.title') }}
            </q-item-label>
            <q-item-label caption>{{ $t('company') }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-card-section>
      <q-card-section class="row col-12 q-pb-xs q-pt-md">
        <q-input
          filled
          v-model="newAuctionData.title"
          :label="$t('auction.new.title')"
          class="q-pa-xs col-12"
          :rules="requiredRule"
        />
      </q-card-section>
      <q-card-section class="row col-12">
        <q-input
          filled
          v-model="newAuctionData.description"
          :label="$t('auction.new.description')"
          class="q-pa-xs col-12"
          type="textarea"
          clearable
          :rules="requiredRule"
        />
      </q-card-section>
      <q-card-section
        class="row col-12 q-pt-xs justify-center items-center content-center"
      >
        <q-input
          filled
          v-model="newAuctionData.init_price"
          :label="$t('auction.init_price')"
          class="q-pa-xs col-4"
          type="number"
        />
        <q-select
          filled
          v-model="newAuctionData.price_currency"
          :label="$t('auction.price_currency')"
          class="q-pa-xs col-4"
          :options="currencyOptions"
        />
      </q-card-section>
      <q-card-section
        class="row col-12 q-py-none justify-center items-center content-center"
      >
        <q-input
          filled
          v-model="newAuctionData.start_date"
          class="col-4 q-mx-xs"
          :label="$t('auction.start_time')"
          :error="startDateInvalid"
          :rules="requiredRule"
        >
          <template v-slot:append>
            <q-icon name="event" class="cursor-pointer">
              <q-popup-proxy
                cover
                transition-show="scale"
                transition-hide="scale"
              >
                <div class="row items-center justify-end">
                  <q-date
                    v-model="newAuctionData.start_date"
                    mask="YYYY-MM-DD HH:mm"
                    :options="optionsDate"
                  />
                  <q-time
                    v-model="newAuctionData.start_date"
                    mask="YYYY-MM-DD HH:mm"
                    format24h
                  />
                </div>
                <div class="row items-center justify-end q-ma-sm">
                  <q-btn
                    v-close-popup
                    label="Ok"
                    color="primary"
                    no-caps
                    @click="validateStartDate(newAuctionData.start_date)"
                  />
                </div>
              </q-popup-proxy>
            </q-icon>
          </template>
        </q-input>
        <q-input
          filled
          v-model="newAuctionData.finish_date"
          class="col-4 q-mx-xs"
          :label="$t('auction.finish_time')"
          :error="finishDateInvalid"
          :rules="requiredRule"
        >
          <template v-slot:append>
            <q-icon name="event" class="cursor-pointer">
              <q-popup-proxy
                cover
                transition-show="scale"
                transition-hide="scale"
              >
                <div class="row items-center justify-end">
                  <q-date
                    v-model="newAuctionData.finish_date"
                    mask="YYYY-MM-DD HH:mm"
                    :options="optionsDate"
                  />
                  <q-time
                    v-model="newAuctionData.finish_date"
                    mask="YYYY-MM-DD HH:mm"
                    format24h
                  />
                </div>
                <div class="row items-center justify-end q-ma-sm">
                  <q-btn
                    v-close-popup
                    label="Ok"
                    color="primary"
                    no-caps
                    @click="validateFinishDate(newAuctionData.finish_date)"
                  />
                </div>
              </q-popup-proxy>
            </q-icon>
          </template>
        </q-input>
      </q-card-section>
      <q-card-section
        class="row col-12 q-pt-none justify-center items-center content-center"
      >
        <q-chip
          v-for="tag in tags"
          :key="tag"
          color="accent"
          text-color="white"
          icon="bookmark"
          outline
        >
          {{ tag }}
          <q-btn
            size="xs"
            class="q-ml-sm q-py-xs"
            icon="clear"
            round
            outline
            @click="deleteTag(tag)"
          />
        </q-chip>
      </q-card-section>
      <q-card-section
        class="row col-12 q-pt-none justify-center items-center content-center"
      >
        <q-input
          v-model="currentTag"
          :label="$t('auction.tags')"
          class="q-pa-xs col-8"
          @keydown.space="addTag"
        >
          <q-tooltip
            class="bg-primary text-caption"
            transition-show="flip-right"
            transition-hide="flip-left"
          >
            {{ $t('auction.new.tags_desc') }}
          </q-tooltip>
        </q-input>
      </q-card-section>
      <q-card-section div class="row col-12 justify-center" v-if="apiError">
        <q-banner dense class="bg-grey-2">
          <template v-slot:avatar>
            <q-icon name="priority_high" color="red" />
          </template>
          {{ $t('api.error') }}
        </q-banner>
      </q-card-section>
      <q-card-actions align="right" class="row col-12">
        <q-btn
          outline
          :label="isEdit ? $t('auction.update.btn') : $t('auction.new.btn')"
          color="green"
          type="submit"
          :loading="loading"
          :disable="loading"
          no-caps
          :icon-right="isEdit ? 'save' : 'add_circle'"
        />
      </q-card-actions>
    </q-card>
  </q-form>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useQuasar, QSpinnerOrbit } from 'quasar';
import { useRouter, useRoute } from 'vue-router';
import { AuctionNew } from 'src/types/market';
import { requiredRule } from 'src/rules/form';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import MARKETPLACE_API_IMP from 'src/api/endpoints/marketplace';
import { formatDate } from 'src/utils/timedates';
import { SEVERITY } from 'src/types/severity';

const $q = useQuasar();
const $r = useRouter();
const $route = useRoute();

const newAuctionData = reactive({} as AuctionNew);
const currencyOptions = ref(['euro', 'pound', 'dollar'] as string[]);
const currentTag = ref(null as null | string);
const tags = ref([] as string[]);
const optionsDate = (date: string) => {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  return Date.parse(date) > Date.parse(yesterday.toString());
};
const startDateInvalid = ref(false);
const finishDateInvalid = ref(false);
const loading = ref(false);
const apiError = ref(false);
const isEdit = ref(false);

const vRules = computed(() => ({
  newAuctionData: {
    title: { required },
    description: { required },
    init_price: {},
    price_currency: { required },
    start_date: { required },
    finish_date: { required },
    tags: {},
  },
}));
const $v = useVuelidate(vRules, { newAuctionData });

const validateStartDate = (date: string) => {
  const now = new Date();
  const parsedDate = Date.parse(date);
  if (Date.parse(now.toString()) > parsedDate) {
    // Start date > now
    startDateInvalid.value = true;
    return;
  }
  if (newAuctionData.finish_date !== undefined) {
    if (parsedDate >= Date.parse(newAuctionData.finish_date)) {
      // Finish date < start date
      startDateInvalid.value = true;
      return;
    }
  }
  startDateInvalid.value = false;
};
const validateFinishDate = (date: string) => {
  const now = new Date();
  const parsedDate = Date.parse(date);
  if (Date.parse(now.toString()) > parsedDate) {
    // Start date > now
    finishDateInvalid.value = true;
    return;
  }
  if (newAuctionData.start_date !== undefined) {
    if (parsedDate <= Date.parse(newAuctionData.start_date)) {
      // Finish date < start date
      finishDateInvalid.value = true;
      return;
    }
  }
  finishDateInvalid.value = false;
};
const addTag = () => {
  if (
    currentTag.value !== null &&
    currentTag.value !== '' &&
    currentTag.value !== ' '
  )
    tags.value.push(currentTag.value.trim());
  currentTag.value = null;
};
const deleteTag = (toDelete: string) => {
  for (const index in tags.value) {
    if (tags.value[index] === toDelete) {
      tags.value.splice(parseInt(index), 1);
    }
  }
};
const createAuction = async () => {
  loading.value = true;
  $v.value.newAuctionData.$touch();
  if (!$v.value.$error) {
    // Check if user set up tags
    if (tags.value.length > 0) {
      let auctionTags = '';
      for (const tag of tags.value) {
        auctionTags += tag + ' ';
      }
      newAuctionData.tags = auctionTags.trim();
    } else {
      newAuctionData.tags = '';
    }
    let res;
    if (!isEdit.value) {
      res = await MARKETPLACE_API_IMP.postAuction(newAuctionData);
    } else {
      res = await MARKETPLACE_API_IMP.putAuction(
        $route.params.id as string,
        newAuctionData
      );
    }
    if (res.data) {
      apiError.value = false;
      $r.push({
        name: 'user_auction_list',
      });
      $q.notify({
        type: SEVERITY.POSITIVE,
        message: 'Auction created',
        timeout: 2000,
      });
    } else {
      apiError.value = true;
    }
  }
  loading.value = false;
};
onMounted(async () => {
  // Check if the router has an id - if so this is an update
  if ($route.params.id) {
    $q.loading.show({
      spinner: QSpinnerOrbit,
      spinnerColor: 'primary',
      spinnerSize: 70,
      backgroundColor: 'white',
      message: 'Loading data',
      messageColor: 'black',
    });
    // Check if the auction is owned by the user
    let resCanEdit = await MARKETPLACE_API_IMP.getUserCanEditAuction(
      $route.params.id as string
    );
    if (resCanEdit.status && resCanEdit.status === 200) {
      // Request data for the existing auction
      let resAuction = await MARKETPLACE_API_IMP.getAuction(
        $route.params.id as string
      );
      if (resAuction.data) {
        Object.assign(newAuctionData, resAuction.data as AuctionNew);
        tags.value = newAuctionData.tags.trim().split(' ');
        // Format dates for the Quasar popup input
        newAuctionData.start_date = formatDate(newAuctionData.start_date);
        newAuctionData.finish_date = formatDate(newAuctionData.finish_date);
        // Set `isEdit` to true to displey different texts in html
        isEdit.value = true;
      }
    } else {
      $r.push({
        name: 'user_auction_list',
      });
      $q.notify({
        type: SEVERITY.NEGATIVE,
        message: 'You can not edit that!',
        timeout: 3500,
      });
    }
    $q.loading.hide();
  }
});
</script>
