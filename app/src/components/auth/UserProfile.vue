<template>
  <div class="justify-center row">
    <q-card class="q-pa-sm col-9">
      <q-card-section class="row">
        <div class="row col-1 justify-center items-center content-center">
          <q-icon name="face" size="3em" />
        </div>
        <div class="col-10 q-ml-sm">
          <div class="row text-h5">
            Hi, {{ authS.personal_name + ' ' + authS.personal_surname }}
          </div>
          <div class="row text-subtitle1">Welcome back to your profile</div>
        </div>
      </q-card-section>
      <q-separator class="q-mx-sm" />
      <div class="row">
        <q-input
          v-model="newUserData.personal_name"
          :label="$t('account.name')"
          class="q-pa-xs col-6"
        >
          <template v-slot:prepend>
            <q-icon name="badge" />
          </template>
        </q-input>
        <q-input
          v-model="newUserData.personal_surname"
          :label="$t('account.surname')"
          class="q-pa-xs col-6"
        >
          <template v-slot:prepend>
            <q-icon name="badge" />
          </template>
        </q-input>
      </div>
      <div class="row">
        <q-input
          v-model="authS.email"
          :label="$t('account.email')"
          class="q-pa-xs col-12"
          disable
        >
          <template v-slot:prepend>
            <q-icon name="email" />
          </template>
        </q-input>
      </div>
      <div class="row">
        <q-input
          v-model="newUserData.address"
          :label="$t('account.address')"
          class="q-pa-xs col-8"
        />
        <q-input
          v-model="newUserData.country"
          :label="$t('account.country')"
          class="q-pa-xs col-4"
        />
      </div>
      <div class="row">
        <q-input
          v-model="newUserData.phone"
          :label="$t('account.phone')"
          class="q-pa-xs col-6"
        />
        <q-input
          v-model="newUserData.identification_number"
          :label="$t('account.id_num')"
          class="q-pa-xs col-6"
        />
      </div>
      <div class="text-overline q-mt-md">
        <q-icon name="verified" color="light-green-7" size="2em" />
        Member since:
        {{ new Date(authS.member_since as string).toLocaleString('es-ES') }}
      </div>
      <q-card-actions align="right">
        <q-btn
          color="primary"
          :label="$t('account.update_btn')"
          @click="updateUserData"
          :loading="loading"
          no-caps
        />
      </q-card-actions>
      <q-separator />
      <q-expansion-item
        v-model="expanded"
        icon="settings"
        label="Extra settings"
        header-class="bg-accent text-white"
        expand-icon-class="text-white"
        class="q-my-sm"
      >
        <div class="row justify-center text-blue q-my-sm q-ma-sm">
          <q-btn
            label="Change email"
            @click="dialogEmailChange = !dialogEmailChange"
            unelevated
            no-caps
            outline
            class="q-mx-sm"
          />
          <q-btn
            label="Change password"
            @click="dialogPwdChange = !dialogPwdChange"
            unelevated
            no-caps
            outline
          />
        </div>
      </q-expansion-item>
    </q-card>
    <q-dialog
      v-model="dialogEmailChange"
      persistent
      transition-show="scale"
      transition-hide="scale"
    >
      <q-card style="width: 500px">
        <q-card-section class="row bg-accent text-white">
          <div class="row col-1 justify-center items-center content-center">
            <q-icon name="lock" size="2.5em" />
          </div>
          <div class="col-10 q-ml-sm">
            <div class="row text-h5">Change your email</div>
            <div class="row text-caption">
              You will be asked to login again after the change!
            </div>
          </div>
        </q-card-section>
        <q-card-section>
          <div class="row">
            <q-input
              v-model="newEmail.new_email"
              :label="$t('account.email')"
              class="q-pa-xs col-12"
              type="email"
              :rules="requiredRule"
              :error="$v.newEmail.new_email.$error"
            >
              <template v-slot:prepend>
                <q-icon name="email" />
              </template>
            </q-input>
          </div>
        </q-card-section>
        <q-card-actions align="right" class="bg-white text-primary q-mx-sm">
          <q-btn
            label="Cancel"
            color="red"
            :disable="loading"
            v-close-popup
            no-caps
            outline
            @click="clearEmailData()"
          />
          <q-btn
            label="Update email"
            :loading="loading"
            no-caps
            outline
            @click="updateEmail()"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <q-dialog
      v-model="dialogPwdChange"
      persistent
      transition-show="scale"
      transition-hide="scale"
    >
      <q-card style="width: 500px">
        <q-card-section class="row bg-accent text-white">
          <div class="row col-1 justify-center items-center content-center">
            <q-icon name="lock" size="2.5em" />
          </div>
          <div class="col-10 q-ml-sm">
            <div class="row text-h5">Change your password</div>
          </div>
        </q-card-section>
        <q-card-section>
          <div class="row">
            <q-input
              v-model="newPwd.old_pwd"
              :label="$t('account.old_password')"
              class="q-pa-xs col-12"
              type="password"
              :rules="requiredRule"
              :error="$v.newPwd.old_pwd.$error"
            >
              <template v-slot:prepend>
                <q-icon name="password" />
              </template>
            </q-input>
          </div>
          <div class="row">
            <q-input
              v-model="newPwd.new_pwd"
              :label="$t('account.new_password')"
              class="q-pa-xs col-12"
              type="password"
              :rules="requiredRule"
              :error="$v.newPwd.new_pwd.$error"
            >
              <template v-slot:prepend>
                <q-icon name="password" />
              </template>
            </q-input>
          </div>
          <div class="row">
            <q-input
              v-model="newPwd.new_pwd_repeated"
              :label="$t('account.repeat_new_password')"
              class="q-pa-xs col-12"
              type="password"
              :rules="requiredRule"
              :error="$v.newPwd.new_pwd_repeated.$error"
            >
              <template v-slot:prepend>
                <q-icon name="password" />
              </template>
            </q-input>
          </div>
        </q-card-section>
        <q-card-actions align="right" class="bg-white text-primary q-mx-sm">
          <q-btn
            label="Cancel"
            color="red"
            :disable="loading"
            v-close-popup
            no-caps
            outline
            @click="clearPasswordData()"
          />
          <q-btn
            label="Update password"
            :loading="loading"
            no-caps
            outline
            @click="updateUserPassword()"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { useQuasar } from 'quasar';
