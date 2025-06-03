<template>
    <el-container>
        <el-header style="padding-top: 10px; height: 50px">
            <div class="config__header">
                <div class="config__header--item">
                    <el-input
                        style="width: 300px"
                        size="small"
                        placeholder="请输入配置名称"
                        v-model="search"
                        clearable
                    >
                    </el-input>
                </div>

                <div class="config__header--item">
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

        <el-container>
            <el-main style="padding: 0; margin-left: 10px; margin-top: 10px;">
                <div class="config-body-table">
                    <el-table
                        highlight-current-row
                        v-loading="loading"
                        :data="configData.results"
                        stripe
                        height="calc(100%)"
                        @cell-mouse-enter="cellMouseEnter"
                        @cell-mouse-leave="cellMouseLeave"
                        @selection-change="handleSelectionChange"
                    >
                        <el-table-column
                            type="selection"
                            width="55"
                        ></el-table-column>
                        <el-table-column label="配置名称" width="300">
                            <template v-slot="scope">
                                <div
                                    :title="scope.row.name"
                                    style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                                >
                                    {{ scope.row.name }}
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column label="基础URL">
                            <template v-slot="scope">
                                <div
                                    :title="scope.row.base_url"
                                    style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                                >
                                    {{
                                        scope.row.base_url === ""
                                            ? "无"
                                            : scope.row.base_url
                                    }}
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column label="是否默认">
                            <template v-slot="scope">
                                <el-switch
                                    disabled
                                    v-model="scope.row.is_default"
                                    active-color="#13ce66"
                                ></el-switch>
                            </template>
                        </el-table-column>

                        <el-table-column label="更新时间">
                            <template v-slot="scope">
                                <div>
                                    {{ scope.row.update_time | datetimeFormat }}
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column label="配置操作">
                            <template v-slot="scope">
                                <el-row v-show="currentRow === scope.row">
                                    <el-button
                                        type="info"
                                        icon="el-icon-edit"
                                        title="编辑"
                                        circle
                                        size="mini"
                                        @click="handleEditConfig(scope.row)"
                                    ></el-button>
                                    <el-button
                                        type="success"
                                        icon="el-icon-document"
                                        title="复制"
                                        circle
                                        size="mini"
                                        @click="
                                            handleCopyConfig(
                                                scope.row.id,
                                                scope.row.name
                                            )
                                        "
                                    ></el-button>
                                    <el-button
                                        v-show="configData.count !== 0"
                                        type="danger"
                                        icon="el-icon-delete"
                                        title="删除"
                                        circle
                                        size="mini"
                                        @click="handleDelConfig(scope.row.id)"
                                    ></el-button>
                                </el-row>
                            </template>
                        </el-table-column>
                    </el-table>
                    <div class="pagination-container">
                        <el-pagination
                            v-show="configData.count !== 0"
                            @current-change="handleCurrentChange"
                            @size-change="handleSizeChange"
                            :current-page.sync="localCurrentPage"
                            :page-sizes="[10, 20, 30, 40]"
                            :page-size="localPageSize"
                            :pager-count="5"
                            layout="total, sizes, prev, pager, next, jumper"
                            :total="configData.count"
                            background
                        ></el-pagination>
                    </div>
                </div>
            </el-main>
        </el-container>
    </el-container>
</template>

