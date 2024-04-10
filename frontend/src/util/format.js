/**
 * 将日期对象转化为指定格式的日期字符串
 * @param {Date} time - 日期对象
 * @param {string} format - 日期格式，支持YY-MM-DD hh:mm:ss
 * @return {string} - 格式化后的日期字符串
 */
export const datetimeObj2str = function(time, format = "YY-MM-DD hh:mm:ss") {
    let date = new Date(time);
    let year = date.getFullYear(),
        month = date.getMonth() + 1,
        day = date.getDate(),
        hour = date.getHours(),
        min = date.getMinutes(),
        sec = date.getSeconds();
    let preArr = Array.apply(null, Array(10)).map(function(elem, index) {
        return "0" + index;
    });

    return format
        .replace(/YY/g, preArr[year] || year)
        .replace(/MM/g, preArr[month] || month)
        .replace(/DD/g, preArr[day] || day)
        .replace(/hh/g, preArr[hour] || hour)
        .replace(/mm/g, preArr[min] || min)
        .replace(/ss/g, preArr[sec] || sec);
};

/**
 * 将时间戳转换为可读的时间格式
 * @param {Number} timestamp - 时间戳
 * @returns {String} - 可读的时间格式，例如：2022-04-12 13:30:45
 */
export const timestamp2time = function(timestamp) {
    if (!timestamp) {
        return "";
    }
    let date = new Date(timestamp * 1000);
    const Y = date.getFullYear() + "-";

    // js的月份从0开始
    const month = date.getMonth() + 1;
    const M = (month < 10 ? "0" + month : month) + "-";

    const days = date.getDate();
    const D = (days < 10 ? "0" + days : days) + " ";

    const hours = date.getHours();
    const h = (hours < 10 ? "0" + hours : hours) + ":";

    const minutes = date.getMinutes();
    const m = (minutes < 10 ? "0" + minutes : minutes) + ":";

    const seconds = date.getSeconds();
    const s = seconds < 10 ? "0" + seconds : seconds;

    return Y + M + D + h + m + s;
};
