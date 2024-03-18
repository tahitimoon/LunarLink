/* jshint esversion: 6 */
import Vue from "vue";
import ElementUI from "element-ui";
import VJsoneditor from "v-jsoneditor";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import VueApexCharts from "vue-apexcharts";
import Skeleton from "vue-loading-skeleton";
import VueClipboard from "vue-clipboard2";
import "element-ui/lib/theme-chalk/index.css";
import "styles/iconfont.css";
import "styles/swagger.css";
import "styles/tree.css";
import "styles/home.css";
import "styles/reports.css";
import "styles/iconfont.js";
import * as api from "./restful/api";
import { datetimeObj2str, timestamp2time } from "@/util/format";

Vue.use(ElementUI);
Vue.use(VueApexCharts);
Vue.use(VJsoneditor);
Vue.use(Skeleton);
Vue.use(VueClipboard);

Vue.component("ApexCharts", VueApexCharts);

Vue.config.productionTip = false;
Vue.prototype.$api = api;

Vue.filter("datetimeFormat", datetimeObj2str);
Vue.filter("timestampToTime", timestamp2time);

Vue.prototype.setLocalValue = function(name, value) {
    if (window.localStorage) {
        localStorage.setItem(name, value);
    } else {
        alert("This browser does not support localStorage");
    }
};

Vue.prototype.getLocalValue = function(name) {
    const value = localStorage.getItem(name);
    if (value) {
        // localStorage只能存字符串，布尔类型需要转换
        if (value === "false" || value === "true") {
            return eval(value);
        }
        return value;
    } else {
        return "";
    }
};

router.beforeEach((to, from, next) => {
    setTimeout(() => {
        // 修改页面title
        if (to.meta.title) {
            document.title = to.meta.title;
        }

        // 鉴权
        if (to.meta.requireAuth) {
            if (store.state.token !== "") {
                next();
            } else {
                next({
                    name: "Login"
                });
            }
        } else {
            next();
        }
    });
});

new Vue({
    el: "#app",
    router,
    store,
    components: { App },
    template: "<App/>",
    created() {
        if (this.getLocalValue("token") === null) {
            this.setLocalValue("token", "");
        }

        if (this.getLocalValue("user") === null) {
            this.setLocalValue("user", "");
        }

        if (this.getLocalValue("name") === null) {
            this.setLocalValue("name", "");
        }

        if (this.getLocalValue("id") === null) {
            this.setLocalValue("id", "");
        }

        if (this.getLocalValue("routerName") === null) {
            this.setLocalValue("routerName", "ProjectList");
        }

        if (this.getLocalValue("is_superuser") === null) {
            this.setLocalValue("is_superuser", false);
        }

        if (this.getLocalValue("show_hosts") === null) {
            this.setLocalValue("show_hosts", false);
        }

        this.$store.commit("isLogin", this.getLocalValue("token"));
        this.$store.commit("setUser", this.getLocalValue("user"));
        this.$store.commit("setName", this.getLocalValue("name"));
        this.$store.commit("setId", parseInt(this.getLocalValue("id"), 10));
        this.$store.commit("setRouterName", this.getLocalValue("routerName"));
        this.$store.commit(
            "setIsSuperuser",
            this.getLocalValue("is_superuser")
        );
        this.$store.commit("setShowHosts", this.getLocalValue("show_hosts"));
        this.$store.dispatch("initStore").then(() => {});
    }
});
