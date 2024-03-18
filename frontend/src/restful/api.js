import axios from "axios";
import store from "../store/state";
import router from "../router";
import { Message } from "element-ui";

export let baseUrl = process.env.VUE_APP_BASE_URL;

axios.defaults.withCredentials = true;
axios.defaults.baseURL = baseUrl;

axios.interceptors.request.use(
    function(config) {
        if (
            !config.url.startsWith("/api/user") ||
            config.url === "/api/user/list" ||
            config.url === "/api/user/login_log"
        ) {
            // 在请求拦截中，每次请求，都会加上一个Authorization头
            config.headers.Authorization = store.token;

            // 取url地址的第四位作为projectId, 如果不存在，默认设置为0
            let projectId = window.location.pathname.split("/")[3];
            projectId = projectId ? projectId : 0;
            config.headers["Project"] = projectId;
        }
        return config;
    },
    function(error) {
        return Promise.reject(error);
    }
);

axios.interceptors.response.use(
    function(response) {
        return response; // 安全地返回 response
    },
    function(error) {
        if (axios.isCancel(error)) {
            // 请求被取消
            if (error.message !== "User cancelled the request") {
                Message.error({
                    message: "请求超时，请稍后再试",
                    duration: 2000
                });
            }
        } else {
            // 其他错误
            try {
                let status = error.response ? error.response.status : 0;
                if (status === 401) {
                    router.replace({
                        name: "Login"
                    });
                }
                if (status === 500) {
                    Message.error({
                        message: "服务器内部异常, 请检查",
                        duration: 2000
                    });
                }
                if (status === 403) {
                    Message.error({
                        message: error.response.data.detail,
                        duration: 2000
                    });
                }
            } catch (e) {
                Message.error({
                    message: "服务器连接超时, 请重试",
                    duration: 2000
                });
            }
        }
        return Promise.reject(error);
    }
);

export const login = params => {
    return axios.post("/api/user/login", params).then(res => res.data);
};

export const addProject = params => {
    return axios.post("/api/lunarlink/project", params).then(res => res.data);
};

export const updateProject = params => {
    return axios.patch("/api/lunarlink/project", params).then(res => res.data);
};

export const deleteProject = config => {
    return axios
        .delete("/api/lunarlink/project", config)
        .then(res => res.data);
};

export const getProjectList = () => {
    return axios.get("/api/lunarlink/project").then(res => res.data);
};

export const getPagination = url => {
    return axios.get(url).then(res => res.data);
};

export const getUserList = () => {
    return axios.get("/api/user/list").then(res => res.data);
};

export const getDashboard = () => {
    return axios.get("/api/lunarlink/dashboard").then(res => res.data);
};

export const getVisit = params => {
    return axios.get("/api/lunarlink/visit", params).then(res => res.data);
};

export const getProjectDetail = pk => {
    return axios.get("/api/lunarlink/project/" + pk).then(res => res.data);
};

export const updateTree = (treeId, params) => {
    return axios
        .patch("/api/lunarlink/tree/" + treeId, params)
        .then(res => res.data);
};

export const getTree = (projectId, params) => {
    return axios
        .get("/api/lunarlink/tree/" + projectId, params)
        .then(res => res.data.data);
};

export const getAllConfig = projectId => {
    return axios
        .get("/api/lunarlink/config/" + projectId)
        .then(res => res.data);
};

export const getProjectYapiInfo = pk => {
    return axios
        .get("/api/lunarlink/project/yapi/" + pk)
        .then(res => res.data);
};

export const addYAPI = projectId => {
    return axios
        .post("/api/lunarlink/yapi/" + projectId)
        .then(res => res.data);
};

export const addAPI = params => {
    return axios.post("/api/lunarlink/api", params).then(res => res.data);
};

export const updateAPI = (url, params) => {
    return axios
        .patch("/api/lunarlink/api/" + url, params)
        .then(res => res.data);
};

export const apiList = params => {
    return axios.get("/api/lunarlink/api", params).then(res => res.data);
};

export const delAllAPI = params => {
    return axios.delete("/api/lunarlink/api", params).then(res => res.data);
};

export const tagAPI = params => {
    return axios.patch("/api/lunarlink/api/tag", params).then(res => res.data);
};

