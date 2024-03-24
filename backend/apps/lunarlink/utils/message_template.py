# -*- coding: utf-8 -*-
"""
@File    : message_template.py
@Time    : 2023/11/21 17:29
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 消息模板
"""
from typing import Dict
from django.conf import settings


def parse_message(summary: Dict, **kwargs):
    """
    解析消息模板

    :param summary: 测试报告摘要
    :param kwargs: 其他参数
    :return:
    """
    task_name = summary["task_name"]
    rows_count = summary["stat"]["testsRun"]
    pass_count = summary["stat"]["successes"]
    fail_count = summary["stat"]["failures"]
    error_count = summary["stat"]["errors"]
    duration = "%.2fs" % summary["time"]["duration"]
    report_id = summary["report_id"]
    base_url = settings.IM_REPORT_SETTING.get("base_url")
    port = settings.IM_REPORT_SETTING.get("port")
    report_url = f"{base_url}:{port}/api/lunarlink/reports/{report_id}/"
    executed = rows_count
    fail_rate = "{:.2%}".format(fail_count / executed)
    case_count = kwargs.get("case_count")

    return {
        "task_name": task_name,
        "duration": duration,
        "case_count": case_count,
        "pass_count": pass_count,
        "error_count": error_count,
        "fail_count": fail_count,
        "fail_rate": fail_rate,
        "report_url": report_url,
    }


def email_msg_template(
    task_name,
    duration,
    case_count,
    pass_count,
    error_count,
    fail_count,
    fail_rate,
    report_url,
):
    """
    定制邮件报告消息模板

    :param task_name:
    :param duration:
    :param case_count:
    :param pass_count:
    :param error_count:
    :param fail_count:
    :param fail_rate:
    :param report_url:
    :return:
    """
    email_subject = "LunarLink自动化测试报告"
    email_content = f"""<!DOCTYPE html>    
<html>    
<head>    
<meta charset="UTF-8">    
<title>LunarLink自动化测试报告</title>    
</head>    

<body leftmargin="8" marginwidth="0" topmargin="8" marginheight="4"    
    offset="0">    
    <table width="95%" cellpadding="0" cellspacing="0"  style="font-size: 11pt; font-family: Tahoma, Arial, Helvetica, sans-serif">    
        <tr>    
            本邮件由系统自动发出，无需回复！<br/>            
            各位同事，大家好，以下为LunarLink平台自动化测试报告</br>   
        </tr>    
        <tr>    
            <td><br />    
            <b><font color="#0B610B">报告信息</font></b>    
            <hr size="2" width="100%" align="center" /></td>    
        </tr>    
        <tr>    
            <td>    
                <ul>    
                    <li>任务名称: {task_name}</li>    
                    <li>总共耗时: {duration}</li>         
                    <li>用例个数: <span style="font-weight: bold;">{case_count}</span></li>
                    <li>成功接口: <span style="color: green;font-weight: bold;">{pass_count}</span></li>
                    <li>异常接口: <span style="color: red;font-weight: bold;">{error_count}</span></li>
                    <li>失败接口: <span style="color: red;font-weight: bold;">{fail_count}</span></li>
                    <li>失败比例: <span style="font-weight: bold;">{fail_rate}</span></li>
                    <li>测试报告: <a href="{report_url}">点击查看</a></li>
                </ul>    
            </td>    
        </tr>    
    </table>    
</body>    
</html>"""

    return {
        "subject": email_subject,
        "html_message": email_content,
    }


def qy_msg_template(
    task_name,
    duration,
    case_count,
    pass_count,
    error_count,
    fail_count,
    fail_rate,
    report_url,
    msg_type: str = "markdown",
):
    """
    定制企业微信消息模板

    :param task_name:
    :param duration:
    :param case_count:
    :param pass_count:
    :param error_count:
    :param fail_count:
    :param fail_rate:
    :param report_url:
    :param msg_type:
    :return:
    """
    if msg_type == "markdown":
        msg_template = {"msgtype": "markdown", "markdown": {"content": ""}}
        content = f"""<font color=\'warning\'>**LunarLink自动化测试报告**</font> \n
        >任务名称: <font color=\'comment\'>{task_name}</font>
        >总共耗时: <font color=\'comment\'>{duration}</font>
        >用例个数: <font color=\'comment\'>{case_count}</font>
        >成功接口: <font color=\'info\'>**{pass_count}**</font>
        >异常接口: <font color=\'comment\'>**{error_count}**</font>
        >失败接口: <font color=\'comment\'>**{fail_count}**</font>
        >失败比例: <font color=\'comment\'>**{fail_rate}**</font>
        >测试报告: <font color=\'comment\'>[点击查看]({report_url})</font>"""
        msg_template["markdown"]["content"] = content
        return msg_template
    text = f" 任务名称: {task_name}\n 总共耗时: {duration}\n 成功接口: {pass_count}个\n 异常接口: {error_count}个\n 失败接口: {fail_count}个\n 失败比例: {fail_rate}\n 查看详情: {report_url}"
    return text
