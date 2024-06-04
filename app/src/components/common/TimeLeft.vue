<template>
  <div class="row full-width self-center justify-center">
    <span v-if="loaded">
      <q-chip
        color="primary"
        text-color="white"
        :label="$t('auction.time_left') + ': '"
        icon="alarm"
        v-if="!hasFinished()"
        class="text-overline"
        size="1em"
      >
        {{ days() + ' ' + $t('auction.time_units.days') + ', ' }}
        {{ hours() + ' ' + $t('auction.time_units.hours') + ', ' }}
        {{ minutes() + ' ' + $t('auction.time_units.minutes') + ', ' }}
        {{ seconds() + ' ' + $t('auction.time_units.seconds') }}
      </q-chip>
      <q-chip color="primary" text-color="white" icon="alarm" v-else>
        {{ $t('auction.finished') }}
      </q-chip>
    </span>
    <span v-else>
      <q-chip
        color="primary"
        text-color="white"
        class="text-overline"
        size="1em"
      >
        {{ $t('auction.calculating_time') }}
      </q-chip>
    </span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { formatDateWSeconds } from 'src/utils/timedates';

interface Props {
  timeLeft: string;
}

const props = defineProps<Props>();

let interval: NodeJS.Timeout;
const currentTime = ref();
const loaded = ref(false);

/*
  See https://stackoverflow.com/questions/19700283/how-to-convert-time-in-milliseconds-to-hours-min-sec-format-in-javascript
  for time unit conversions reference
*/
const msDate = () => {
  return Math.trunc(Date.parse(formatDateWSeconds(props.timeLeft)) / 1000);
};
const msTill = () => {
  // Get the ms left to the desired date
  // This is `ms as end_time` - `ms as now`
  return msDate() - currentTime.value;
};
const seconds = () => {
  // Get the seconds - just remainder of 60
  return msTill() % 60;
};
const minutes = () => {
  // Divide by minutes - 1 minute = 60 seconds
  // Remainder of 60 - 60 seconds in 1 minute
  return Math.trunc(msTill() / 60) % 60;
};
const hours = () => {
  // Divide by hours - 1 hour = 60 minutes
  // Divide by minutes - 1 minute = 60 seconds
  // Remainder of 24 - 24 hours in 1 day
  return Math.trunc(msTill() / 60 / 60) % 24;
};
const days = () => {
  // Divide by seconds - 1 minute = 60 seconds
  // Divide by hours - 1 hour = 60 minutes
  // Divide by days - 1 day = 24 hours
  return Math.trunc(msTill() / 60 / 60 / 24);
};
const hasFinished = () => {
  return msTill() < 0;
};

onMounted(async () => {
  interval = setInterval(() => {
    currentTime.value = Math.trunc(new Date().getTime() / 1000);
  }, 1000);
  // Timeout not to show NaN values to the user
  await new Promise((r) => setTimeout(r, 1000));
  loaded.value = true;
});

onUnmounted(() => {
  clearInterval(interval);
});
</script>
