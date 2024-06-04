<template>
  <q-page padding>
    <br />
    <div class="row justify-center items-center"></div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar, QSpinnerOrbit } from 'quasar';
import { authStore } from 'src/stores/auth-store';

const $q = useQuasar();
const $r = useRouter();
const authS = authStore();

const emit = defineEmits<{
  (e: 'clean-data'): void;
}>();

onMounted(async () => {
  $q.loading.show({
    spinner: QSpinnerOrbit,
    spinnerColor: 'primary',
    spinnerSize: 70,
    backgroundColor: 'white',
    message: 'Loggin you out... Bye! Hasta luego! Auf Wiedersehen!',
    messageColor: 'black',
  });
  await new Promise((r) => setTimeout(r, 2000)); // Set a timeout to show the spinner
  document.cookie = 'appforauctionsauth=';
  authS.$reset();
  emit('clean-data');
  $r.push({
    name: 'home',
  });
  $q.loading.hide();
});
</script>
