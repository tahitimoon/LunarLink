/* jshint esversion: 6 */
import Vue from "vue";
import Vuex from "vuex";
import state from "./state";
import mutations from "./mutations";
import actions from "@/store/actions";

Vue.use(Vuex);

export default new Vuex.Store({
    state,
    mutations,
    actions
});
