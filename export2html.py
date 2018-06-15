#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ref: https://blog.csdn.net/reallocing1/article/details/51694967
# bs4: https://beautifulsoup.readthedocs.io/zh_CN/v4.4.0/index.html?highlight=insert_after
# bs4 css selector: https://www.cnblogs.com/kongzhagen/p/6472746.html
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
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
if not os.path.exists(OUTPUTS_DIR):
    os.makedirs(OUTPUTS_DIR)

highcharts_path = os.path.join(STATIC_DIR, 'highcharts-6.1.0', 'highcharts.js')
jquery_path = os.path.join(STATIC_DIR, 'jquery-1.8.3', 'jquery-1.8.3.min.js')

# https://api.hcharts.cn/highcharts#series%3Cline%3E
# https://www.hcharts.cn/docs/line-chart
line_chart_template = {
    'title': {  # 图表标题
        'text': ''
    },
    'yAxis': {  # y轴
        'title': {
            'text': ''
        }
    },
    'legend': {  # 图例
        'align': 'right',  # 右边
        'verticalAlign': 'middle',  # 居中
        'layout': 'vertical'  # 垂直排列
    },
    'series': [],  # 数据列
    'credits': {'enabled': False}
}

# https://www.hcharts.cn/docs/column-and-bar-charts
column_chart_template = {
    'chart': {'type': 'column'},
    'title': {  # 图表标题
        'text': ''
    },
    'xAxis': {
        'categories': [],
        'crosshair': True
    },
    'yAxis': {
        'min': 0,
        'title': {
            'text': ''
        }
    },
    'series': [],  # 数据列
    'credits': {'enabled': False}
}

# https://www.hcharts.cn/docs/pie-chart
pie_chart_template = {
    'title': {  # 图表标题
        'text': ''
    },
    'tooltip': {
        'headerFormat': '{series.name}<br>',
        'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'
    },
    'plotOptions': {
        'pie': {
            'allowPointSelect': True,  # 可以被选择
            'cursor': 'pointer',  # 鼠标样式
            'dataLabels': {
                'enabled': True,
                'format': '<b>{point.name}</b>: {point.percentage:.1f} %',
                'style': {
                    'color': "'(Highcharts.theme && Highcharts.theme.contrastTextColor)' || 'black'"
                }
            }
        }
    },
    'series': [],  # 数据列
    'credits': {'enabled': False}
}


def render_template(report_template, report_title, report_content):
    report_title = report_title.decode('utf-8')
    # 生成报表名
    current_time = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
    ext = '.' + report_template.split('.')[-1]
    report_name = report_title + '_' + current_time + ext
    # 读取html模板
    template_path = os.path.join(TEMPLATES_DIR, report_template)
    soup = BeautifulSoup(open(template_path), 'lxml')
    soup.html.head.title.string = report_title
    soup.select('#report-title a')[0].string = report_title
    soup.select('#report-subtitle a')[0].string = '导出时间：' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 添加jquery.js依赖
    with open(jquery_path, 'r') as jquery_js:
        line = jquery_js.readline()
        jquery_js_str = ''
        while line:
            jquery_js_str = jquery_js_str + line
            line = jquery_js.readline()
    jquery_js_tag = soup.new_tag('script', language='javascript', type='text/javascript')
    jquery_js_tag.string = jquery_js_str
    soup.html.append(jquery_js_tag)

    # 添加highcharts.js依赖
    with open(highcharts_path, 'r') as highcharts_js:
        line = highcharts_js.readline()
        highcharts_js_str = ''
        while line:
            highcharts_js_str = highcharts_js_str + line
            line = highcharts_js.readline()
    highcharts_js_tag = soup.new_tag('script', language='javascript', type='text/javascript')
    highcharts_js_tag.string = highcharts_js_str
    soup.html.append(highcharts_js_tag)

    # 插入html节点 - 报告内容: 综述
    summary = report_content.get('summary', '')
    if summary:
        subtitle_tag = soup.new_tag('span', style='color:#24A6BC;font-size:30px;font-weight:500')
        subtitle_tag.string = '综述'
        soup.select('body div.content div.report-summary')[0].insert_before(subtitle_tag)
        halving_line_tag = soup.new_tag('hr',
                                        style='height:1px;border:none;border-top:2px solid #CCCCCC;margin:10px 0;')
        soup.select('body div.content div.report-summary')[0].insert_before(halving_line_tag)
        soup.select('body div.content div.report-summary')[0].append(summary)

    # 插入html节点 - 报告内容: 图表
    charts = report_content.get('charts', [])
    if charts:
        subtitle_tag = soup.new_tag('span', style='color:#24A6BC;font-size:30px;font-weight:500;')
        subtitle_tag.string = '图表'
        soup.select('body div.content div.report-charts')[0].insert_before(subtitle_tag)
        halving_line_tag = soup.new_tag('hr',
                                        style='height:1px;border:none;border-top:2px solid #CCCCCC;margin:10px 0;')
        soup.select('body div.content div.report-charts')[0].insert_before(halving_line_tag)
        for idx, chart in enumerate(charts):
            if chart['chart_type'] == 'line_chart':
                chart_template = copy.deepcopy(line_chart_template)
                for key in chart:
                    chart_template[key] = chart[key]
            elif chart['chart_type'] == 'pie_chart':
                chart_template = copy.deepcopy(pie_chart_template)
                for key in chart:
                    chart_template[key] = chart[key]
            elif chart['chart_type'] == 'column_chart':
                chart_template = copy.deepcopy(column_chart_template)
                for key in chart:
                    chart_template[key] = chart[key]
            else:
                chart_template = copy.deepcopy(line_chart_template)
            chart_id = 'chart' + str(idx)
            # 图表dom
            chart_tag = soup.new_tag('div', id=chart_id,
                                     style='max-width:600px;height:400px;float:left;margin-bottom:20px;')
            soup.select('body div.content div.report-charts')[0].append(chart_tag)
            # 图表js
            chart_js_tag = soup.new_tag('script', language='javascript', type='text/javascript')
            chart_js_str = "var chart = Highcharts.chart('%(chart_id)s',%(chart_options)s);" % {
                'chart_id': chart_id,
                'chart_options': json.dumps(chart_template, encoding='utf-8', ensure_ascii=False)
            }
            chart_js_tag.string = chart_js_str
            soup.html.append(chart_js_tag)

    # 插入html节点 - 报告内容: 分析路径
    analysis_path = report_content.get('analysis_path', '')
    if analysis_path:
        subtitle_tag = soup.new_tag('span', style='color:#24A6BC;font-size:30px;font-weight:500')
        subtitle_tag.string = '分析路径'
        soup.select('body div.content div.report-analysis-path')[0].insert_before(subtitle_tag)
        halving_line_tag = soup.new_tag('hr',
                                        style='height:1px;border:none;border-top:2px solid #CCCCCC;margin:10px 0;')
        soup.select('body div.content div.report-analysis-path')[0].insert_before(halving_line_tag)
        soup.select('body div.content div.report-analysis-path')[0].append(analysis_path)

    # 导出报告
    export2html(report_name, soup.prettify())


