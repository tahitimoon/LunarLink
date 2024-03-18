<template>
    <div class="nav-header">
        <div class="logo-and-title">
            <img
                class="side-logo"
                src="~@/assets/images/side-logo.svg"
                alt="sidebar-logo"
            />
            <span style="color: #D9D9D9; font-size: 23px;">{{
                platformTitle + $store.state.projectName
            }}</span>
        </div>
        <div class="right">
            <div style="float: right; color: #D9D9D9; margin-right: 100px;">
                <i class="el-icon-document"></i>
                <a :href="$store.state.docsURL" class="a-text" target="_blank"
                    >帮助文档
                </a>

                <i class="el-icon-user"></i>
                <span style="font-size: 15px">{{ $store.state.name }}</span>

                <a style="padding-left: 10px;" @click="handleLogOut">注 销</a>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "Header",
    data() {
        return {
            platformTitle: this.$store.state.LunarLink
        };
    },
    methods: {
        handleLogOut() {
            this.$store.commit("isLogin", null);
            this.setLocalValue("token", null);
            this.setLocalValue("is_superuser", false);
            this.setLocalValue("show_hosts", false);
            this.$store.commit("setProjectName", "");
            this.$router.push({ name: "Login" });
        }
    }
};
</script>

<style scoped>
.right {
    position: fixed;
    left: 300px;
    right: 0;
    top: 0;
}

.right div a:hover {
    color: darkcyan;
}

.nav-header {
    position: fixed;
    left: 0;
    right: 0;
    z-index: 100;
    background: #242f42;
    margin: 0 auto;
    font-size: 14px;
    width: 100%;
    height: 49px;
    line-height: 49px;
}

.side-logo {
    width: 36px;
    height: 36px;
    padding-left: 10px;
    vertical-align: top;
}

.logo-and-title {
    display: flex;
    align-items: center;
}

.a-text {
    margin-right: 10px;
    font-size: 15px;
    color: #d9d9d9;
}
</style>
