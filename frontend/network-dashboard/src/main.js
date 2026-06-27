import { createApp } from "vue";
import { createPinia } from "pinia";
import VueApexCharts from "vue3-apexcharts";
import router from "./router";
import "./style.css";
import App from "./App.vue";

const app = createApp(App);
app.use(createPinia());
app.use(VueApexCharts);
app.use(router);
app.mount("#app");
