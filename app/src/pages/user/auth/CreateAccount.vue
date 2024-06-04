<template>
  <q-page padding>
    <q-form greedy @submit.prevent="createUser">
      <div class="fit wrap self-center justify-center row">
        <q-intersection
          transition="flip-up"
          once
          class="col-xs-12 col-md-10 col-lg-8"
        >
          <q-card
            class="q-pa-sm justify-center items-center content-center animate-pop"
          >
            <q-item>
              <q-item-section avatar>
                <q-avatar>
                  <img src="~/assets/icon.jpg" />
                </q-avatar>
              </q-item-section>
              <q-item-section class="non-selectable">
                <q-item-label class="text-h5 text-weight-bold">{{
                  $t('account.create')
                }}</q-item-label>
                <q-item-label caption>{{ $t('company') }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-card-section class="row q-pb-xs q-pt-md">
              <q-input
                filled
                v-model="userData.personal_name"
                :label="$t('account.name')"
                class="q-pa-xs col-6"
                :error="$v.userData.personal_name.$error"
                :rules="requiredRule"
              />
              <q-input
                filled
                v-model="userData.personal_surname"
                :label="$t('account.surname')"
                class="q-pa-xs col-6"
                :error="$v.userData.personal_surname.$error"
                :rules="requiredRule"
              />
            </q-card-section>
            <q-card-section class="row q-py-sm">
              <q-input
                filled
                v-model="userData.email"
                :label="$t('account.email')"
                class="q-pa-xs col-4"
                :error="$v.userData.email.$error"
                :rules="requiredRule"
              />
              <q-input
                filled
                v-model="userData.phone"
                :label="$t('account.phone')"
                class="q-pa-xs col-3"
                :error="$v.userData.phone.$error"
                :rules="requiredRule"
              />
              <q-input
                filled
                v-model="userData.identification_number"
                :label="$t('account.id_num')"
                class="q-pa-xs col-5"
                :error="$v.userData.identification_number.$error"
                :rules="requiredRule"
              />
            </q-card-section>
            <q-card-section class="row q-py-sm">
              <q-input
                filled
                v-model="userData.address"
                :label="$t('account.address')"
                class="q-pa-xs col-9"
                :error="$v.userData.address.$error"
                :rules="requiredRule"
              />
              <q-input
                filled
                v-model="userData.country"
                :label="$t('account.country')"
                class="q-pa-xs col-3"
                :error="$v.userData.country.$error"
                :rules="requiredRule"
              />
            </q-card-section>
            <q-card-section class="row q-py-sm">
              <q-input
                filled
                v-model="userData.password"
                :label="$t('account.password')"
                class="q-pa-xs col-6"
                :error="$v.userData.password.$error"
                :rules="requiredRule"
                type="password"
              />
              <q-input
                filled
                v-model="repeatPassword"
                :label="$t('account.repeat_password')"
                class="q-pa-xs col-6"
                :error="$v.repeatPassword.$error"
                :rules="requiredRule"
                type="password"
              />
            </q-card-section>
            <q-card-section class="row q-py-sm">
              <q-checkbox v-model="ageOk" label="18+" />
              <q-input
                filled
                v-model="dateOfBirth"
                label="Date of birth"
                class="q-pa-md"
                :rules="requiredRule"
              >
                <q-popup-proxy
                  @before-show="updateProxy"
                  cover
                  transition-show="scale"
                  transition-hide="scale"
                >
                  <q-date v-model="dateOfBirth">
                    <div class="row items-center justify-end q-gutter-sm">
                      <q-btn
                        label="Cancel"
                        color="primary"
                        flat
                        v-close-popup
                      />
                      <q-btn
                        label="OK"
                        color="primary"
                        flat
                        @click="save"
                        v-close-popup
                      />
                    </div>
                  </q-date>
                </q-popup-proxy>
              </q-input>
            </q-card-section>
            <q-separator size="0.05em" color="grey" class="q-mt-md" />
            <q-card-actions class="row q-pt-md">
              <q-banner v-if="error" class="text-red bg-white">
                <q-icon name="report_problem" style="font-size: 1.5em" />
                &nbsp;&nbsp;{{ errorMsg }}
              </q-banner>
              <q-space />
              <q-btn
                no-caps
                outline
                icon="person_add"
                class="text-primary q-mr-md"
                :label="$t('account.create_go')"
                type="submit"
                :disable="!ageOk"
              />
            </q-card-actions>
          </q-card>
        </q-intersection>
      </div>
    </q-form>
    <q-dialog v-model="alert">
      <q-card>
        <q-card-section class="bg-green">
          <div class="text-h6">{{ $t('modal.acc_created') }}</div>
        </q-card-section>
        <q-card-section>
          {{ $t('modal.acc_created_txt') }}
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="OK"
            color="primary"
            v-close-popup
            persistent
            @click="toLogin"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { USERSINGUP } from 'src/types/auth';
import { requiredRule } from 'src/rules/form';
import { email, required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useQuasar, QSpinnerOrbit } from 'quasar';
import { useI18n } from 'vue-i18n';
import AUTH_API_IMP from 'src/api/endpoints/auth';
import { useRouter } from 'vue-router';

const $q = useQuasar();
const $r = useRouter();
const { t } = useI18n();
const userData = reactive({} as USERSINGUP);
const repeatPassword = ref('');
const error = ref(false);
const errorMsg = ref('');
const alert = ref(false);
const ageOk = ref(false);
const date = ref(null as string | null);
const dateOfBirth = ref(null as string | null);

const updateProxy = () => {
  dateOfBirth.value = date.value;
};

const save = () => {
  date.value = dateOfBirth.value;
};

const vRules = computed(() => ({
  userData: {
    email: { required, email },
    password: { required },
    identification_number: { required },
    personal_name: { required },
    personal_surname: { required },
    country: { required },
    address: { required },
    phone: { required },
  },
  repeatPassword: { required },
}));
const $v = useVuelidate(vRules, { userData, repeatPassword });

const createUser = async () => {
  $q.loading.show({
    spinner: QSpinnerOrbit,
    spinnerColor: 'primary',
    spinnerSize: 70,
    backgroundColor: 'white',
  });
  $v.value.userData.$touch();
  $v.value.repeatPassword.$touch();
  error.value = false;
  if (!$v.value.userData.$error && !$v.value.repeatPassword.$error) {
    if (userData.password === repeatPassword.value) {
      // Perform request
      let res = await AUTH_API_IMP.createUser(userData);
      if (res.data) {
        // Alert user
        alert.value = true;
      } else {
        // API error
        error.value = true;
        errorMsg.value = t('api.error');
      }
    } else {
      // Passwords don't match!
      error.value = true;
      errorMsg.value = t('account.pwd_error');
    }
  }
  $q.loading.hide();
};
const toLogin = () => {
  $r.push({
    name: 'login',
  });
};
</script>
