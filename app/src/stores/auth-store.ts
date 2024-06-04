import { defineStore } from 'pinia';
import { getCookie } from 'src/api/client.api';
import AUTH_API_IMP from 'src/api/endpoints/auth';

export const authStore = defineStore({
  id: 'authStore',
  state: () => ({
    id: null as string | null,
    email: null as string | null,
    personal_name: null as string | null,
    personal_surname: null as string | null,
    n_auctions: null as number | null,
    n_bids: null as number | null,
    logged: false as boolean,
    member_since: null as null | string,
    address: null as null | string,
    phone: null as null | string,
    identification_number: null as null | string,
    country: null as string | null
  }),
  getters: {
    getEmail: (state) => state.email,
  },
  actions: {
    setData(
      id: string,
      email: string,
      p_name: string,
      p_surname: string,
      n_auctions: number,
      n_bids: number,
      member_since: string,
      address: string,
      phone: string,
      identification_number: string,
      country: string
    ) {
      this.id = id;
      this.email = email;
      this.personal_name = p_name;
      this.personal_surname = p_surname;
      this.n_auctions = n_auctions;
      this.n_bids = n_bids;
      this.logged = true;
      this.member_since = member_since;
      this.address = address;
      this.phone = phone;
      this.identification_number = identification_number;
      this.country = country;
    },
    async validCredentials() {
      if (
        getCookie('appforauctionsauth') !== null &&
        getCookie('appforauctionsauth') !== ''
      ) {
        const res = await AUTH_API_IMP.getUserData()
        if (res.data)
          return true
        else
          return false
      }
    },
    async refreshData() {
      const res = await AUTH_API_IMP.getUserData();
      if (res.data) {
        this.setData(
          res.data.id,
          res.data.email,
          res.data.personal_name,
          res.data.personal_surname,
          res.data.n_auctions,
          res.data.n_bids,
          res.data.singup_date,
          res.data.address,
          res.data.phone,
          res.data.identification_number,
          res.data.country
        );
      }
    }
  }
})
