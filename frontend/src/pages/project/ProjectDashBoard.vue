<template>
    <div style="display: flex; justify-content: space-around; flex-wrap: wrap">
        <div class="api-case">
            <el-card>
                <div slot="header">
                    <span>每日趋势</span>
                    <i class="iconfont">&#xe66e;</i>
                </div>
                <el-skeleton v-if="isLoading" :rows="9" />
                <ApexCharts
                    v-else
                    :options="apiOptionsLine"
                    :series="apiCaseLineSeries"
                ></ApexCharts>
            </el-card>
        </div>

        <div class="api-case">
            <el-card>
                <div slot="header">
                    <span>每周指标</span>
                    <i class="iconfont">&#xe66e;</i>
                </div>
                <el-skeleton v-if="isLoading" :rows="9" />
                <ApexCharts
                    v-else
                    :options="optionsWeekBar"
                    :series="weekBarSeries"
                ></ApexCharts>
            </el-card>
        </div>

        <div class="api-case">
            <el-card>
                <div slot="header">
                    <span>每月指标</span>
                    <i class="iconfont">&#xe66e;</i>
                </div>
                <el-skeleton v-if="isLoading" :rows="9" />
                <ApexCharts
                    v-else
                    :options="optionsMonthBar"
                    :series="monthBarSeries"
                ></ApexCharts>
            </el-card>
        </div>

        <div class="api-case-monthly">
            <el-card>
                <div slot="header">
                    <span>近半年接口创建前5名统计</span>
                    <i class="iconfont">&#xe66e;</i>
                </div>
                <el-skeleton v-if="isLoading" :rows="9" />
                <ApexCharts
                    v-else
                    :options="apiMonthlyOptionsLine"
                    :series="apiMonthlyLineSeries"
                ></ApexCharts>
            </el-card>
        </div>

        <div class="api-case-monthly">
            <el-card>
                <div slot="header">
                    <span>近半年用例创建前5名统计</span>
                    <i class="iconfont">&#xe66e;</i>
                </div>
                <el-skeleton v-if="isLoading" :rows="9" />
                <ApexCharts
                    v-else
                    :options="caseMonthlyOptionsLine"
                    :series="caseMonthlyLineSeries"
                ></ApexCharts>
            </el-card>
        </div>

        <div class="api-case-monthly">
            <el-card>
                <div slot="header">
                    <span>报告日-周-月趋势</span>
                    <i class="iconfont">&#xe66e;</i>
                </div>
                <el-skeleton v-if="isLoading" :rows="12" />
                <ApexCharts
                    v-else
                    :options="reportOptionsLine"
                    :series="reportLineSeries"
                ></ApexCharts>
            </el-card>
        </div>
    </div>
</template>

