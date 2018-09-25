#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from functools import reduce
import chardet
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
        'formatter': "{a} <br/>{b} : {c} ({d}%)"
    },
    'legend': {
        'type': 'scroll',
        'selectedMode': False,
        'orient': 'vertical',
        'right': 0,
        'top': 0,
        'bottom': 'auto',
        'data': ['紧急', '高风险', '中风险', '低风险']
    },
    'label': {
        'show': True,
        'formatter': '{b}: {d}%'
    },
    'series': [
        {
            'name': '等级',
            'type': 'pie',
            'data': [
                {'name': '紧急', 'value': 2},
                {'name': '高风险', 'value': 54},
                {'name': '中风险', 'value': 146},
                {'name': '低风险', 'value': 120}
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
    'tooltip': {
        'trigger': 'axis',
        'axisPointer': {
            'type': 'shadow'
        }
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
        'formatter': "{a} <br/>{b} : {c} ({d}%)"
    },
    'legend': {
        'type': 'scroll',
        'selectedMode': False,
        'orient': 'vertical',
        'right': 0,
        'top': 0,
        'bottom': 'auto',
        'data': ['主机漏洞', 'Web漏洞', '弱密码']
    },
    'label': {
        'show': True,
        'formatter': '{b}: {d}%'
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
    'tooltip': {
        'trigger': 'axis',
        'axisPointer': {
            'type': 'shadow'
        }
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

# 主机漏洞统计图、Web漏洞统计图、弱密码统计图
vul_statis_chart_tpl = {
    'title': {
        'text': '主机漏洞分布图',
        'x': 'center'
    },
    'tooltip': {
        'trigger': 'axis',
        'axisPointer': {
            'type': 'shadow'
        }
    },
    'grid': {
        'width': '80%',
        'height': '60%',
        'top': 50,
        'bottom': 20,
    },
    'xAxis': {
        'type': 'category',
        'axisLabel': {
            'interval': 0,
            'rotate': 45,
            'margin': 2,
            'textStyle': {
                'color': '#222'
            }
        },
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
        'orient': 'vertical',
        'right': 0,
        'top': 50,
        'data': ['192.168.10,1', '192.168.10.2', '192.168.10.3', '192.168.10.4']
    },
    'grid': {
        'width': '80%',
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


def render_template(report_template, report_title, report_data):
    report_title = report_title.decode('utf-8')
    # 生成报表名
    current_time = datetime.datetime.now()
    report_name = report_title + '_' + current_time.strftime('%Y%m%d%H%M%S')
    # 读取html模板
    template_path = os.path.join(TEMPLATES_DIR, report_template)
    soup = BeautifulSoup(open(template_path), 'lxml', from_encoding='utf-8')
    soup.html.head.title.string = report_title
    soup.select('#report-id')[0].string = 'Hibitom-{date}-{time}'.format(date=current_time.strftime('%Y%m%d'),
                                                                         time=current_time.strftime('%H%M%S'))
    soup.select('#generate-time')[0].string = current_time.strftime('%Y-%m-%d %H:%M:%S')

    # 渲染html内容 - 1.综述
    summary = report_data.get('summary', {})
    if summary:
        soup.select('#machine-count')[0].string = summary.get('machine_count')  # 主机总数
        soup.select('#host-count')[0].string = summary.get('host_count')  # 域名总数
        soup.select('#risk-count')[0].string = summary.get('risk_count')  # 风险总数
        soup.select('#info-count')[0].string = summary.get('info_count')  # 信息级风险总数
        soup.select('#risk-level')[0].string = summary.get('level')  # 安全风险总评级
        soup.select('#high-crit-count')[0].string = summary.get('high_crit_count')  # 高风险及以上风险总数
        soup.select('#high-crit-hostvul-count1')[0].string = summary.get('high_crit_hostvul_count')  # 高风险及以上主机漏洞
        soup.select('#high-crit-hostvul-pct-in-risk')[0].string = summary.get(
            'high_crit_hostvul_pct_in_risk')  # 占风险总数百分比
        soup.select('#high-crit-webvul-count1')[0].string = summary.get('high_crit_webvul_count')  # 高风险及以上web漏洞
        soup.select('#high-crit-webvul-pct-in-risk')[0].string = summary.get('high_crit_webvul_pct_in_risk')  # 占风险总数百分比
        soup.select('#weakpwdvul-count1')[0].string = summary.get('weakpwdvul_count')  # 弱密码
        soup.select('#weakpwdvul-pct-in-risk')[0].string = summary.get('weakpwdvul_pct_in_risk')  # 占风险总数百分比
        soup.select('#machine-in-high')[0].string = summary.get('machine_in_high')  # 包含高风险漏洞的主机
        soup.select('#machine-in-high-pct')[0].string = summary.get('machine_in_high_pct')  # 占主机总数百分比
        soup.select('#host-in-high')[0].string = summary.get('host_in_high')  # 包含高风险漏洞的域名
        soup.select('#host-in-high-pct')[0].string = summary.get('host_in_high_pct')  # 占域名总数百分比
        soup.select('#high-crit-hostvul-count2')[0].string = summary.get('high_crit_hostvul_count')  # 高风险及以上主机漏洞
        soup.select('#high-crit-hostvul-pct-in-hostvul')[0].string = summary.get(
            'high_crit_hostvul_pct_in_hostvul')  # 占主机漏洞总数百分比
        soup.select('#high-crit-webvul-count2')[0].string = summary.get('high_crit_webvul_count')  # 高风险及以上web漏洞
        soup.select('#high-crit-webvul-pct-in-webvul')[0].string = summary.get(
            'high_crit_webvul_pct_in_webvul')  # 占web漏洞总数百分比
        soup.select('#weakpwdvul-count2')[0].string = summary.get('weakpwdvul_count')  # 弱密码总数
        soup.select('#machine-in-weakpwdvul1')[0].string = summary.get('machine_in_weakpwdvul')  # 影响主机

    # 插入html节点
    overall_risk_analysis = report_data.get('overall_risk_analysis', {})
    # 2.总体风险分析 - 风险等级分布
    level_data = overall_risk_analysis.get('level_data', [])
    if level_data:
        risk_level_dist_chart = copy.deepcopy(risk_level_dist_chart_tpl)
        # 渲染
        risk_level_dist_chart['legend']['data'] = [level['name'] for level in level_data]
        risk_level_dist_chart['series'][0]['data'] = level_data
        _draw_chart(soup, 'risk-level-dist-chart', risk_level_dist_chart)

        risk_level_statis_chart = copy.deepcopy(risk_level_statis_chart_tpl)
        # 渲染
        risk_level_statis_chart['series'][0]['data'] = [level['value'] for level in level_data]
        _draw_chart(soup, 'risk-level-statis-chart', risk_level_statis_chart)

    # 插入html节点
    # 2.总体风险分析 - 风险类型分布
    vul_type_data = overall_risk_analysis.get('vul_type_data', [])
    if vul_type_data:
        scan_type_dist_chart = copy.deepcopy(scan_type_dist_chart_tpl)
        # 渲染
        scan_type_dist_chart['legend']['data'] = [vul_type['name'] for vul_type in vul_type_data]
        scan_type_dist_chart['series'][0]['data'] = vul_type_data
        _draw_chart(soup, 'scan-type-dist-chart', scan_type_dist_chart)

        scan_type_statis_chart = copy.deepcopy(scan_type_statis_chart_tpl)
        # 渲染
        scan_type_statis_chart['xAxis']['data'] = [vul_type['name'] for vul_type in vul_type_data]
        scan_type_statis_chart['series'][0]['data'] = [vul_type['value'] for vul_type in vul_type_data]
        _draw_chart(soup, 'scan-type-statis-chart', scan_type_statis_chart)

    hostvul_data = overall_risk_analysis.get('hostvul_data', [])
    if hostvul_data:
        hostvul_statis_chart = copy.deepcopy(vul_statis_chart_tpl)
        # 渲染
        hostvul_statis_chart['title']['text'] = '主机漏洞统计图'
        hostvul_statis_chart['xAxis']['data'] = [hostvul['name'] for hostvul in hostvul_data]
        hostvul_statis_chart['series'][0]['data'] = [hostvul['value'] for hostvul in hostvul_data]
        _draw_chart(soup, 'hostvul-statis-chart', hostvul_statis_chart)

    webvul_data = overall_risk_analysis.get('webvul_data', [])
    if webvul_data:
        webvul_statis_chart = copy.deepcopy(vul_statis_chart_tpl)
        # 渲染
        webvul_statis_chart['title']['text'] = 'Web漏洞统计图'
        webvul_statis_chart['xAxis']['data'] = [webvul['name'] for webvul in webvul_data]
        webvul_statis_chart['series'][0]['data'] = [webvul['value'] for webvul in webvul_data]
        _draw_chart(soup, 'webvul-statis-chart', webvul_statis_chart)

    weakpwdvul_data = overall_risk_analysis.get('weakpwdvul_data', [])
    if weakpwdvul_data:
        weakpwdvul_statis_chart = copy.deepcopy(vul_statis_chart_tpl)
        # 渲染
        weakpwdvul_statis_chart['title']['text'] = '弱密码统计图'
        weakpwdvul_statis_chart['xAxis']['data'] = [weakpwdvul['name'] for weakpwdvul in weakpwdvul_data]
        weakpwdvul_statis_chart['series'][0]['data'] = [weakpwdvul['value'] for weakpwdvul in weakpwdvul_data]
        _draw_chart(soup, 'weakpwdvul-statis-chart', weakpwdvul_statis_chart)

    # 插入html节点 - 3.所有主机（IP）信息统计 - 表格
    all_machine_info = report_data.get('all_machine_info', [])
    for machine_info in all_machine_info:
        row = "<tr><td>{machine_ip}</td><td>{host_count}</td><td>{hostvul_count}</td><td>{webvul_count}</td><td>{weakpwdvul_count}</td><td>{level}</td></tr>" \
            .format(machine_ip=machine_info['machine_ip'], host_count=machine_info['host_count'],
                    hostvul_count=machine_info['hostvul_count'], webvul_count=machine_info['webvul_count'],
                    weakpwdvul_count=machine_info['weakpwdvul_count'], level=machine_info['level'])
        soup.select('#machine-info-table')[0].append(BeautifulSoup(row, 'lxml', from_encoding='utf-8').html.body.tr)

    # 插入html节点
    risk_trend = report_data.get('risk_trend', [])
    # 4.风险趋势 - 紧急风险趋势
    crit_trend = filter(lambda risk: risk['level'] == 'CRIT', risk_trend)
    if crit_trend:
        crit_trend = crit_trend[0]
        crit_risk_trend_chart = copy.deepcopy(risk_trend_chart_tpl)
        # 渲染
        trend_data = crit_trend.get('trend_data', [])
        ip_list = []
        series = []
        for each_ip_trend in trend_data:
            machine_ip = each_ip_trend['machine_ip']
            ip_list.append(machine_ip)
            series.append({
                'name': machine_ip,
                'type': 'line',
                'stack': '总量',
                'data': each_ip_trend['timeline_data']
            })
        crit_risk_trend_chart['title']['text'] = '紧急风险趋势(全网Top10)'
        crit_risk_trend_chart['xAxis']['data'] = crit_trend.get('timeline', [])
        crit_risk_trend_chart['legend']['data'] = list(set(ip_list))
        crit_risk_trend_chart['series'] = series
        _draw_chart(soup, 'crit-risk-trend-chart', crit_risk_trend_chart)

    # 4.风险趋势 - 高风险趋势
    high_trend = filter(lambda risk: risk['level'] == 'HIGH', risk_trend)
    if high_trend:
        high_trend = high_trend[0]
        high_risk_trend_chart = copy.deepcopy(risk_trend_chart_tpl)
        # 渲染
        trend_data = high_trend.get('trend_data', [])
        ip_list = []
        series = []
        for each_ip_trend in trend_data:
            machine_ip = each_ip_trend['machine_ip']
            ip_list.append(machine_ip)
            series.append({
                'name': machine_ip,
                'type': 'line',
                'stack': '总量',
                'data': each_ip_trend['timeline_data']
            })
        high_risk_trend_chart['title']['text'] = '高风险趋势(全网Top10)'
        high_risk_trend_chart['xAxis']['data'] = high_trend.get('timeline', [])
        high_risk_trend_chart['legend']['data'] = list(set(ip_list))
        high_risk_trend_chart['series'] = series
        _draw_chart(soup, 'high-risk-trend-chart', high_risk_trend_chart)

    # 4.风险趋势 - 中风险趋势
    med_trend = filter(lambda risk: risk['level'] == 'MED', risk_trend)
    if med_trend:
        med_trend = med_trend[0]
        med_risk_trend_chart = copy.deepcopy(risk_trend_chart_tpl)
        # 渲染
        trend_data = med_trend.get('trend_data', [])
        ip_list = []
        series = []
        for each_ip_trend in trend_data:
            machine_ip = each_ip_trend['machine_ip']
            ip_list.append(machine_ip)
            series.append({
                'name': machine_ip,
                'type': 'line',
                'stack': '总量',
                'data': each_ip_trend['timeline_data']
            })
        med_risk_trend_chart['title']['text'] = '中风险趋势(全网Top10)'
        med_risk_trend_chart['xAxis']['data'] = med_trend.get('timeline', [])
        med_risk_trend_chart['legend']['data'] = list(set(ip_list))
        med_risk_trend_chart['series'] = series
        _draw_chart(soup, 'med-risk-trend-chart', med_risk_trend_chart)

    # 5.风险趋势 - 低风险趋势
    low_trend = filter(lambda risk: risk['level'] == 'LOW', risk_trend)
    if low_trend:
        low_trend = low_trend[0]
        low_risk_trend_chart = copy.deepcopy(risk_trend_chart_tpl)
        # 渲染
        trend_data = low_trend.get('trend_data', [])
        ip_list = []
        series = []
        for each_ip_trend in trend_data:
            machine_ip = each_ip_trend['machine_ip']
            ip_list.append(machine_ip)
            series.append({
                'name': machine_ip,
                'type': 'line',
                'stack': '总量',
                'data': each_ip_trend['timeline_data']
            })
        low_risk_trend_chart['title']['text'] = '低风险趋势(全网Top10)'
        low_risk_trend_chart['xAxis']['data'] = low_trend.get('timeline', [])
        low_risk_trend_chart['legend']['data'] = list(set(ip_list))
        low_risk_trend_chart['series'] = series
        _draw_chart(soup, 'low-risk-trend-chart', low_risk_trend_chart)

    # 插入html节点 - 5.风险类型分析 - 表格
    risk_type_analysis = report_data.get('risk_type_analysis', {})
    # 主机风险分析
    machine_risk_analysis = risk_type_analysis.get('machine_risk_analysis', []) if risk_type_analysis else []
    for each_machine in machine_risk_analysis:
        row = "<tr><td>{machine_ip}</td><td>{crit_level_count}</td><td>{high_level_count}</td><td>{med_level_count}</td><td>{low_level_count}</td><td>{info_level_count}</td><td>{level}</td></tr>" \
            .format(machine_ip=each_machine['machine_ip'], crit_level_count=each_machine['crit_level_count'],
                    high_level_count=each_machine['high_level_count'],
                    med_level_count=each_machine['med_level_count'], low_level_count=each_machine['low_level_count'],
                    info_level_count=each_machine['info_level_count'], level=each_machine['level'])
        soup.select('#machine-risk-table')[0].append(BeautifulSoup(row, 'lxml', from_encoding='utf-8').html.body.tr)

    # 域名风险分析
    hosts_risk_analysis = risk_type_analysis.get('hosts_risk_analysis', []) if risk_type_analysis else []
    for each_host in hosts_risk_analysis:
        row = "<tr><td>{host_name}</td><td>{crit_level_count}</td><td>{high_level_count}</td><td>{med_level_count}</td><td>{low_level_count}</td><td>{info_level_count}</td><td>{level}</td></tr>" \
            .format(host_name=each_host['host_name'], crit_level_count=each_host['crit_level_count'],
                    high_level_count=each_host['high_level_count'], med_level_count=each_host['med_level_count'],
                    low_level_count=each_host['low_level_count'], info_level_count=each_host['info_level_count'],
                    level=each_host['level'])
        soup.select('#host-risk-table')[0].append(BeautifulSoup(row, 'lxml', from_encoding='utf-8').html.body.tr)

    # 弱密码分析
    soup.select('#weakpwdvul-count3')[0].string = risk_type_analysis.get('weakpwdvul_count', '0') if risk_type_analysis else '无数据'
    soup.select('#machine-in-weakpwdvul2')[0].string = risk_type_analysis.get('machine_in_weakpwdvul', '0') if risk_type_analysis else '无数据'
    weakpwdvul_analysis = risk_type_analysis.get('weakpwdvul_analysis', []) if risk_type_analysis else []
    for each_weakpwdvul in weakpwdvul_analysis:
        row = "<tr><td>{machine_ip}</td><td>{username}</td><td>{password}</td><td>{type}</td></tr>" \
            .format(machine_ip=each_weakpwdvul['machine_ip'], username=each_weakpwdvul['username'],
                    password=each_weakpwdvul['password'], type=each_weakpwdvul['type'])
        soup.select('#pwd-risk-table')[0].append(BeautifulSoup(row, 'lxml', from_encoding='utf-8').html.body.tr)

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
    print(os.path.join(OUTPUTS_DIR, report_name + ext).encode('utf-8'))
    report_path = os.path.join(OUTPUTS_DIR, report_name + ext).encode('utf-8')
    with open(report_path, 'wb') as html_file:
        html_file.write(report_content.encode('utf-8'))


if __name__ == "__main__":
    template_name = 'whole_tpl.html'
    report_title = '全网风险趋势报告'
    report_data = {}
    with open(os.path.join(BASE_DIR, 'data', 'whole_data.json'), 'r') as load_f:
        report_data = json.load(load_f)
    report_name, report_content = render_template(template_name, report_title, report_data)
    # 导出html格式报告
    export2html(report_name, report_content)
