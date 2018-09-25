# py_gen_reports
> python生成报表（html，pdf）
> 作为后端接口使用
> 支持丰富的图表类型


## 适用场景
* 测试数据结果统计
* 业务系统报表
* 历史数据分析
* 其它


## 调用环境
* python2.7
* pip 9.0.1以上


## 演示步骤
1. 安装pip依赖包
	```
	pip install -r requirements.txt
	```
2. 安装wkhtmltopdf
	* Linux环境
	```
	Debian/Ubuntu: 
		sudo apt-get install wkhtmltopdf
	Redhat/CentOS:
		sudo yum intsall wkhtmltopdf
	```
	* [Windows和Mac安装wkhtmltopdf](https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf)</br>
	  [Windows版下载地址](http://www.bkill.com/download/153533.html)
3. python export_report.py
	* 导出为html
	![image](https://github.com/xwenyuan/py_gen_reports/blob/master/screenshots/html_report.gif)
	* 导出为pdf
	![image](https://github.com/xwenyuan/py_gen_reports/blob/master/screenshots/pdf_report.gif)


## 定制化需求
可以采用不同的报告模板进行渲染，这些模板位于/templates目录下。</br>
目前：
* 有一个demo模板，使用highcharts作图
* 一个实际案例报表，使用echarts作图


## 问题
* 导出pdf格式的报告时报错
```
IOError: No wkhtmltopdf executable found: ""
```
当前运行环境是在Windows下，通过.exe执行文件在本机安装了wkhtmltopdf。
在export_report.py中，修改约第19行位置的**path_wk**这一参数，指向wkhtmltopdf安装位置。注意如果路径中的bin前面使用双斜杠，因为单斜杠会视为将字母b转义。
```
path_wk = r'D:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe'
```
网上说修改系统变量、保证wkhtmltopdf和python版本一致等做法，试过没有用，依旧读取不到wkhtmltopdf.exe，所以这里采用在程序中指定的方式。<font color=red>希望有更好的解决方案。</font>
