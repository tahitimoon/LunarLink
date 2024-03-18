<template>
    <el-container>
        <el-container>
            <el-header
                style="padding-top: 10px; margin-left: 10px; height: 50px"
            >
                <div class="env__header">
                    <div class="env__header--item">
                        <el-input
                            style="width: 300px"
                            size="small"
                            placeholder="请输入用户名或IP地址"
                            v-model="search"
                            clearable
                        >
                        </el-input>
                    </div>

                    <div class="env__header--item">
                        <el-button
                            plain
                            size="small"
                            icon="el-icon-refresh"
                            @click="resetSearch"
                            >重置</el-button
                        >
                    </div>
                </div>
            </el-header>

            <el-dialog
                title="详情"
                width="35%"
                :close-on-click-modal="false"
                :visible.sync="dialogVisible"
                :style="{ 'text-align': 'center' }"
            >
                <el-form
                    :inline="true"
                    label-position="right"
                    :model="loginLogForm"
                    label-width="80px"
                >
                    <el-form-item label="登录用户" prop="username">
                        <el-input
                            readonly
                            v-model="loginLogForm.username"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="ID" prop="id">
                        <el-input readonly v-model="loginLogForm.id"></el-input>
                    </el-form-item>

                    <el-form-item label="姓名" prop="name">
                        <el-input
                            readonly
                            v-model="loginLogForm.name"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="IP" prop="ip">
                        <el-input readonly v-model="loginLogForm.ip"></el-input>
                    </el-form-item>

                    <el-form-item label="agent信息" prop="agent">
                        <el-input
                            readonly
                            v-model="loginLogForm.agent"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="操作系统" prop="os">
                        <el-input readonly v-model="loginLogForm.os"></el-input>
                    </el-form-item>

                    <el-form-item label="浏览器" prop="browser">
                        <el-input
                            readonly
                            v-model="loginLogForm.browser"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="洲" prop="continent">
                        <el-input
                            readonly
                            v-model="loginLogForm.continent"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="国家" prop="country">
                        <el-input
                            readonly
                            v-model="loginLogForm.country"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="省份" prop="province">
                        <el-input
                            readonly
                            v-model="loginLogForm.province"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="城市" prop="city">
                        <el-input
                            readonly
                            v-model="loginLogForm.city"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="县/区" prop="district">
                        <el-input
                            readonly
                            v-model="loginLogForm.district"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="运营商" prop="isp">
                        <el-input
                            readonly
                            v-model="loginLogForm.isp"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="区域代码" prop="area_code">
                        <el-input
                            readonly
                            v-model="loginLogForm.area_code"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="英文全称" prop="country_english">
                        <el-input
                            readonly
                            v-model="loginLogForm.country_english"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="国家代码" prop="country_code">
                        <el-input
                            readonly
                            v-model="loginLogForm.country_code"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="经度" prop="longitude">
                        <el-input
                            readonly
                            v-model="loginLogForm.longitude"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="纬度" prop="latitude">
                        <el-input
                            readonly
                            v-model="loginLogForm.latitude"
                        ></el-input>
                    </el-form-item>
                </el-form>
            </el-dialog>

            <el-container>
                <el-main style="margin-left: 10px; margin-top: 10px">
                    <div class="log-body-table">
                        <el-table
                            highlight-current-row
                            stripe
                            :data="loginLogData.results"
                            v-loading="isLoading"
                            height="calc(100%)"
                            @cell-mouse-enter="cellMouseEnter"
                            @cell-mouse-leave="cellMouseLeave"
                        >
                            <el-table-column label="用户" width="100">
                                <template slot-scope="scope">
                                    <div
                                        :title="scope.row.name"
                                        class="table-column"
                                    >
                                        {{ scope.row.name }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="IP" width="150">
                                <template slot-scope="scope">
                                    <div
                                        :title="scope.row.ip"
                                        class="table-column"
                                    >
                                        {{ scope.row.ip }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作系统" width="150">
                                <template slot-scope="scope">
                                    <div
                                        :title="scope.row.os"
                                        class="table-column"
                                    >
                                        {{ scope.row.os }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="浏览器" width="150">
                                <template slot-scope="scope">
                                    <div
                                        :title="scope.row.browser"
                                        class="table-column"
                                    >
                                        {{ scope.row.browser }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="国家" width="120">
                                <template slot-scope="scope">
                                    <div
                                        :title="scope.row.country"
                                        class="table-column"
                                    >
                                        {{ scope.row.country }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="省份" width="120">
                                <template slot-scope="scope">
                                    <div
                                        :title="scope.row.province"
                                        class="table-column"
                                    >
                                        {{ scope.row.province }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="城市" width="120">
                                <template slot-scope="scope">
                                    <div
                                        :title="scope.row.city"
                                        class="table-column"
                                    >
                                        {{ scope.row.city }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="县/区" width="120">
                                <template slot-scope="scope">
                                    <div
                                        :title="scope.row.district"
                                        class="table-column"
                                    >
                                        {{ scope.row.district }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="运营商" width="120">
                                <template slot-scope="scope">
                                    <div
                                        :title="scope.row.isp"
                                        class="table-column"
                                    >
                                        {{ scope.row.isp }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="登录时间" width="180">
                                <template slot-scope="scope">
                                    <div>
                                        {{
                                            scope.row.create_time
                                                | datetimeFormat
                                        }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作">
                                <template slot-scope="scope">
                                    <el-row v-show="currentRow === scope.row">
                                        <el-button
                                            type="success"
                                            icon="el-icon-view"
                                            title="查看"
                                            circle
                                            size="mini"
                                            @click="
                                                handleEditVariables(scope.row)
                                            "
                                        ></el-button>
                                    </el-row>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="pagination-container">
                            <el-pagination
                                v-show="loginLogData.count !== 0"
                                background
                                @current-change="handleCurrentChange"
                                @size-change="handleSizeChange"
                                :current-page.sync="currentPage"
                                :page-sizes="[10, 20, 30, 40]"
                                :page-size="pageSize"
                                :pager-count="5"
                                layout="total, sizes, prev, pager, next, jumper"
                                :total="loginLogData.count"
                            ></el-pagination>
                        </div>
                    </div>
                </el-main>
            </el-container>
        </el-container>
    </el-container>
</template>

<script>
export default {
    name: "LoginLog",
    data() {
        return {
            search: "",
            currentRow: "",
            currentPage: 1,
            pageSize: 10,
            loginLogData: {
                count: 0,
                results: []
            },
            dialogVisible: false,
            isLoading: true,
            searchDebounce: null,
            loginLogForm: {
                id: "",
                username: "",
                name: "",
                ip: "",
                agent: "",
                os: "",
                browser: "",
                continent: "",
                country: "",
                province: "",
                city: "",
                district: "",
                isp: "",
                area_code: "",
                country_english: "",
                country_code: "",
                longitude: "",
                latitude: ""
            }
        };
    },
    methods: {
        debouncedGetLogList() {
            clearTimeout(this.searchDebounce);
            this.searchDebounce = setTimeout(() => {
                this.currentPage = 1;
                this.getLoginLogList();
            }, 300);
        },
        cellMouseEnter(row) {
            this.currentRow = row;
        },
        cellMouseLeave() {
            this.currentRow = "";
        },
        handleEditVariables(row) {
            this.dialogVisible = true;
            this.loginLogForm.username = row["username"];
            this.loginLogForm.id = row["id"];
            this.loginLogForm.name = row["name"];
            this.loginLogForm.ip = row["ip"];
            this.loginLogForm.agent = row["agent"];
            this.loginLogForm.os = row["os"];
            this.loginLogForm.browser = row["browser"];
            this.loginLogForm.continent = row["continent"];
            this.loginLogForm.country = row["country"];
            this.loginLogForm.province = row["province"];
            this.loginLogForm.city = row["city"];
            this.loginLogForm.district = row["district"];
            this.loginLogForm.isp = row["isp"];
            this.loginLogForm.area_code = row["area_code"];
            this.loginLogForm.country_english = row["country_english"];
            this.loginLogForm.country_code = row["country_code"];
            this.loginLogForm.longitude = row["longitude"];
            this.loginLogForm.latitude = row["latitude"];
        },
        handleCurrentChange() {
            this.$api
                .loginLogPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: this.pageSize,
                        search: this.search
                    }
                })
                .then(resp => {
                    this.loginLogData = resp;
                });
        },
        handleSizeChange(newSize) {
            this.pageSize = newSize;
            // 计算新的最大页码
            let maxPage = Math.ceil(this.loginLogData.count / newSize);
            if (this.currentPage > maxPage) {
                // 如果当前页码超出了范围，请将其设置为最大页面
                this.currentPage = maxPage;
            }
            this.$api
                .loginLogPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: newSize,
                        search: this.search
                    }
                })
                .then(resp => {
                    this.loginLogData = resp;
                });
        },
        getLoginLogList() {
            this.$api
                .loginLogList({
                    params: {
                        page: this.currentPage,
                        size: this.pageSize,
                        search: this.search
                    }
                })
                .then(resp => {
                    this.loginLogData = resp;
                    this.isLoading = false;
                });
        },
        resetSearch() {
            this.currentPage = 1;
            this.pageSize = 10;
            this.search = "";
            this.getLoginLogList();
        }
    },
    watch: {
        search() {
            this.debouncedGetLogList();
        }
    },
    mounted() {
        this.getLoginLogList();
    }
};
</script>

<style scoped>
.env__header {
    display: flex;
    align-items: center;
    margin-left: -30px;
}

.env__header--item {
    display: flex;
    margin-left: 10px;
}

.table-column {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.log-body-table {
    position: fixed;
    bottom: 0;
    right: 0;
    left: 220px;
    top: 100px;
    margin-left: -10px;
    padding-bottom: 60px;
}
</style>