export const delAPI = apiId => {
    return axios.delete("/api/lunarlink/api/" + apiId).then(res => res.data);
};

export const copyAPI = (apiId, params) => {
    return axios
        .post("/api/lunarlink/api/" + apiId, params)
        .then(res => res.data);
};

export const syncCaseStep = apiId => {
    return axios
        .patch("/api/lunarlink/api/sync/" + apiId)
        .then(res => res.data);
};

export const getAPISingle = apiId => {
    return axios.get("/api/lunarlink/api/" + apiId).then(res => res.data);
};

export const moveAPI = params => {
    return axios
        .patch("/api/lunarlink/api/move_api", params)
        .then(res => res.data);
};

export const getPaginationByPage = params => {
    return axios.get("/api/lunarlink/api", params).then(res => res.data);
};

export const runAPIByPk = (apiId, params, cancelToken) => {
    return axios
        .get("/api/lunarlink/run_api_pk/" + apiId, {
            params: params,
            cancelToken: cancelToken
        })
        .then(res => res.data);
};

export const runSingleAPI = params => {
    return axios.post("/api/lunarlink/run_api", params).then(res => res.data);
};

// TODO: 上传文件接口需要优化，后端当前不存在此接口
export const uploadFile = url => {
    return baseUrl + "/api/lunarlink/file/?token=" + store.token;
};

export const addConfig = params => {
    return axios.post("/api/lunarlink/config", params).then(res => res.data);
};

export const updateConfig = (configId, params) => {
    return axios
        .patch("/api/lunarlink/config/" + configId, params)
        .then(res => res.data);
};

export const configList = params => {
    return axios.get("/api/lunarlink/config", params).then(res => res.data);
};

export const delAllConfig = params => {
    return axios.delete("/api/lunarlink/config", params).then(res => res.data);
};

export const delConfig = configId => {
    return axios
        .delete("/api/lunarlink/config/" + configId)
        .then(res => res.data);
};

export const copyConfig = (configId, params) => {
    return axios
        .post("/api/lunarlink/config/" + configId, params)
        .then(res => res.data);
};

export const getConfigPaginationByPage = params => {
    return axios.get("/api/lunarlink/config", params).then(res => res.data);
};

export const delAllTest = params => {
    return axios.delete("/api/lunarlink/test", params).then(res => res.data);
};

export const testList = params => {
    return axios.get("/api/lunarlink/test", params).then(res => res.data);
};

export const runSuiteTree = params => {
    return axios
        .post("/api/lunarlink/run_suite_tree", params)
        .then(res => res.data);
};

export const moveCase = params => {
    return axios
        .patch("/api/lunarlink/test/move_case", params)
        .then(res => res.data);
};

export const tagCase = params => {
    return axios
        .patch("/api/lunarlink/test/tag", params)
        .then(res => res.data);
};

export const runTestByPk = (testId, params) => {
    return axios
        .get("/api/lunarlink/run_testsuite_pk/" + testId, params)
        .then(res => res.data);
};

export const runTestByPkWithCancel = (testId, params, cancelToken) => {
    return axios
        .get("/api/lunarlink/run_testsuite_pk/" + testId, {
            params: params,
            cancelToken: cancelToken
        })
        .then(res => res.data);
};

export const getTestPaginationByPage = params => {
    return axios.get("/api/lunarlink/test", params).then(res => res.data);
};

export const editTest = testId => {
    return axios
        .get("/api/lunarlink/teststep/" + testId)
        .then(res => res.data);
};

export const copyTest = (testId, params) => {
    return axios
        .post("/api/lunarlink/test/" + testId, params)
        .then(res => res.data);
};

export const delTest = pk => {
    return axios.delete("/api/lunarlink/test/" + pk).then(res => res.data);
};

export const syncTest = testId => {
    return axios.put("/api/lunarlink/test/" + testId).then(res => res.data);
};

export const addTestCase = params => {
    return axios.post("/api/lunarlink/test", params).then(res => res.data);
};

export const updateTestCase = (testId, params) => {
    return axios
        .patch("/api/lunarlink/test/" + testId, params)
        .then(res => res.data);
};

