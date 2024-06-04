<template>
  <q-page padding>
    <q-form greedy @submit.prevent="logInUser">
      <div class="fit row wrap self-center justify-center">
        <q-intersection transition="flip-up" once>
          <q-card
            class="q-pa-sm justify-center items-center content-center animate-pop border-primary"
          >
            <q-item>
              <q-item-section avatar>
                <q-avatar>
                  <img src="~/assets/icon.jpg" />
                </q-avatar>
              </q-item-section>
              <q-item-section class="non-selectable">
                <q-item-label class="text-h5 text-weight-bold">{{
                  $t('account.login')
                }}</q-item-label>
                <q-item-label caption>{{ $t('company') }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-card-section class="q-py-sm q-ma-xs">
              <q-input
                filled
                v-model="user.email"
                :label="$t('account.email')"
                class="q-pa-xs q-my-md"
                :error="$v.user.email.$error"
                :rules="requiredRule"
              ></q-input>
              <q-input
                filled
                v-model="user.password"
                :label="$t('account.password')"
                class="q-pa-xs q-my-md"
                :type="passwordVisible ? 'text' : 'password'"
                :error="$v.user.password.$error"
                :rules="requiredRule"
              >
                <template v-slot:append>
                  <q-icon
                    :name="passwordVisible ? 'visibility' : 'visibility_off'"
                    class="cursor-pointer"
                    @click="passwordVisible = !passwordVisible"
                  ></q-icon>
                </template>
              </q-input>
              <br />
              <p
                class="q-mb-sm text-blue"
                align="right"
                @click="forgotPasswordModal = !forgotPasswordModal"
              >
                Forgot your password?
              </p>
              <q-separator horizontal inset class="q-mx-lg" />
              <q-banner v-if="apiError" class="q-mt-md text-red">
                <template v-slot:avatar>
                  <q-icon name="error" color="red" size="md" />
                </template>
                Invalid credentials
              </q-banner>
              <q-card-actions class="justify-end q-pt-md">
                <q-btn
                  no-caps
                  outline
                  icon="login"
                  class="text-secondary"
                  :label="$t('account.login_short')"
                  type="submit"
                ></q-btn>
              </q-card-actions>
            </q-card-section>
          </q-card>
        </q-intersection>
      </div>
    </q-form>
    <q-dialog v-model="forgotPasswordModal" persistent>
      <q-card v-if="!passwordResetEmailSent">
        <q-card-section>
          <div class="text-h6">Password reset</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          An email will be sent to your email inbox containing a code you will
          have to input.
        </q-card-section>
        <q-card-section>
          <q-input
            filled
            v-model="forgotPasswordEmail"
            :label="$t('account.email')"
            class="q-pa-xs q-my-md"
            :rules="requiredRule"
          ></q-input>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Request token"
            color="primary"
            @click="requestToken"
          />
          <q-btn flat label="Close" color="red" v-close-popup />
        </q-card-actions>
      </q-card>
      <q-card v-else>
        <q-card-section>
          <div class="text-h6">Password reset</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          Please input the received token and your new password. Do not close
          this modal or leave the page.
        </q-card-section>
        <q-card-section>
          <q-input
            filled
            v-model="forgotPasswordToken"
            label="The received token"
            class="q-pa-xs q-my-md"
            :rules="requiredRule"
          ></q-input>
          <q-input
            filled
            v-model="forgotPasswordValue"
            label="Your new password"
            class="q-pa-xs q-my-md"
            :rules="requiredRule"
            type="password"
          ></q-input>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Change passowrd"
            color="primary"
            @click="requestPasswordChange"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { email, required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useQuasar, QSpinnerOrbit } from 'quasar';
import { useI18n } from 'vue-i18n';
import { USERLOGIN } from 'src/types/auth';
import AUTH_API_IMP from 'src/api/endpoints/auth';
import { requiredRule } from 'src/rules/form';
import { SEVERITY } from 'src/types/severity';

const $q = useQuasar();
const $r = useRouter();
const route = useRoute();
const { t } = useI18n();

const emit = defineEmits<{
  (e: 'reload-user-data'): void;
  (e: 'clean-data'): void;
}>();

const user = ref({} as USERLOGIN);
const passwordVisible = ref(false);

const vRules = computed(() => ({
  user: {
    email: { required, email },
    password: { required },
  },
}));
const $v = useVuelidate(vRules, { user });
const apiError = ref(false);
const apiErrorMsg = ref('');
const forgotPasswordModal = ref(false);
const forgotPasswordEmail = ref(null as null | string);
const passwordResetEmailSent = ref(false);
const forgotPasswordToken = ref(null as null | string);
const forgotPasswordValue = ref(null as null | string);

const logInUser = async () => {
  $q.loading.show({
    spinner: QSpinnerOrbit,
    spinnerColor: 'primary',
    spinnerSize: 70,
    backgroundColor: 'white',
  });
  apiError.value = false;
  $v.value.user.$touch();
  if (!$v.value.user.$error) {
    const form_data = new FormData(); // Required by the backend

    form_data.append('username', user.value.email as string); // called as username BUT it's the email!
    form_data.append('password', user.value.password as string);

    const res = await AUTH_API_IMP.login(form_data);
    if (res?.data) {
      // Login successful - Update states
      document.cookie = `appforauctionsauth=${res.data.access_token}; path=/`; // Set the cookie in the browser
      emit('reload-user-data');
      if (route.query.redirect) {
        // Redirect to target location
        $r.replace(route.query.redirect as string);
      } else {
        // Normal redirect
        $r.push({
          name: 'home',
        });
      }
    } else {
      // Login unsuccessful or api error
      if ('statusCode' in res && res.statusCode === 400) {
        // Invalid credentials
        apiErrorMsg.value = t('account.invalid_credentials');
      } else {
        // Any other error
        apiErrorMsg.value = t('api.error');
      }
      apiError.value = true;
    }
  }
  $q.loading.hide();
};
const requestToken = async () => {
  $q.loading.show({
    spinner: QSpinnerOrbit,
    spinnerColor: 'primary',
    spinnerSize: 70,
    backgroundColor: 'white',
  });
  if (forgotPasswordEmail.value !== null && forgotPasswordEmail.value !== '') {
    const res = await AUTH_API_IMP.resetPasswordEmail({
      email: forgotPasswordEmail.value,
    });
    if (res.status === 200) {
      passwordResetEmailSent.value = true; // all ok
    }
  }
  $q.loading.hide();
};
const requestPasswordChange = async () => {
  $q.loading.show({
    spinner: QSpinnerOrbit,
    spinnerColor: 'primary',
    spinnerSize: 70,
    backgroundColor: 'white',
  });
  if (
    forgotPasswordToken.value !== null &&
    forgotPasswordToken.value !== '' &&
    forgotPasswordValue.value !== null &&
    forgotPasswordValue.value !== ''
  ) {
    const res = await AUTH_API_IMP.resetPasswordToken({
      email: forgotPasswordEmail.value,
      token: forgotPasswordToken.value,
      password: forgotPasswordValue.value,
    });
    if (res.status === 200) {
      forgotPasswordModal.value = false;
      $q.notify({
        type: SEVERITY.POSITIVE,
        message: 'Password updated',
        timeout: 2000,
      });
    } else {
      $q.notify({
        type: SEVERITY.NEGATIVE,
        message: 'Something went wrong',
        timeout: 2000,
      });
    }
  }
  $q.loading.hide();
};
onMounted(() => {
  if (route.query.emailUpdate) {
    // If ther user comes from an email update, clear the user data
    emit('clean-data');
  }
});
</script>
