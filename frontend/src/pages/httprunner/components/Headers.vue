<template>
    <div>
        <el-table
            highlight-current-row
            stripe
            :data="tableData"
            :height="height"
            style="width: 100%;"
            :border="false"
            @cell-mouse-enter="cellMouseEnter"
            @cell-mouse-leave="cellMouseLeave"
            :cell-style="{ paddingTop: '4px', paddingBottom: '4px' }"
        >
            <el-table-column label="标签" width="300">
                <template slot-scope="scope">
                    <el-autocomplete
                        clearable
                        v-model.trim="scope.row.key"
                        :fetch-suggestions="querySearch"
                        placeholder="头部标签"
                    ></el-autocomplete>
                </template>
            </el-table-column>

            <el-table-column label="内容" width="400">
                <template slot-scope="scope">
                    <el-input
                        clearable
                        v-model.trim="scope.row.value"
                        placeholder="头部内容"
                    ></el-input>
                </template>
            </el-table-column>

            <el-table-column label="描述" width="220">
                <template slot-scope="scope">
                    <el-input
                        clearable
                        v-model.trim="scope.row.desc"
                        placeholder="头部信息简要描述"
                    ></el-input>
                </template>
            </el-table-column>

            <el-table-column>
                <template slot="header" slot-scope="scope">
                    <div
                        v-show="isHoveringHeader || isHoveringRow"
                        style="cursor: pointer; font-weight: bold; color: #409EFF; font-size: 14px;"
                        @click="handleBulkEdit"
                    >
                        <i class="el-icon-edit"></i>
                        <span>批量编辑</span>
                    </div>
                </template>

                <template slot-scope="scope">
                    <el-row v-show="scope.row === currentRow">
                        <el-button
                            icon="el-icon-circle-plus-outline"
                            size="mini"
                            type="info"
                            @click="handleAdd"
                        ></el-button>

                        <el-button
                            icon="el-icon-delete"
                            size="mini"
                            type="danger"
                            v-show="scope.$index !== 0"
                            @click="handleDelete(scope.$index)"
                        ></el-button>
                    </el-row>
                </template>
            </el-table-column>
        </el-table>

        <el-dialog
            title="批量编辑"
            :visible.sync="showDialog"
            :close-on-click-modal="false"
            width="45%"
        >
            <div style="margin-bottom: 8px;">
                <span style="color: #7d858e;">
                    格式:&nbsp;<span>参数名:</span><span>参数值</span>
                </span>
            </div>
            <el-input
                type="textarea"
                :autosize="{ minRows: 10, maxRows: 16 }"
                v-model="textareaData"
            ></el-input>
            <div style="margin-top: 8px; color: #7d858e;">
                字段之间以英文冒号( : )分隔，多条记录以换行分隔
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button @click="showDialog = false">取 消</el-button>
                <el-button type="primary" @click="handleSubmit"
                    >确 定</el-button
                >
            </span>
        </el-dialog>
    </div>
</template>

<script>
import { isEqual } from "lodash";