<script>
export default {
    name: "ProjectDashBoard",
    data() {
        return {
            isLoading: true,
            weekBarSeries: [],
            monthBarSeries: [],
            optionsWeekBar: {
                chart: {
                    type: "bar",
                    stacked: true
                },
                plotOptions: {
                    bar: {
                        columnWidth: "30%",
                        horizontal: false
                    }
                },
                xaxis: {
                    categories: [
                        "前5周",
                        "前4周",
                        "前3周",
                        "前2周",
                        "前1周",
                        "当前周"
                    ]
                },
                fill: {
                    opacity: 1
                }
            },
            optionsMonthBar: {
                chart: {
                    type: "bar",
                    stacked: true
                },
                plotOptions: {
                    bar: {
                        columnWidth: "30%",
                        horizontal: false
                    }
                },
                xaxis: {
                    categories: [
                        "前5月",
                        "前4月",
                        "前3月",
                        "前2月",
                        "前1月",
                        "当前月"
                    ]
                },
                fill: {
                    opacity: 1
                }
            },
            apiCaseLineSeries: [],
            apiMonthlyLineSeries:[],
            caseMonthlyLineSeries:[],
            reportLineSeries: [],
            apiOptionsLine:{},
            apiMonthlyOptionsLine:{},
            caseMonthlyOptionsLine:{},
            reportOptionsLine:{},
            optionsLine: {
                chart: {
                    type: "area",
                    zoom: {
                        enabled: false
                    },
                    dropShadow: {
                        top: 3,
                        left: 2,
                        blur: 4,
                        opacity: 1
                    }
                },
                stroke: {
                    curve: "smooth",
                    widths: 2
                },
                markers: {
                    size: 6,
                    strokeWidth: 0,
                    hover: {
                        size: 9
                    }
                },
                grid: {
                    show: true,
                    padding: {
                        bottom: 0
                    }
                },
                labels: [],
                xaxis: {
                    tooltip: {
                        enabled: true
                    }
                },
                // 底部说明
                legend: {
                    position: "bottom",
                    horizontalAlign: "center"
                }
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
                    animations: {
                        enabled: true,
                        easing: "easeinout",
                        speed: 800
                    },
                    type: "donut"
                },
                // 饼图右上角的分类，会被接口返回值的覆盖
                labels: ["调试", "异步", "定时"]
            },
            reportPieSeries: [],
            reportRadiaOptions: {
                chart: {
                    type: "pie"
                },
                colors: ["#08f540", "#e50810"],
                labels: ["成功", "失败"],
                theme: {
                    monochrome: {
                        enabled: false
                    }
                },
                plotOptions: {
                    radialBar: {
                        size: "20%"
                    }
                },
                legend: {
                    show: true,
                    position: "left",
                    containerMarin: {
                        right: 0
                    }
                }
            },
            reportRadiaSeries: []
        };
    },
    methods: {
        getData() {
            this.$api.getDashboard().then(resp => {
                this.reportPieSeries = resp.report.type;
                this.reportRadiaSeries = resp.report.status;

                // 报告趋势
                this.reportLineSeries.push({
                    name: "日",
                    data: resp.report.day
                });
                this.reportLineSeries.push({
                    name: "周",
                    data: resp.report.week
                });
                this.reportLineSeries.push({
                    name: "月",
                    data: resp.report.month
                });
                this.reportOptionsLine = {
                    ...this.optionsLine,
                    ...{ labels: ["前5", "前4", "前3", "前2", "前1", "当前"] }
                };

                // 每日指标趋势
                this.apiCaseLineSeries.push({
                    name: "Case",
                    data: resp.case.day
                });
                this.apiCaseLineSeries.push({
                    name: "API",
                    data: resp.api.day
                });
                this.apiCaseLineSeries.push({
                    name: "Yapi",
                    data: resp.yapi.day
                });
                this.apiOptionsLine = {
                    ...this.optionsLine,
                    ...{ labels: resp.recent_days }
                };

                // 每周指标
                this.weekBarSeries.push({
                    name: "Case",
                    data: resp.case.week
                });
                this.weekBarSeries.push({ name: "API", data: resp.api.week });
                this.weekBarSeries.push({
                    name: "Yapi",
                    data: resp.yapi.week
                });
                this.optionsWeekBar = {
                    ...this.optionsWeekBar,
                    ...{ xaxis: { categories: resp.recent_weeks } }
                };

                // 每月指标
                this.monthBarSeries.push({
                    name: "Case",
                    data: resp.case.month
                });
                this.monthBarSeries.push({ name: "API", data: resp.api.month });
                this.monthBarSeries.push({
                    name: "Yapi",
                    data: resp.yapi.month
                });
                this.optionsMonthBar = {
                    ...this.optionsMonthBar,
                    ...{ xaxis: { categories: resp.recent_months } }
                };

                // 近半年接口创建前5名统计
                resp.api.monthly_top_creators.forEach(creator => {
                    this.apiMonthlyLineSeries.push({
                        name: creator,
                        data: resp.api.monthly_creator_counts[creator]
                    });
                });
                this.apiMonthlyOptionsLine = {
                    ...this.optionsLine,
                    ...{ labels: resp.recent_months }
                };

                // 近半年用例创建前5名统计
                resp.case.monthly_top_creators.forEach(creator => {
                    this.caseMonthlyLineSeries.push({
                        name: creator,
                        data: resp.case.monthly_creator_counts[creator]
                    });
                });
                this.caseMonthlyOptionsLine = {
                    ...this.optionsLine,
                    ...{ labels: resp.recent_months }
                };

                this.isLoading = false;
            });
        }
    },
    mounted() {
        this.getData();
    }
};
</script>

<style scoped>
.api-case {
    margin-top: 10px;
    width: 32%;
}

.api-case-monthly {
    margin-top: 10px;
    width: 32%;
    margin-bottom: 10px;
}
</style>
