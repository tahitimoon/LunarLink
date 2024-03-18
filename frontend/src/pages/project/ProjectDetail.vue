<template>
    <div>
        <div class="scrollbar-inner">
            <ul class="title-project">
                <el-skeleton v-if="isLoading" :rows="1" style="width: 300px" />
                <li v-else class="title-li" title="Test API Project">
                    <b>{{ projectInfo.name }}</b>
                    <b class="desc-li">{{ projectInfo.desc }}</b>
                </li>
            </ul>
            <div style="display: flex; justify-content: space-around;">
                <el-card class="el-card-width">
                    <div slot="header">
                        <span>API</span>
                        <i class="iconfont">&#xe74a;</i>
                    </div>
                    <el-row type="flex">
                        <el-col :span="16">
                            <el-skeleton v-if="isLoading" :rows="6" />
                            <ApexCharts
                                v-else
                                :options="apiPieOptions"
                                :series="apiPieSeries"
                            ></ApexCharts>
                        </el-col>
                    </el-row>
                    <el-row type="flex" justify="end">
                        <el-col :span="12">
                            <el-skeleton v-if="isLoading" :rows="6" />
                            <ApexCharts
                                v-else
                                :options="apiCoverRateOptions"
                                :series="apiCoverRateSeries"
                            ></ApexCharts>
                        </el-col>
                    </el-row>
                </el-card>

                <el-card class="el-card-width">
                    <div slot="header">
                        <span>Case</span>
                        <i class="iconfont">&#xe6da;</i>
                    </div>
                    <el-row type="flex">
                        <el-col :span="16">
                            <el-skeleton v-if="isLoading" :rows="6" />
                            <ApexCharts
                                v-else
                                :options="casePieOptions"
                                :series="casePieSeries"
                            ></ApexCharts>
                        </el-col>
                    </el-row>

                    <el-row type="flex" justify="end">
                        <el-col :span="12">
                            <el-skeleton v-if="isLoading" :rows="6" />
                            <ApexCharts
                                v-else
                                :options="coreCaseCoverRateOptions"
                                :series="coreCaseCoverRateSeries"
                            ></ApexCharts>
                        </el-col>
                    </el-row>
                </el-card>

                <el-card class="el-card-width">
                    <div slot="header">
                        <span>Report</span>
                        <i class="iconfont">&#xe66e;</i>
                    </div>
                    <el-skeleton v-if="isLoading" :rows="11" />
                    <ApexCharts
                        v-else
                        :options="reportPieOptions"
                        :series="reportPieSeries"
                    ></ApexCharts>
                </el-card>
            </div>
            <div
                class="daily_data"
            >
                <el-card class="el-card-width">
                    <div slot="header">
                        <span>API每日创建</span>
                        <i class="iconfont">&#xe74a;</i>
                    </div>
                    <el-skeleton v-if="isLoading" :rows="6" />
                    <ApexCharts
                        v-else
                        type="area"
                        :options="apiAreaOptions"
                        :series="apiAreaSeries"
                    ></ApexCharts>
                </el-card>
                <el-card class="el-card-width">
                    <div slot="header">
                        <span>Case每日创建</span>
                        <i class="iconfont">&#xe6da;</i>
                    </div>
                    <el-skeleton v-if="isLoading" :rows="6" />
                    <ApexCharts
                        v-else
                        type="area"
                        :options="caseAreaOptions"
                        :series="caseAreaSeries"
                    ></ApexCharts>
                </el-card>
                <el-card class="el-card-width">
                    <div slot="header">
                        <span>Report每日创建</span>
                        <i class="iconfont">&#xe66e;</i>
                    </div>
                    <el-skeleton v-if="isLoading" :rows="6" />
                    <ApexCharts
                        v-else
                        type="area"
                        :options="reportAreaOptions"
                        :series="reportAreaSeries"
                    ></ApexCharts>
                </el-card>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "ProjectDetail",
    data() {
        return {
            visitInfo: {},
            projectInfo: {},
            apiPieOptions: {
                plotOptions: {
                    pie: {
                        donut: {
                            size: "50%",
                            labels: {
                                show: true,
                                total: {
                                    show: true,
                                    showAlways: true,
                                    label: "Total"
                                }
                            }
                        }
                    }
                },
                show: true,
                chart: {
                    id: "apiPie",
                    type: "donut"
                },
                // 饼图右上角的分类，会被接口返回值覆盖
                labels: ["手动创建的API", "从YAPI导入的API"]
            },
            apiCoverRateSeries: [],
            coreCaseCoverRateSeries: [],
            apiCoverRateOptions: {
                chart: {
                    height: 20,
                    type: "radialBar"
                },
                plotOptions: {
                    radialBar: {
                        hollow: {
                            margin: 15,
                            size: "50%"
                        },
                        dataLabels: {
                            showOn: "always",
                            name: {
                                offsetY: 0,
                                show: true,
                                color: "#888",
                                fontSize: "13px"
                            },
                            value: {
                                color: "#111",
                                fontSize: "16px",
                                show: true
                            }
                        }
                    }
                },
                stroke: {
                    lineCap: "round"
                },
                labels: ["接口覆盖率"]
            },
            coreCaseCoverRateOptions: {
                chart: {
                    height: 20,
                    type: "radialBar"
                },
                plotOptions: {
                    radialBar: {
                        hollow: {
                            margin: 15,
                            size: "50%"
                        },
                        dataLabels: {
                            showOn: "always",
                            name: {
                                offsetY: 0,
                                show: true,
                                color: "#888",
                                fontSize: "13px"
                            },
                            value: {
                                color: "#111",
                                fontSize: "16px",
                                show: true
                            }
                        }
                    }
                },
                stroke: {
                    lineCap: "round"
                },
                labels: ["核心用例覆盖率"]
            },
            casePieOptions: {
                plotOptions: {
                    pie: {
                        donut: {
                            size: "50%",
                            labels: {
                                show: true,
                                total: {
                                    show: true,
                                    showAlways: true,
                                    label: "Total"
                                }
                            }
                        }
                    }
                },
                show: true,
                chart: {
                    id: "casePie",
                    type: "donut"
                },
                // 饼图右上角的分类，会被接口返回值覆盖
                labels: ["冒烟用例", "集成用例", "监控用例", "核心用例"]
            },
            reportPieOptions: {
                plotOptions: {
                    pie: {
                        donut: {
                            size: "50%",
                            labels: {
                                show: true,
                                total: {
                                    show: true,
                                    showAlways: true,
                                    label: "Total"
                                }
                            }
                        }
                    }
                },
                show: true,
                chart: {
                    type: "donut"
                },
                // 饼图右上角的分类，会被接口返回值覆盖
                labels: ["调试", "异步", "定时"]
            },
            apiPieSeries: [],
            casePieSeries: [],
            reportPieSeries: [],
            visitCharOptions: {
                chart: {
                    id: "vuechart-example"
                },
                xaxis: {
                    categories: []
                }
            },
            apiAreaOptions: {
                chart: {
                    foreColor: "#aaa",
                    id: "apiArea"
                },
                xaxis: {
                    categories: []
                }
            },
            caseAreaOptions: {
                chart: {
                    id: "caseArea"
                },
                xaxis: {
                    categories: []
                }
            },
            reportAreaOptions: {
                chart: {
                    id: "reportArea"
                },
                xaxis: {
                    categories: []
                }
            },
            visitSeries: [
                {
                    name: "访问量",
                    data: []
                }
            ],
            apiAreaSeries: [
                {
                    name: "API创建数量",
                    data: []
                }
            ],
            caseAreaSeries: [
                {
                    name: "Case创建数量",
                    data: []
                }
            ],
            reportAreaSeries: [
                {
                    name: "Report创建数量",
                    data: []
                }
            ],
            isLoading: true
        };
    },
    methods: {
        getVisitData() {
            const project = this.$route.params.id;
            this.$api
                .getVisit({
                    params: {
                        project: project
                    }
                })
                .then((/** @type {{ recent7days: string[] }} */ res) => {
                    this.visitCharOptions = {
                        ...this.visitCharOptions,
                        ...{ xaxis: { categories: res.recent7days } }
                    };
                });
        },
        success(resp) {
            this.$notify({
                title: "成功",
                message: resp["msg"],
                type: "success",
                duration: this.$store.state.duration
            });
        },
        failure(resp) {
            this.$notify.error({
                title: "失败",
                message: resp["msg"],
                duration: this.$store.state.duration
            });
        },

        handleArea() {
            const res = this.projectInfo.daily_create_count;
            const apiDays = res.api.days;
            const caseDays = res.case.days;
            const reportDays = res.report.days;
            const apiCount = res.api.count;
            const caseCount = res.case.count;
            const reportCount = res.report.count;
            this.apiAreaOptions = {
                ...this.apiAreaOptions,
                ...{ xaxis: { categories: apiDays } }
            };
            this.caseAreaOptions = {
                ...this.caseAreaOptions,
                ...{ xaxis: { categories: caseDays } }
            };
            this.reportAreaOptions = {
                ...this.reportAreaOptions,
                ...{ xaxis: { categories: reportDays } }
            };
            this.apiAreaSeries[0].data = apiCount;
            this.caseAreaSeries[0].data = caseCount;
            this.reportAreaSeries[0].data = reportCount;

            this.apiCoverRateSeries.push(this.projectInfo.api_cover_rate);
            this.coreCaseCoverRateSeries.push(
                this.projectInfo.core_case_cover_rate
            );
        },
        handlePie() {
            const pi = this.projectInfo;
            this.apiPieSeries = pi.api_count_by_create_type.count;
            this.apiPieOptions = {
                ...this.apiPieOptions,
                ...{ labels: pi.api_count_by_create_type.type }
            };

            this.casePieSeries = pi.case_count_by_tag.count;
            this.casePieOptions = {
                ...this.casePieOptions,
                ...{ labels: pi.case_count_by_tag.tag }
            };

            this.reportPieSeries = pi.report_count_by_type.count;
            this.reportPieOptions = {
                ...this.reportPieOptions,
                ...{ labels: pi.report_count_by_type.type }
            };
        },
        getProjectDetail() {
            const pk = this.$route.params.id;
            this.$api.getProjectDetail(pk).then(resp => {
                this.projectInfo = resp;
                this.handleArea();
                this.handlePie();
                this.isLoading = false;
            });
        }
    },
    mounted() {
        this.getVisitData();
        this.getProjectDetail();
    }
};
</script>

<style scoped>
.title-project li a {
    font-size: 12px;
    text-decoration: none;
    color: #a3a3a3;
    margin-left: 20px;
}

.project_detail li {
    margin-top: 10px;
    text-indent: 20px;
    display: inline-block;
    height: 90px;
    width: calc(20% - 2px);
    border: 1px solid #ddd;
}

.title-project {
    margin-top: 15px;
    margin-left: 15px;
    margin-bottom: 10px;
}

.daily_data {
    display: flex; 
    justify-content: space-around;
    margin-top: 20px; 
    margin-bottom: 10px;
}

ul li {
    list-style: none;
}

.title-li {
    font-size: 24px;
    color: #607d8b;
}

.desc-li {
    margin-top: 10px;
    color: #b6b6b6;
    font-size: 14px;
}

.el-card-width {
    width: 32%;
}
</style>
