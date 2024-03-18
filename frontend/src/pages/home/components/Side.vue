<template>
    <el-menu
        class="common-side-bar"
        :default-active="$store.state.routerName"
        background-color="#304056"
        text-color="#BFCBD9"
        active-text-color="#318DF1"
        @select="select"
    >
        <el-menu-item index="ProjectList">
            <i class="iconfont">&#xe631;</i>&nbsp;&nbsp;首 页
        </el-menu-item>

        <template v-for="item of side_menu">
            <el-menu-item
                v-if="!item.children"
                :key="item.url"
                :index="item.url"
                :disabled="$store.state.routerName === 'ProjectList'"
            >
                <span class="iconfont" v-html="item.code"></span>&nbsp;&nbsp;{{
                    item.name
                }}
            </el-menu-item>

            <el-submenu
                v-if="item.children"
                :key="item.url"
                :index="item.url"
                :disabled="$store.state.routerName === 'ProjectList'"
            >
                <template slot="title">
                    <span class="iconfont" v-html="item.code"></span
                    >&nbsp;&nbsp;{{ item.name }}
                </template>
                <el-menu-item
                    v-for="subItem in item.children"
                    :key="subItem.url"
                    :index="subItem.url"
                >
                    {{ subItem.name }}
                </el-menu-item>
            </el-submenu>
        </template>
    </el-menu>
</template>

<script>
export default {
    name: "Side",
    data() {
        return {
            side_menu: [
                { name: "项目概况", url: "ProjectDetail", code: "&#xe64a;" },
                { name: "接口管理", url: "RecordApi", code: "&#xe74a;" },
                {
                    name: "测试用例",
                    url: "TestCase",
                    code: "&#xe6da;",
                    children: [
                        { name: "添加用例", url: "AutoTest" },
                        { name: "录制用例", url: "RecordCase" }
                    ]
                },
                { name: "配置管理", url: "RecordConfig", code: "&#xee32;" },
                { name: "全局变量", url: "GlobalEnv", code: "&#xe692;" },
                { name: "驱动代码", url: "DebugTalk", code: "&#xe7ca;" },
                { name: "定时任务", url: "Tasks", code: "&#xe61e;" },
                { name: "测试报告", url: "Reports", code: "&#xe66e;" },
                {
                    name: "日志管理",
                    url: "Logging",
                    code: "&#59266;",
                    children: [{ name: "登录日志", url: "LoginLog" }]
                }
            ]
        };
    },
    methods: {
        select(url) {
            this.$store.commit("setRouterName", url);
            this.$router.push({ name: url }).catch(err => {
                // 忽略NavigationDuplicated错误
                if (err.name !== "NavigationDuplicated") {
                    // 如果错误不是NavigationDuplicated，则继续抛出错误
                    throw err;
                }
            });
            this.setLocalValue("routerName", url);
            let projectName = "";
            if (url !== "ProjectList") {
                projectName = this.$store.state.projectName;
            }
            this.$store.commit("setProjectName", projectName);
        }
    },
    mounted() {
        if (this.$store.state.show_hosts) {
            this.side_menu.splice(5, 0, {
                name: "Hosts管理",
                url: "HostIP",
                code: "&#xe609;"
            });
        }
    }
};
</script>

<style scoped>
.common-side-bar {
    position: fixed;
    top: 48px;
    border-right: 1px solid #ddd;
    height: 100%;
    width: 202px;
    background-color: #fff;
    display: inline-block;
}
</style>