export const runSingleTestSuite = params => {
    return axios
        .post("/api/lunarlink/run_testsuite", params)
        .then(res => res.data);
};

export const runSingleTest = params => {
    return axios.post("/api/lunarlink/run_test", params).then(res => res.data);
};

export const getAPIPaginationByPage = params => {
    return axios.get("/api/lunarlink/api", params).then(res => res.data);
};

export const deleteVariables = variableId => {
    return axios
        .delete("/api/lunarlink/variables/" + variableId)
        .then(res => res.data);
};

export const variablesList = params => {
    return axios.get("/api/lunarlink/variables", params).then(res => res.data);
};

export const getVariablesPaginationByPage = params => {
    return axios.get("/api/lunarlink/variables", params).then(res => res.data);
};

export const delAllVariables = params => {
    return axios
        .delete("/api/lunarlink/variables", params)
        .then(res => res.data);
};

export const addVariables = params => {
    return axios
        .post("/api/lunarlink/variables", params)
        .then(res => res.data);
};

export const updateVariables = (variablesId, params) => {
    return axios
        .patch("/api/lunarlink/variables/" + variablesId, params)
        .then(res => res.data);
};

export const loginLogList = params => {
    return axios.get("/api/user/login_log", params).then(res => res.data);
};

export const loginLogPaginationByPage = params => {
    return axios.get("/api/user/login_log", params).then(res => res.data);
};

export const runDebugtalk = params => {
    return axios
        .post("/api/lunarlink/debugtalk", params)
        .then(res => res.data);
};

export const updateDebugtalk = params => {
    return axios
        .patch("/api/lunarlink/debugtalk", params)
        .then(res => res.data);
};

export const getDebugtalk = debugtalkId => {
    return axios
        .get("/api/lunarlink/debugtalk/" + debugtalkId)
        .then(res => res.data);
};

export const delTasks = taskId => {
    return axios
        .delete("/api/lunarlink/schedule/" + taskId)
        .then(res => res.data);
};

export const taskList = params => {
    return axios.get("/api/lunarlink/schedule", params).then(res => res.data);
};

export const patchTask = (taskId, params) => {
    return axios
        .patch("/api/lunarlink/schedule/" + taskId, params)
        .then(res => res.data);
};

export const copyTask = (taskId, params) => {
    return axios
        .post("/api/lunarlink/schedule/" + taskId, params)
        .then(res => res.data);
};

export const runTask = taskId => {
    return axios
        .get("/api/lunarlink/schedule/" + taskId)
        .then(res => res.data);
};

export const getTaskPaginationByPage = params => {
    return axios.get("/api/lunarlink/schedule", params).then(res => res.data);
};

export const addTask = params => {
    return axios.post("/api/lunarlink/schedule", params).then(res => res.data);
};

export const updateTask = (taskId, data) => {
    return axios({
        method: "put",
        url: "/api/lunarlink/schedule/" + taskId,
        data: data
    }).then(res => res.data);
};

export const reportList = params => {
    return axios.get("/api/lunarlink/reports", params).then(res => res.data);
};

export const getReportPaginationByPage = params => {
    return axios.get("/api/lunarlink/reports", params).then(res => res.data);
};

export const runMultiTest = params => {
    return axios
        .post("/api/lunarlink/run_multi_tests", params)
        .then(res => res.data);
};

export const delReports = reportId => {
    return axios
        .delete("/api/lunarlink/reports/" + reportId)
        .then(res => res.data);
};

export const delAllReports = params => {
    return axios
        .delete("/api/lunarlink/reports", params)
        .then(res => res.data);
};

export const recordStart = params => {
    return axios
        .get("/api/lunarlink/record/start", params)
        .then(res => res.data);
};

export const recordStop = params => {
    return axios
        .get("/api/lunarlink/record/stop", params)
        .then(res => res.data);
};

export const getRecordStatus = params => {
    return axios
        .get("/api/lunarlink/record/status", params)
        .then(res => res.data);
};

export const recordRemove = params => {
    return axios
        .get("/api/lunarlink/record/remove", params)
        .then(res => res.data);
};

export const generateTestCase = params => {
    return axios
        .post("/api/lunarlink/record_case", params)
        .then(res => res.data);
};
