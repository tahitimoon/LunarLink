// 定义异步操作更改state对象中的数据状态
export default {
    initStore(context) {
        const projectName = localStorage.getItem("projectName");
        if (projectName) {
            context.commit("setProjectName", projectName);
        }
    }
};
