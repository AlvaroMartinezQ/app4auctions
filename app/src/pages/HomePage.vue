<template>
  <q-page padding>
    <q-intersection
      transition="slide-up"
      transition-duration="1200"
      once
      class="q-mb-xl"
    >
      <div
        class="row full-width self-center justify-center text-h3 richland q-mt-md"
      >
        App4Auctions
      </div>
      <div
        class="row full-width self-center justify-center text-h5 q-my-lg richland"
      >
        <img :src="logoImage" spinner-color="white" />
      </div>
      <div
        class="row full-width self-center justify-center text-h5 q-my-lg richland"
      >
        Sell and buy online
      </div>
    </q-intersection>
    <q-intersection transition="fade" transition-duration="1000" once>
      <div class="row self-center justify-center q-mt-md">
        <q-card class="col-4 q-mx-md" bordered>
          <q-card-section class="row self-center justify-center">
            <q-icon name="shopping_cart" size="3em" color="primary"></q-icon>
          </q-card-section>
          <q-card-section class="row self-center justify-center">
            Sell objects you do not want any longer with 3 simple clicks.
          </q-card-section>
          <q-card-actions
            class="row self-center justify-center text-caption items-end"
          >
            <q-btn
              outline
              color="primary"
              label="Create new auction"
              no-caps
              :to="{ name: 'auction_new' }"
            />
          </q-card-actions>
          <q-separator size="4px" color="primary" class="q-ma-md" />
          <q-card-section class="row self-center justify-center text-caption">
            Create your account and start creating auctions. All users of the
            web will be able to bid on your auctions!
          </q-card-section>
        </q-card>
        <q-card class="col-4 q-mx-md" bordered>
          <q-card-section class="row self-center justify-center">
            <q-icon name="storefront" size="3em" color="primary"></q-icon>
          </q-card-section>
          <q-card-section class="row self-center justify-center">
            You can buy anything for all sellers of the e-commerce web!
          </q-card-section>
          <q-card-actions class="row self-center justify-center text-caption">
            <q-btn
              outline
              color="primary"
              label="View market"
              no-caps
              :to="{ name: 'market' }"
            />
          </q-card-actions>
          <q-separator size="4px" color="primary" class="q-ma-md" />
          <q-card-section class="row self-center justify-center text-caption">
            Create your account and start bidding on your desired objects. When
            you win an auction you will be notified with the seller info so you
            can get in contact with them.
          </q-card-section>
        </q-card>
      </div>
      <div class="row self-center justify-center q-my-md">
        <q-card class="col-3 q-mx-md">
          <q-card-section class="row self-center justify-center">
            <q-icon name="person_add" size="3em" color="primary"></q-icon>
          </q-card-section>
          <q-card-actions class="row self-center justify-center text-caption">
            <q-btn
              outline
              color="primary"
              label="Create your account"
              no-caps
              :to="{ name: 'new_account' }"
            />
          </q-card-actions>
        </q-card>
      </div>
    </q-intersection>
  </q-page>
</template>

<script setup lang="ts">
import logoImage from 'src/assets/app-logo-mini.png';
</script>
