import { route } from 'quasar/wrappers';
import { authStore } from 'src/stores/auth-store';
import {
  // createMemoryHistory,
  createRouter,
  // createWebHashHistory,
  createWebHistory,
} from 'vue-router';

import routes from './routes';

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route(function (/* { store, ssrContext } */) {
  const createHistory = createWebHistory;
  /*
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory);
  */

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  Router.beforeEach(async (to, /*from*/) => {
    const authS = authStore();
    if (to.meta.requiresAuth) {
      if (!await authS.validCredentials()) {
        if (to.fullPath === '/logout') {
          return {
            path: ''
          }
        }
        return {
          path: '/login',
          query: { redirect: to.fullPath }
        }
      }
    }
  })

  return Router;
});