<script>
export default {
    name: "ConfigList",
    props: {
        back: Boolean,
        project: {
            required: true
        },
        pageSize: Number,
        currentPage: Number,
        del: Boolean,
        isSelectConfig: Boolean
    },
    data() {
        return {
            localCurrentPage: this.currentPage || 1,
            localPageSize: this.pageSize || 10,
            search: "",
            searchDebounce: null,
            selectConfig: [],
            currentRow: "",
            configData: {
                count: 0,
                results: []
            },
            loading: true
        };
    },
    watch: {
        currentPage(newValue) {
            this.localCurrentPage = newValue;
        },
        pageSize(newValue) {
            this.localPageSize = newValue;
        },
        search() {
            this.debouncedGetConfigList();
        },
        configData(newValue) {
            this.$emit("configDataChanged", newValue);
        },
        back() {
            this.getConfigList();
        },
        del() {
            if (this.selectConfig.length !== 0) {
                this.$confirm("此操作将永久删除配置，是否继续?", "提示", {
                    confirmButtonText: "确定",
                    cancelButtonText: "取消",
                    type: "warning"
                }).then(() => {
                    this.$api
                        .delAllConfig({ data: this.selectConfig })
                        .then(resp => {
                            if (resp.success) {
                                this.$message.success(resp.msg);
                                this.getConfigList();
                            } else {
                                this.$message.error(resp.msg);
                            }
                        });
                });
            } else {
                this.$notify.warning({
                    title: "提示",
                    message: "请至少勾选一个配置",
                    duration: this.$store.state.duration
                });
            }
        }
    },
    methods: {
        debouncedGetConfigList() {
            clearTimeout(this.searchDebounce);
            this.searchDebounce = setTimeout(() => {
                this.localCurrentPage = 1;
                this.getConfigList();
            }, 300);
        },
        handleSelectionChange(val) {
            this.selectConfig = val;
            // 更新是否已经选择Config, 父组件依赖这个属性来判断是否禁用批量删除按钮
            if (this.selectConfig.length > 0) {
                this.$emit("update:isSelectConfig", true);
            } else {
                this.$emit("update:isSelectConfig", false);
            }
        },
        handleCurrentChange() {
            this.$api
                .getConfigPaginationByPage({
                    params: {
                        page: this.localCurrentPage,
                        size: this.localPageSize,
                        project: this.project,
                        search: this.search
                    }
                })
                .then(resp => {
                    this.configData = resp;
                    this.$emit("update:currentPage", this.localCurrentPage);
                });
        },
        handleSizeChange(newSize) {
            this.localPageSize = newSize;
            // 计算新的最大页码
            let maxPage = Math.ceil(this.configData.count / newSize);
            if (this.localCurrentPage > maxPage) {
                // 如果当前页码超出了范围，请将其设置为最大页面
                this.localCurrentPage = maxPage;
            }
            this.$api
                .getConfigPaginationByPage({
                    params: {
                        page: this.localCurrentPage,
                        size: newSize,
                        project: this.project,
                        search: this.search
                    }
                })
                .then(resp => {
                    this.configData = resp;
                    this.$emit("update:pageSize", this.localPageSize);
                });
        },
        handleDelConfig(index) {
            this.$confirm("此操作将永久删除该配置, 是否继续?", "提示", {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning"
            }).then(() => {
                this.$api.delConfig(index).then(resp => {
                    if (resp.success) {
                        this.$message.success(resp.msg);
                        this.getConfigList();
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
            });
        },
        handleEditConfig(row) {
            this.$emit("respConfig", row);
        },
        handleCopyConfig(id, name) {
            this.$prompt("请输入配置名称", "提示", {
                closeOnClickModal: false,
                confirmButtonText: "确定",
                inputPattern: /^[\s\S]*.*[^\s][\s\S]*$/,
                inputErrorMessage: "配置名称不能为空",
                inputValue: name
            }).then(({ value }) => {
                this.$api
                    .copyConfig(id, {
                        name: value
                    })
                    .then(resp => {
                        if (resp.success) {
                            this.$message.success("配置复制成功");
                            this.getConfigList();
                        } else {
                            this.$message.error(resp.msg);
                        }
                    });
            });
        },
        cellMouseEnter(row) {
            this.currentRow = row;
        },
        cellMouseLeave() {
            this.currentRow = "";
        },
        getConfigList() {
            this.$api
                .configList({
                    params: {
                        page: this.localCurrentPage,
                        size: this.localPageSize,
                        project: this.project,
                        search: this.search
                    }
                })
                .then(resp => {
                    this.configData = resp;
                    this.loading = false;
                });
        },
        resetSearch() {
            this.search = "";
            this.localPageSize = 10;
            this.localCurrentPage = 1;
            this.getConfigList();
        }
    },

    mounted() {
        this.getConfigList();
    }
};
</script>

<style scoped>
.config__header {
    display: flex;
    align-items: center;
    margin-left: -30px;
}

.config__header--item {
    display: flex;
    margin-left: 10px;
}

.config-body-table {
    position: fixed;
    bottom: 0;
    right: 0;
    left: 220px;
    top: 150px;
    margin-left: -10px;
    padding-bottom: 60px;
}
</style>
