<template>
    <el-container>
        <el-header style="padding: 10px 0; height: 50px">
            <div class="report__header">
                <div class="report__header--item">
                    <el-input
                        clearable
                        size="small"
                        placeholder="请输入报告名称"
                        v-model="search"
                        style="width: 300px"
                    >
                    </el-input>
                </div>
                <div class="report__header--item">
                    <el-dropdown @command="reportTypeChangeHandle">
                        <el-button type="primary" size="small">
                            类型
                            <i class="el-icon-arrow-down el-icon--right"></i>
                        </el-button>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item command="1"
                                >调试</el-dropdown-item
                            >
                            <el-dropdown-item command="2"
                                >异步</el-dropdown-item
                            >
                            <el-dropdown-item command="3"
                                >定时</el-dropdown-item
                            >
                            <el-dropdown-item command="">全部</el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>
                <div class="report__header--item">
                    <el-dropdown @command="reportStatusChangeHandle">
                        <el-button type="primary" size="small">
                            结果
                            <i class="el-icon-arrow-down el-icon--right"></i>
                        </el-button>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item command="0"
                                >失败</el-dropdown-item
                            >
                            <el-dropdown-item command="1"
                                >成功</el-dropdown-item
                            >
                            <el-dropdown-item command="0"
                                >全部</el-dropdown-item
                            >
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>

                <div class="report__header--item">
                    <el-button
                        plain
                        size="small"
                        icon="el-icon-refresh"
                        @click="resetSearch"
                        >重置</el-button
                    >
                </div>

                <div class="report__header--item">
                    <el-button
                        :title="'删除'"
                        :disabled="!isSelectReport"
                        v-if="isSuperuser"
                        type="danger"
                        icon="el-icon-delete"
                        size="small"
                        @click="delSelectionReports"
                        >批量删除</el-button
                    >
                </div>

                <el-switch
                    style="margin-left: 10px"
                    v-model="onlyMe"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    active-text="只看自己"
                ></el-switch>
            </div>
        </el-header>

        <el-container>
            <el-main style="padding: 0; margin-left: 10px; margin-top: 10px">
                <el-dialog
                    v-if="dialogTableVisible"
                    :visible.sync="dialogTableVisible"
                    width="70%"
                >
                    <report :summary="summary"></report>
                </el-dialog>
                <div class="report__body__table">
                    <el-table
                        :data="reportData.results"
                        highlight-current-row
                        stripe
                        height="calc(100%)"
                        @cell-mouse-enter="cellMouseEnter"
                        @cell-mouse-leave="cellMouseLeave"
                        @selection-change="handleSelectionChange"
                        v-loading="loading"
                        style="margin-top: -10px"
                    >
                        <el-table-column type="selection" width="55">
                        </el-table-column>

                        <el-table-column label="报告类型" width="100">
                            <template slot-scope="scope">
                                <el-tag color="#2C3E50" style="color: white">{{
                                    scope.row.type
                                }}</el-tag>
                            </template>
                        </el-table-column>

                        <el-table-column label="报告名称" width="250">
                            <template slot-scope="scope">
                                <div
                                    :title="scope.row.name"
                                    style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                                >
                                    {{ scope.row.name }}
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column label="执行结果" width="100">
                            <template slot-scope="scope">
                                <el-button
                                    :type="
                                        scope.row.success ? 'success' : 'danger'
                                    "
                                    size="mini"
                                >
                                    {{ scope.row.success ? "成功" : "失败" }}
                                </el-button>
                            </template>
                        </el-table-column>

                        <el-table-column label="耗时" width="100">
                            <template slot-scope="scope">
                                <div
                                    v-text="
                                        scope.row.time.duration.toFixed(3) +
                                            ' 秒'
                                    "
                                ></div>
                            </template>
                        </el-table-column>

                        <el-table-column label="总计接口" width="80">
                            <template slot-scope="scope">
                                <el-tag>{{ scope.row.stat.testsRun }}</el-tag>
                            </template>
                        </el-table-column>

                        <el-table-column label="通过" width="80">
                            <template slot-scope="scope">
                                <el-tag type="success">{{
                                    scope.row.stat.successes
                                }}</el-tag>
                            </template>
                        </el-table-column>

                        <el-table-column label="失败" width="80">
                            <template slot-scope="scope">
                                <el-tag type="danger">{{
                                    scope.row.stat.failures
                                }}</el-tag>
                            </template>
                        </el-table-column>

                        <el-table-column label="异常" width="80">
                            <template slot-scope="scope">
                                <el-tag type="warning">{{
                                    scope.row.stat.errors
                                }}</el-tag>
                            </template>
                        </el-table-column>

                        <el-table-column label="执行人" width="100">
                            <template slot-scope="scope">
                                <div
                                    :title="scope.row.creator"
                                    style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                                >
                                    <svg class="icon" aria-hidden="true">
                                        <use
                                            :xlink:href="
                                                !scope.row.creator
                                                    ? '#icon-jiqiren'
                                                    : '#icon-sharpicons_user'
                                            "
                                        ></use>
                                    </svg>
                                    <span>{{
                                        !scope.row.creator
                                            ? "机器人"
                                            : scope.row.creator
                                    }}</span>
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column label="执行时间" width="180">
                            <template slot-scope="scope">
                                <div>
                                    {{
                                        scope.row.time.start_at
                                            | timestampToTime
                                    }}
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column label="报告操作">
                            <template slot-scope="scope">
                                <el-row v-show="currentRow === scope.row">
                                    <div
                                        style="display: flex; align-items: center;"
                                    >
                                        <el-button
                                            type="info"
                                            icon="el-icon-refresh-right"
                                            circle
                                            size="mini"
                                            title="重新运行失败用例"
                                            v-show="handleShowReRun(scope.row)"
                                            @click="
                                                handleRunFailCase(scope.row)
                                            "
                                        ></el-button>
                                        <el-button
                                            type="success"
                                            icon="el-icon-view"
                                            circle
                                            size="mini"
                                            @click="
                                                handleWatchReports(scope.row.id)
                                            "
                                        ></el-button>
                                        <el-button
                                            type="danger"
                                            icon="el-icon-delete"
                                            title="删除"
                                            circle
                                            size="mini"
                                            @click="
                                                handleDelReports(scope.row.id)
                                            "
                                        ></el-button>
                                    </div>
                                </el-row>
                            </template>
                        </el-table-column>
                    </el-table>
                    <div class="pagination-container">
                        <el-pagination
                            v-show="reportData.count !== 0"
                            @size-change="handleSizeChange"
                            @current-change="handleCurrentChange"
                            :current-page.sync="currentPage"
                            :page-sizes="[10, 20, 30, 40]"
                            :page-size="pageSize"
                            :pager-count="5"
                            :total="reportData.count"
                            layout="total, sizes, prev, pager, next, jumper"
                            background
                        ></el-pagination>
                    </div>
                </div>
            </el-main>
        </el-container>
    </el-container>