def export2html(report_name, html_data):
    template_path = os.path.join(OUTPUTS_DIR, report_name)
    with open(template_path, 'wb') as html_file:
        html_file.write(html_data.encode('utf-8'))


if __name__ == "__main__":
    report_title = 'Test Report'
    # 前后端api约定的数据传递格式
    report_content = {
        'summary': '这是一份测试报告，目前支持基础折线图、基础柱状图和基础饼图的一键生成',
        'charts': [
            {
                'chart_type': 'line_chart',
                'title': {
                    'text': '第一张图表'
                },
                'yAxis': {
                    'title': {
                        'text': '就业人数'
                    }
                },
                'series': [{
                    'name': '安装，实施人员',
                    'data': [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
                }, {
                    'name': '工人',
                    'data': [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
                }, {
                    'name': '销售',
                    'data': [11744, 17722, 16005, 19771, 20185, 24377, 32147, 39387]
                }, {
                    'name': '其他',
                    'data': [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
                }]
            },
            {
                'chart_type': 'pie_chart',
                'title': {
                    'text': '各浏览器的访问量占比'
                },
                'tooltip': {
                    'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'
                },
                'series': [{
                    'type': 'pie',
                    'name': '浏览器占比',
                    'data': [
                        ['Firefox', 45.0],
                        ['IE', 26.8],
                        {
                            'name': 'Chrome',
                            'y': 12.8,
                            'sliced': True,
                            'selected': True
                        },
                        ['Safari', 8.5],
                        ['Opera', 6.2],
                        ['其他', 0.7]
                    ]
                }]
            },
            {
                'chart_type': 'column_chart',
                'chart': {
                    'type': 'column'
                },
                'title': {
                    'text': '月平均降雨量'
                },
                'xAxis': {
                    'categories': [],
                    'crosshair': True
                },
                'yAxis': {
                    'min': 0,
                    'title': {
                        'text': '降雨量 (mm)'
                    }
                },
                'series': [{
                    'name': '东京',
                    'data': [49.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4]
                }, {
                    'name': '纽约',
                    'data': [83.6, 78.8, 98.5, 93.4, 106.0, 84.5, 105.0, 104.3, 91.2, 83.5, 106.6, 92.3]
                }, {
                    'name': '伦敦',
                    'data': [48.9, 38.8, 39.3, 41.4, 47.0, 48.3, 59.0, 59.6, 52.4, 65.2, 59.3, 51.2]
                }, {
                    'name': '柏林',
                    'data': [42.4, 33.2, 34.5, 39.7, 52.6, 75.5, 57.4, 60.4, 47.6, 39.1, 46.8, 51.1]
                }]
            }
        ],
        'analysis_path': 'xxx'
    }
    render_template('template.html', report_title, report_content)
