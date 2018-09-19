#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from functools import reduce
import copy
import json
import datetime
from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

BASE_DIR = reduce(lambda x, y: os.path.dirname(x), range(1), os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
if not os.path.exists(OUTPUTS_DIR):
    os.makedirs(OUTPUTS_DIR)

# 风险等级分布图
risk_level_dist_chart_tpl = {
    'title': {
        'text': '风险等级分布图',
        'x': 'center'
    },
    'tooltip': {
        'trigger': 'item',
        'formatter': "{a} <br/>{b} : {c}%"
    },
    'legend': {
        'type': 'scroll',
        'selectedMode': False,
        'orient': 'vertical',
        'right': 0,
        'top': 100,
        'bottom': 'auto',
        'data': ['紧急', '高风险', '中风险', '低风险']
    },
    'label': {
        'show': True,
        'formatter': '{b}: {c}%'
    },
    'series': [
        {
            'name': '等级',
            'type': 'pie',
            'data': [
                {'name': '紧急', 'value': 0.6},
                {'name': '高风险', 'value': 16.8},
                {'name': '中风险', 'value': 45.3},
                {'name': '低风险', 'value': 37.3}
            ],
            'itemStyle': {
                'emphasis': {
                    'shadowBlur': 10,
                    'shadowOffsetX': 0,
                    'shadowColor': 'rgba(0, 0, 0, 0.5)'
                }
            }
        }
    ],
    'color': ['#E74C3C', '#F88D48', '#F9C810', '#7490C9']
}

# 各级风险统计图
risk_level_statis_chart_tpl = {
    'title': {
        'text': '各级风险统计图',
        'x': 'center'
    },
    'xAxis': {
        'type': 'category',
        'data': ['紧急', '高风险', '中风险', '低风险']
    },
    'yAxis': {
        'type': 'value'
    },
    'series': [{
        'data': [2, 54, 146, 120],
        'type': 'bar',
        'label': {
            'show': True,
            'formatter': '{c}',
            'position': 'top',
            'color': '#000'
        }
    }],
    'color': ['#37A2DA', '#E74C3C', '#F88D48', '#F9C810', '#7490C9']
}

# 扫描类型分布图
scan_type_dist_chart_tpl = {
    'title': {
        'text': '扫描类型分布图',
        'x': 'center'
    },
    'tooltip': {
        'trigger': 'item',
        'formatter': "{a} <br/>{b} : {c}%"
    },
    'legend': {
        'type': 'scroll',
        'selectedMode': False,
        'orient': 'vertical',
        'right': 0,
        'top': 100,
        'bottom': 'auto',
        'data': ['主机漏洞', 'Web漏洞', '弱密码']
    },
    'label': {
        'show': True,
        'formatter': '{b}: {c}%'
    },
    'series': [
        {
            'name': '等级',
            'type': 'pie',
            'data': [
                {'name': '主机漏洞', 'value': 53.7},
                {'name': 'Web漏洞', 'value': 40.1},
                {'name': '弱密码', 'value': 6.2}
            ],
            'itemStyle': {
                'emphasis': {
                    'shadowBlur': 10,
                    'shadowOffsetX': 0,
                    'shadowColor': 'rgba(0, 0, 0, 0.5)'
                }
            }
        }
    ],
    'color': ['#37A2DA', '#65E1E3', '#FEDB5D', '#FF9F7F']
}

# 扫描类型统计图
scan_type_statis_chart_tpl = {
    'title': {
        'text': '扫描类型统计图',
        'x': 'center'
    },
    'xAxis': {
        'type': 'category',
        'data': ['主机漏洞', 'Web漏洞', '弱密码']
    },
    'yAxis': {
        'type': 'value'
    },
    'series': [{
        'data': [173, 129, 20],
        'type': 'bar',
        'label': {
            'show': True,
            'formatter': '{c}',
            'position': 'top',
            'color': '#000'
        }
    }],
    'color': ['#37A2DA', '#E74C3C', '#F88D48', '#F9C810', '#7490C9']
}

# 主机漏洞分布图、Web漏洞分布图、弱密码分布图
vulne_dist_chart_tpl = {
    'title': {
        'text': '主机漏洞分布图',
        'x': 'center'
    },
    'xAxis': {
        'type': 'category',
        'data': ['Web服务器漏洞', 'Windows漏洞', 'MacOS漏洞']
    },
    'yAxis': {
        'type': 'value'
    },
    'series': [{
        'data': [202, 60, 0],
        'type': 'bar',
        'label': {
            'show': True,
            'formatter': '{c}',
            'position': 'top',
            'color': '#000'
        }
    }],
    'color': ['#F88D48', '#37A2DA', '#E74C3C', '#F9C810', '#7490C9']
}

# 紧急风险趋势、高风险趋势、中风险趋势、低风险趋势
risk_trend_chart_tpl = {
    'title': {
        'text': '紧急风险趋势(全网Top10)',
        'x': 'center'
    },
    'tooltip': {
        'trigger': 'axis'
    },
    'legend': {
        'bottom': 10,
        'data': ['192.168.10,1', '192.168.10.2', '192.168.10.3', '192.168.10.4']
    },
    'grid': {
        'left': '3%',
        'right': '4%',
        'bottom': '10%',
        'containLabel': True
    },
    'xAxis': {
        'type': 'category',
        'boundaryGap': False,
        'data': ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    'yAxis': {
        'type': 'value'
    },
    'series': [
        {
            'name': '192.168.10,1',
            'type': 'line',
            'stack': '总量',
            'data': [120, 132, 101, 134, 90, 230, 210]
        },
        {
            'name': '192.168.10.2',
            'type': 'line',
            'stack': '总量',
            'data': [220, 182, 191, 234, 290, 330, 310]
        },
        {
            'name': '192.168.10.3',
            'type': 'line',
            'stack': '总量',
            'data': [150, 232, 201, 154, 190, 330, 410]
        },
        {
            'name': '192.168.10.4',
            'type': 'line',
            'stack': '总量',
            'data': [320, 332, 301, 334, 390, 330, 320]
        }
    ]
}


def render_template(report_template, report_title):
    report_title = report_title.decode('utf-8')
    # 生成报表名
    current_time = datetime.datetime.now()
    report_name = report_title + '_' + current_time.strftime('%Y%m%d%H%M%S')
    # 读取html模板
    template_path = os.path.join(TEMPLATES_DIR, report_template)
    soup = BeautifulSoup(open(template_path), 'lxml')
    soup.html.head.title.string = report_title
    soup.select('#report-id')[0].string = 'XXXX-{date}-{time}'.format(date=current_time.strftime('%Y%m%d'),
                                                                         time=current_time.strftime('%H%M%S'))
    soup.select('#generate-time')[0].string = current_time.strftime('%Y-%m-%d %H:%M:%S')

    # 渲染html内容 - 1.综述
    summary = ';'
    if summary:
        soup.select('#host-count')[0].string = '10'
        soup.select('#domain-count')[0].string = '10'
        soup.select('#info-risk-count')[0].string = '10'
        soup.select('#risk-level')[0].string = '10'
        soup.select('#high-risk-count')[0].string = '10'
        soup.select('#host-vulne-count')[0].string = '10'
        soup.select('#host-vulne-pct')[0].string = '10'
        soup.select('#web-vulne-count')[0].string = '10'
        soup.select('#web-vulne-pct')[0].string = '10'
        soup.select('#weak-pwd-count1')[0].string = '10'
        soup.select('#weak-pwd-pct')[0].string = '10'
        soup.select('#high-risk-host-count')[0].string = '10'
        soup.select('#high-risk-host-pct')[0].string = '10'
        soup.select('#high-risk-domain-count')[0].string = '10'
        soup.select('#high-risk-domain-pct')[0].string = '10'
        soup.select('#high-risk-host-vulne-count')[0].string = '10'
        soup.select('#high-risk-host-vulne-pct')[0].string = '10'
        soup.select('#high-risk-web-vulne-count')[0].string = '10'
        soup.select('#high-risk-web-vulne-pct')[0].string = '10'
        soup.select('#weak-pwd-count2')[0].string = '10'
        soup.select('#host-in-weak-pwd1')[0].string = '10'

    # 插入html节点
    # 2.总体风险分析 - 风险等级分布
    risk_level_dist_chart = copy.deepcopy(risk_level_dist_chart_tpl)
    # todo...渲染risk_level_dist_chart
    _draw_chart(soup, 'risk-level-dist-chart', risk_level_dist_chart)

    risk_level_statis_chart = copy.deepcopy(risk_level_statis_chart_tpl)
    # todo...渲染risk_level_statis_chart
    _draw_chart(soup, 'risk-level-statis-chart', risk_level_statis_chart)

    # 插入html节点
    # 2.总体风险分析 - 风险类型分布
    scan_type_dist_chart = copy.deepcopy(scan_type_dist_chart_tpl)
    # todo...渲染scan_type_dist_chart
    _draw_chart(soup, 'scan-type-dist-chart', scan_type_dist_chart)

    scan_type_statis_chart = copy.deepcopy(scan_type_statis_chart_tpl)
    # todo...渲染scan_type_statis_chart
    _draw_chart(soup, 'scan-type-statis-chart', scan_type_statis_chart)

    host_vulne_dist_chart = copy.deepcopy(vulne_dist_chart_tpl)
    # todo...渲染host_vulne_dist_chart
    _draw_chart(soup, 'host-vulne-dist-chart', host_vulne_dist_chart)

    web_vulne_dist_chart = copy.deepcopy(vulne_dist_chart_tpl)
    # todo...渲染web_vulne_dist_chart
    _draw_chart(soup, 'web-vulne-dist-chart', web_vulne_dist_chart)

    weak_pwd_dist_chart = copy.deepcopy(vulne_dist_chart_tpl)
    # todo...渲染weak_pwd_dist_chart
    _draw_chart(soup, 'weak-pwd-dist-chart', weak_pwd_dist_chart)

    # 插入html节点 - 3.所有主机（IP）信息统计 - 表格
    for i in range(10):
        row = "<tr><td>{ip}</td><td>{domain_count}</td><td>{host_risk_count}</td><td>{web_risk_count}</td><td>weak_pwd_count</td><td>risk_level</td></tr>" \
            .format(ip='192.168.10.1', domain_count=10, host_risk_count=2, web_risk_count=9, weak_pwd_count=90,
                    risk_level='紧急')
        soup.select('#host-info-table')[0].append(BeautifulSoup(row, 'lxml').html.body.tr)

    # 插入html节点
    # 4.风险趋势 - 紧急风险趋势
    emerg_risk_trend_chart = copy.deepcopy(risk_trend_chart_tpl)
    # todo...渲染emerg_risk_trend_chart
    _draw_chart(soup, 'emerg-risk-trend-chart', emerg_risk_trend_chart)

    # 4.风险趋势 - 高风险趋势
    high_risk_trend_chart = copy.deepcopy(risk_trend_chart_tpl)
    # todo...渲染high_risk_trend_chart
    _draw_chart(soup, 'high-risk-trend-chart', high_risk_trend_chart)

    # 4.风险趋势 - 中风险趋势
    midium_risk_trend_chart = copy.deepcopy(risk_trend_chart_tpl)
    # todo...渲染midium_risk_trend_chart
    _draw_chart(soup, 'midium-risk-trend-chart', midium_risk_trend_chart)

    # 5.风险趋势 - 低风险趋势
    low_risk_trend_chart = copy.deepcopy(risk_trend_chart_tpl)
    # todo...渲染low_risk_trend_chart
    _draw_chart(soup, 'low-risk-trend-chart', low_risk_trend_chart)

    # 插入html节点 - 5.风险类型分析 - 表格
    # 主机风险分析
    for i in range(10):
        row = "<tr><td>{ip}</td><td>{emerg_risk_count}</td><td>{high_risk_count}</td><td>{midium_risk_count}</td><td>low_risk_count</td><td>info_count</td><td>risk_level</td></tr>" \
            .format(ip='192.168.10.1', emerg_risk_count=10, high_risk_count=2, midium_risk_count=9, low_risk_count=90,
                    info_count=88, risk_level='紧急')
        soup.select('#host-risk-table')[0].append(BeautifulSoup(row, 'lxml').html.body.tr)

    # 域名风险分析
    for i in range(10):
        row = "<tr><td>{domain}</td><td>{title}</td><td>{emerg_risk_count}</td><td>{high_risk_count}</td><td>{midium_risk_count}</td><td>low_risk_count</td><td>info_count</td><td>risk_level</td></tr>" \
            .format(domain='192.168.10.1', title='xxx', emerg_risk_count=10, high_risk_count=2, midium_risk_count=9,
                    low_risk_count=90, info_count=88, risk_level='紧急')
        soup.select('#domain-risk-table')[0].append(BeautifulSoup(row, 'lxml').html.body.tr)

    # 弱密码分析
    soup.select('#weak-pwd_count3')[0].string = '10'
    soup.select('#host-in-weak-pwd2')[0].string = '10'
    for i in range(10):
        row = "<tr><td>{ip}</td><td>{admin}</td><td>{password}</td><td>{weak_pwd_type}</td></tr>" \
            .format(ip='192.168.10.1', admin='xxx', password=10, weak_pwd_type=2)
        soup.select('#pwd-risk-table')[0].append(BeautifulSoup(row, 'lxml').html.body.tr)

    return report_name, soup.prettify()


def _draw_chart(soup, tag_id, option):
    chart_js_tag = soup.new_tag('script', language='javascript', type='text/javascript')
    chart_js_str = "echarts.init(document.getElementById('{tag_id}'), 'shine').setOption({option});".format(
        tag_id=tag_id,
        option=json.dumps(option, encoding='utf-8', ensure_ascii=False))
    chart_js_tag.string = chart_js_str
    soup.html.append(chart_js_tag)


def export2html(report_name, report_content):
    ext = '.html'
    report_path = os.path.join(OUTPUTS_DIR, report_name + ext)
    with open(report_path, 'wb') as html_file:
        html_file.write(report_content.encode('utf-8'))


if __name__ == "__main__":
    template_name = 'full_network_tpl.html'
    report_title = '全网风险趋势报告'
    report_name, report_content = render_template(template_name, report_title)
    # 导出html格式报告
    export2html(report_name, report_content)