export default {
    name: "Headers",
    props: {
        save: Boolean,
        header: {
            required: false
        }
    },
    data() {
        return {
            headerOptions: [
                {
                    value: "Accept"
                },
                {
                    value: "Accept-Charset"
                },
                {
                    value: "Accept-Language"
                },
                {
                    value: "Accept-Datetime"
                },
                {
                    value: "Authorization"
                },
                {
                    value: "Cache-Control"
                },
                {
                    value: "Connection"
                },
                {
                    value: "Cookie"
                },
                {
                    value: "Content-Length"
                },
                {
                    value: "Content-MD5"
                },
                {
                    value: "Content-Type"
                },
                {
                    value: "Expect"
                },
                {
                    value: "Date"
                },
                {
                    value: "From"
                },
                {
                    value: "Host"
                },
                {
                    value: "If-Match"
                },
                {
                    value: "If-Modified-Since"
                },
                {
                    value: "If-None-Match"
                },
                {
                    value: "If-Range"
                },
                {
                    value: "If-unmodified-since"
                },
                {
                    value: "Max-Forwards"
                },
                {
                    value: "Origin"
                },
                {
                    value: "Pragma"
                },
                {
                    value: "Proxy-Authorization"
                },
                {
                    value: "Range"
                },
                {
                    value: "Referer"
                },
                {
                    value: "TE"
                },
                {
                    value: "User-Agent"
                },
                {
                    value: "Upgrade"
                },
                {
                    value: "Via"
                },
                {
                    value: "Warning"
                }
            ],
            isHoveringHeader: false,
            isHoveringRow: false,
            showDialog: false,
            textareaData: "",
            currentRow: "",
            originalTableData: [],
            tableData: [{ key: "", value: "", desc: "" }]
        };
    },
    watch: {
        save() {
            this.$emit("header", this.parseHeader(), this.tableData);
        },
        tableData: {
            deep: true,
            handler() {
                this.checkDataChanges();
            }
        },
        header: {
            deep: true,
            handler(newVal) {
                if (newVal.length !== 0) {
                    this.tableData = JSON.parse(JSON.stringify(newVal));
                    this.setOriginalData();
                }
            }
        }
    },
    methods: {
        setOriginalData() {
            this.originalTableData = JSON.parse(JSON.stringify(this.tableData));
        },
        checkDataChanges() {
            const hasChanged = !isEqual(this.originalTableData, this.tableData);
            this.$emit("dataChanged", hasChanged);
        },
        handleSubmit() {
            this.showDialog = false;
            const lines = this.textareaData.split("\n");
            let data = lines
                .filter(item => item.trim() !== "") // 过滤掉空的行
                .map(item => {
                    const colonIndex = item.indexOf(":"); // 找到第一个冒号的位置
                    if (colonIndex === -1) {
                        // 如果没有找到冒号，跳过这一行
                        return null;
                    }
                    const key = item.substring(0, colonIndex).trim(); // 提取key
                    const value = item.substring(colonIndex + 1).trim(); // 提取value
                    return {
                        key,
                        value,
                        desc: ""
                    };
                })
                .filter(item => item !== null); // 过滤掉无效的行

            if (data.length === 0) {
                // 如果data为空，添加一行默认数据
                data.push({
                    key: "",
                    value: "",
                    desc: ""
                });
            }
            this.tableData = data;
        },
        handleBulkEdit() {
            this.showDialog = true;
            const data = this.tableData;
            this.textareaData = data
                .filter(item => item.key || item.value) // 确保key或value存在
                .map(item => {
                    const flag = ":";
                    return `${item.key}${flag}${item.value}`;
                })
                .join("\n");
        },
        querySearch(queryString, cb) {
            let headerOptions = this.headerOptions;
            let results = queryString
                ? headerOptions.filter(this.createFilter(queryString))
                : headerOptions;
            cb(results);
        },
        createFilter(queryString) {
            return headerOptions => {
                return (
                    headerOptions.value
                        .toLowerCase()
                        .indexOf(queryString.toLowerCase()) === 0
                );
            };
        },
        cellMouseEnter(row) {
            this.currentRow = row;
            this.isHoveringRow = true;
        },
        cellMouseLeave() {
            this.currentRow = "";
            this.isHoveringRow = false;
        },
        handleAdd() {
            this.tableData.push({
                key: "",
                value: "",
                desc: ""
            });
        },
        handleDelete(index) {
            this.tableData.splice(index, 1);
        },
        // 头部信息格式化
        parseHeader() {
            let header = {
                header: {},
                desc: {}
            };
            for (let content of this.tableData) {
                if (content["key"] !== "" && content["value"] !== "") {
                    header.header[content["key"]] = content["value"];
                    header.desc[content["key"]] = content["desc"];
                }
            }
            return header;
        }
    },
    mounted() {
        this.setOriginalData();
        const table = this.$el.querySelector(".el-table__header-wrapper");
        table.addEventListener("mouseenter", () => {
            this.isHoveringHeader = true;
        });
        table.addEventListener("mouseleave", () => {
            this.isHoveringHeader = false;
        });
    },
    computed: {
        height() {
            return window.screen.height - 440;
        }
    }
};
</script>

<style scoped></style>
