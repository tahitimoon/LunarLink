// 用于修改state对象中的数据状态
export default {
    isLogin(state, value) {
        state.token = value;
    },

    setUser(state, value) {
        state.user = value;
    },

    setName(state, value) {
        state.name = value;
    },

    setId(state, value) {
        state.id = value;
    },

    setRouterName(state, value) {
        state.routerName = value;
    },

    setProjectName(state, value) {
        if (value !== "") {
            value = " / " + value.replaceAll("/", "").replaceAll(" ", "");
        }
        state.projectName = value;
    },

    setIsSuperuser(state, value) {
        state.is_superuser = value;
    },

    setShowHosts(state, value) {
        state.show_hosts = value;
    }
};