import { useI18n } from 'vue-i18n';
import { authStore } from 'src/stores/auth-store';
import AUTH_API_IMP from 'src/api/endpoints/auth';
import { USERPROFILE, PASSWORDCHANGE, EMAILCHANGE } from 'src/types/auth';
import { SEVERITY } from 'src/types/severity';
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import { requiredRule } from 'src/rules/form';
import { useRouter } from 'vue-router';

const $q = useQuasar();
const $r = useRouter();
const { t } = useI18n();
const authS = authStore();

const expanded = ref(false);
const loading = ref(false);
const newUserData = reactive({} as USERPROFILE);
const newPwd = reactive({} as PASSWORDCHANGE);
const dialogPwdChange = ref(false);
const newEmail = reactive({} as EMAILCHANGE);
const dialogEmailChange = ref(false);

const vRules = computed(() => ({
  newEmail: {
    new_email: { required },
  },
  newPwd: {
    old_pwd: { required },
    new_pwd: { required },
    new_pwd_repeated: { required },
  },
}));
const $v = useVuelidate(vRules, { newEmail, newPwd });

const updateUserData = async () => {
  loading.value = true;
  const res = await AUTH_API_IMP.updateUser(authS.email as string, newUserData);
  if (res.data) {
    notifyAction(t('account.update_ok'), SEVERITY.POSITIVE);
    authS.refreshData();
  } else {
    notifyAction(t('account.update_failed'), SEVERITY.NEGATIVE);
  }
  loading.value = false;
};
const updateUserPassword = async () => {
  loading.value = true;
  $v.value.newPwd.$touch();
  if (!$v.value.$error) {
    const res = await AUTH_API_IMP.updateUserPassword(newPwd);
    if (res.data) {
      notifyAction(t('account.update_ok'), SEVERITY.POSITIVE);
    } else {
      notifyAction(t('account.update_failed'), SEVERITY.NEGATIVE);
    }
  }
  loading.value = false;
};
const clearPasswordData = () => {
  newPwd.new_pwd = null;
  newPwd.new_pwd_repeated = null;
  newPwd.old_pwd = null;
};
const updateEmail = async () => {
  loading.value = true;
  $v.value.newEmail.$touch();
  if (!$v.value.$error) {
    newEmail.old_email = authS.email;
    const res = await AUTH_API_IMP.updateUserEmail(newEmail);
    if (res.data) {
      notifyAction(t('account.update_ok'), SEVERITY.POSITIVE);
      $r.push({ name: 'login', query: { emailUpdate: 't' } });
    } else {
      notifyAction(t('account.update_failed'), SEVERITY.NEGATIVE);
    }
  }
  loading.value = false;
};
const clearEmailData = () => {
  newEmail.new_email = null;
};

const notifyAction = (msg: string, col: string) => {
  $q.notify({
    type: col,
    message: msg,
    timeout: 2000,
  });
};

onMounted(() => {
  newUserData.identification_number = authS.identification_number;
  newUserData.personal_name = authS.personal_name;
  newUserData.personal_surname = authS.personal_surname;
  newUserData.country = authS.country;
  newUserData.address = authS.address;
  newUserData.phone = authS.phone;
});
</script>
