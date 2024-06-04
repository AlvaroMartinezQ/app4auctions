<template>
  <div class="q-gutter-md q-pa-md">
    <div class="row">
      <q-input
        v-model="userData.personal_name"
        :label="$t('account.name')"
        class="q-pa-xs col-6"
        :error="$v.userData.personal_name.$error"
        :rules="requiredRule"
      >
        <template v-slot:prepend>
          <q-icon name="badge" />
        </template>
      </q-input>
      <q-input
        v-model="userData.personal_surname"
        :label="$t('account.surname')"
        class="q-pa-xs col-6"
        :error="$v.userData.personal_surname.$error"
        :rules="requiredRule"
      >
        <template v-slot:prepend>
          <q-icon name="badge" />
        </template>
      </q-input>
    </div>
    <div class="row">
      <q-input
        v-model="userData.email"
        :label="$t('account.email')"
        class="q-pa-xs col-12"
        :error="$v.userData.email.$error"
        :rules="requiredRule"
        disable
      >
        <template v-slot:prepend>
          <q-icon name="email" />
        </template>
      </q-input>
    </div>
    <div class="row">
      <q-input
        v-model="userData.address"
        :label="$t('account.address')"
        class="q-pa-xs col-8"
        :error="$v.userData.address.$error"
        :rules="requiredRule"
      />
      <q-input
        v-model="userData.country"
        :label="$t('account.country')"
        class="q-pa-xs col-4"
        :error="$v.userData.country.$error"
        :rules="requiredRule"
      />
    </div>
    <div class="row">
      <q-input
        v-model="userData.phone"
        :label="$t('account.phone')"
        class="q-pa-xs col-6"
        :error="$v.userData.phone.$error"
        :rules="requiredRule"
      />
      <q-input
        v-model="userData.identification_number"
        :label="$t('account.id_num')"
        class="q-pa-xs col-6"
        :error="$v.userData.identification_number.$error"
        :rules="requiredRule"
      />
    </div>
    <div class="row text-overline q-mt-md">
      <q-icon name="verified" color="green" size="2em" />
      Member since:
      {{ new Date(authS.member_since as string).toLocaleString('es-ES') }}
    </div>
    <q-separator />
    <q-card-actions align="right">
      <q-btn
        color="primary"
        :label="$t('account.update_btn')"
        @click="updateUserData"
        :loading="loading"
        no-caps
      />
    </q-card-actions>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useI18n } from 'vue-i18n';
import useVuelidate from '@vuelidate/core';
import { authStore } from 'src/stores/auth-store';
import { USERPROFILE } from 'src/types/auth';
import { requiredRule } from 'src/rules/form';
import { email, required } from '@vuelidate/validators';
import AUTH_API_IMP from 'src/api/endpoints/auth';
import { SEVERITY } from 'src/types/severity';

const $q = useQuasar();
const { t } = useI18n();
const authS = authStore();

const loading = ref(false);
const userData = reactive({} as USERPROFILE);
const vRules = computed(() => ({
  userData: {
    email: { required, email },
    identification_number: { required },
    personal_name: { required },
    personal_surname: { required },
    country: { required },
    address: { required },
    phone: { required },
  },
}));
const $v = useVuelidate(vRules, { userData });

const updateUserData = async () => {
  loading.value = true;
  $v.value.userData.$touch();
  if (!$v.value.userData.$error) {
    const userD = {
      identification_number: userData.identification_number,
      personal_name: userData.personal_name,
      personal_surname: userData.personal_surname,
      country: userData.country,
      address: userData.address,
      phone: userData.phone,
    };
    const res = await AUTH_API_IMP.updateUser(userData.email, userD);
    if (res.data) {
      notifyAction(t('account.update_ok'), SEVERITY.POSITIVE);
      authS.refreshData();
    } else {
      notifyAction(t('account.update_failed'), SEVERITY.NEGATIVE);
    }
  }
  loading.value = false;
};

const notifyAction = (msg: string, col: string) => {
  $q.notify({
    type: col,
    message: msg,
    timeout: 2000,
  });
};

onMounted(() => {
  userData.email = authS.email as string;
  userData.identification_number = authS.identification_number as string;
  userData.personal_name = authS.personal_name as string;
  userData.personal_surname = authS.personal_surname as string;
  userData.country = authS.country as string;
  userData.address = authS.address as string;
  userData.phone = authS.phone as string;
});
</script>
