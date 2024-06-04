<template>
  <q-page padding>
    <div class="fit wrap self-center justify-center row">
      <div v-if="activationStatus === APIStatus.WORKING">
        <span class="row">{{ $t('account.activating') }}</span>
      </div>
      <div v-else-if="activationStatus === APIStatus.OK">
        <span class="row text-h6">{{ $t('account.success_activation') }}</span>
        <span class="row self-center justify-center">
          <q-icon name="verified" size="5em" color="green" />
        </span>
      </div>
      <div v-else>
        <span class="row text-h6">{{ $t('account.invalid_activation') }}</span>
        <span class="row self-center justify-center">
          <q-icon name="report_gmailerrorred" size="5em" color="red" />
        </span>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import AUTH_API_IMP from 'src/api/endpoints/auth';
import { APIStatus } from 'src/enums/api';

const $route = useRoute();

const activationStatus = ref(APIStatus.WORKING);

onMounted(async () => {
  let res = await AUTH_API_IMP.activateUser($route.params.id as string);
  if (res.data) {
    // User activated
    activationStatus.value = APIStatus.OK;
  } else {
    // Error
    activationStatus.value = APIStatus.ERROR;
  }
});
</script>