</template>

<script>
import Report from "@/pages/reports/DebugReport";
export default {
    name: "ReportList",
    components: {
        Report
    },
    data() {
        return {
            search: "",
            searchDebounce: null,
            selectReports: [],
            currentRow: "",
            currentPage: 1,
            pageSize: 10,
            onlyMe: false,
            isSuperuser: this.$store.state.is_superuser,
            reportType: "",
            reportStatus: "",
            reportData: {
                count: 0,
                results: []
            },
            dialogTableVisible: false,
            summary: {},
            loading: true,
            isSelectReport: false
        };
    },
    methods: {
        cellMouseEnter(row) {
            this.currentRow = row;
        },
        cellMouseLeave() {
            this.currentRow = "";
        },
        handleWatchReports(index) {
            let reportUrl =
                this.$api.baseUrl + this.$store.state.report_path + index;
            window.open(reportUrl);
        },
        handleSelectionChange(val) {
            this.selectReports = val;
            // 更新是否已经选择Report, 依赖这个属性来判断是否禁用批量删除按钮
            this.isSelectReport = this.selectReports.length > 0;
        },
        reportTypeChangeHandle(command) {
            this.reportType = command;
            this.currentPage = 1;
            this.getReportList();
        },
        reportStatusChangeHandle(command) {
            this.reportStatus = command;
            this.currentPage = 1;
            this.getReportList();
        },
        resetSearch() {
            this.pageSize = 10;
            this.search = "";
            this.reportType = "";
            this.reportStatus = "";
            this.currentPage = 1;
            this.onlyMe = false;
            this.getReportList();
        },
        handleCurrentChange() {
            this.$api
                .getReportPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: this.pageSize,
                        project: this.$route.params.id,
                        search: this.search,
                        reportType: this.reportType,
                        reportStatus: this.reportStatus,
                        onlyMe: this.onlyMe
                    }
                })
                .then(resp => {
                    this.reportData = resp;
                });
        },
        handleSizeChange(newSize) {
            this.pageSize = newSize;
            // 计算新的最大页码
            let maxPage = Math.ceil(this.reportData.count / newSize);
            if (this.currentPage > maxPage) {
                // 如果当前页码超出了范围，请将其设置为最大页面
                this.currentPage = maxPage;
            }
            this.$api
                .getReportPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: newSize,
                        project: this.$route.params.id,
                        search: this.search,
                        reportType: this.reportType,
                        reportStatus: this.reportStatus,
                        onlyMe: this.onlyMe
                    }
                })
                .then(resp => {
                    this.reportData = resp;
                });
        },
        handleRunFailCase(row) {
            this.loading = true;
            this.$api
                .runMultiTest({
                    name: row.name,
                    project: this.$route.params.id,
                    case_config_mapping_list:
                        row.stat.failure_case_config_mapping_list
                })
                .then(resp => {
                    this.getReportList();
                    this.loading = false;
                    this.dialogTableVisible = true;
                    this.summary = resp;
                })
                .catch(err => {
                    this.$message.error(err);
                    this.loading = false;
                });
        },
        handleDelReports(index) {
            this.$confirm("此操作将永久删除该测试报告，是否继续？", "提示", {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning"
            }).then(() => {
                this.$api.delReports(index).then(resp => {
                    if (resp.success) {
                        this.$message.success(resp.msg);
                        this.getReportList();
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
            });
        },
        delSelectionReports() {
            if (this.selectReports.length !== 0) {
                this.$confirm(
                    "此操作将永久删除该测试报告，是否继续？",
                    "提示",
                    {
                        confirmButtonText: "确定",
                        cancelButtonText: "取消",
                        type: "warning"
                    }
                ).then(() => {
                    this.$api
                        .delAllReports({ data: this.selectReports })
                        .then(resp => {
                            this.$message.success(resp.msg);
                            this.getReportList();
                        });
                });
            } else {
                this.$message.warning("请至少勾选一个测试报告");
            }
        },
        getReportList() {
            this.$api
                .reportList({
                    params: {
                        project: this.$route.params.id,
                        search: this.search,
                        reportType: this.reportType,
                        reportStatus: this.reportStatus,
                        page: this.currentPage,
                        size: this.pageSize,
                        onlyMe: this.onlyMe
                    }
                })
                .then(resp => {
                    this.reportData = resp;
                    this.loading = false;
                });
        },
        handleShowReRun(row) {
            try {
                if (
                    row.stat.failure_case_config_mapping_list.length > 0 &&
                    row.stat.failure_case_config_mapping_list[0].config_name !==
                        undefined
                ) {
                    return true;
                }
            } catch (e) {
                return false;
            }
        },
        debouncedGetReportList() {
            clearTimeout(this.searchDebounce);
            this.searchDebounce = setTimeout(() => {
                this.currentPage = 1;
                this.getReportList();
            }, 300);
        }
    },
    watch: {
        search() {
            this.debouncedGetReportList();
        },
        onlyMe() {
            this.debouncedGetReportList();
        }
    },
    mounted() {
        this.debouncedGetReportList();
    }
};
</script>

<style scoped>
.report__header {
    display: flex;
    align-items: center;
}

.report__header--item {
    display: flex;
    margin-left: 10px;
}

.report__body__table {
    position: fixed;
    bottom: 0;
    right: 0;
    left: 220px;
    top: 120px;
    margin-left: -10px;
    padding-bottom: 60px;
}
</style>
