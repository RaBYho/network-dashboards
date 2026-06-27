import { createRouter, createWebHistory } from "vue-router";

import VueGlobale from "../pages/VueGlobale.vue";
import Debit from "../pages/Debit.vue";
import Latence from "../pages/Latence.vue";
import Erreurs from "../pages/Erreurs.vue";
import Interface from "../pages/Interface.vue";
import Parametres from "../pages/Parametres.vue";

const routes = [
  { path: "/", component: VueGlobale },
  { path: "/debit", component: Debit },
  { path: "/latence", component: Latence },
  { path: "/erreurs", component: Erreurs },
  { path: "/interface/:name", component: Interface }, // :name = eth0 ou wlan0
  { path: "/parametres", component: Parametres },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
