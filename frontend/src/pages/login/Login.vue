<template>
    <el-container class="login">
        <el-header></el-header>
        <el-main style="padding: 0;">
            <el-row>
                <el-col>
                    <div>
                        <div class="login-header">
                            <img
                                class="login-logo"
                                src="~@/assets/images/logo.svg"
                                alt="logo"
                            />
                        </div>
                        <form id="submit-form" @keyup.enter="submitForm">
                            <div id="form-content">
                                <div id="form-msg">登录</div>
                                <div id="form-inputs">
                                    <div class="form-input-div">
                                        <el-input
                                            placeholder="请输入账号"
                                            v-model="loginForm.username"
                                            prefix-icon="el-icon-user"
                                            clearable
                                        />
                                        <div
                                            class="err_msg"
                                            id="email_err"
                                            v-text="usernameInvalid"
                                            @mouseover="usernameInvalid = ''"
                                        ></div>
                                    </div>
                                    <div class="form-input-div">
                                        <el-input
                                            placeholder="请输入密码"
                                            v-model="loginForm.password"
                                            prefix-icon="el-icon-lock"
                                            show-password
                                            clearable
                                        />
                                        <div
                                            class="err_msg"
                                            id="pwd_err"
                                            v-text="passwordInvalid"
                                            @mouseover="passwordInvalid = ''"
                                        ></div>
                                    </div>
                                    <div class="form-submit">
                                        <el-button
                                            type="primary"
                                            class="btn btn-primary"
                                            @click="submitForm"
                                            :loading="isLoading"
                                        >
                                            登录
                                        </el-button>
                                    </div>
                                </div>
                                <div class="form-foot">
                                    <span></span>
                                </div>
                            </div>
                        </form>
                    </div>
                </el-col>
            </el-row>
        </el-main>
    </el-container>
</template>

<script>
export default {
    name: "Login",

    data() {
        return {
            isLoading: false,
            loginForm: {
                username: "",
                password: ""
            },
            usernameInvalid: "",
            passwordInvalid: ""
        };
    },

    methods: {
        validateUserName() {
            if (this.loginForm.username.replace(/(^\s*)/g, "") === "") {
                this.usernameInvalid = "用户名不能为空";
                return false;
            }
            return true;
        },
        validatePassword() {
            if (this.loginForm.password.replace(/(^\s*)/g, "") === "") {
                this.passwordInvalid = "密码不能为空";
                return false;
            }
            return true;
        },
        handleLoginSuccess(resp) {
            if (resp.success) {
                this.$router.push({ name: "ProjectList" });
                this.$store.commit("isLogin", resp.token);
                this.$store.commit("setUser", resp.user);
                this.$store.commit("setName", resp.name);
                this.$store.commit("setId", resp.id);
                this.$store.commit("setIsSuperuser", resp.is_superuser);
                this.$store.commit("setRouterName", "ProjectList");
                this.$store.commit("setShowHosts", resp.show_hosts);

                this.setLocalValue("token", resp.token);
                this.setLocalValue("user", resp.user);
                this.setLocalValue("name", resp.name);
                this.setLocalValue("id", resp.id);
                this.setLocalValue("is_superuser", resp.is_superuser);
                this.setLocalValue("routerName", "ProjectList");
                this.setLocalValue("show_hosts", resp.show_hosts);
            } else {
                this.$message.error({
                    message: resp.msg,
                    duration: 2000,
                    center: true
                });
            }
        },
        submitForm() {
            if (this.validateUserName() && this.validatePassword()) {
                this.isLoading = true;
                this.$api.login(this.loginForm).then(resp => {
                    this.handleLoginSuccess(resp);
                    this.isLoading = false;
                });
            }
        }
    }
};
</script>

<style scoped>
.login-header {
    display: -webkit-box;
    align-items: center;
    justify-content: center;
}

.login-logo {
    width: 250px;
    height: 66px;
    vertical-align: top;
}
</style>
