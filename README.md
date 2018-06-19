# py_gen_reports
> python生成报表（html，pdf）
> 作为后端接口使用
> 支持丰富的图表类型

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
	* [Windows和Mac安装wkhtmltopdf](https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf)
	  [Windows版下载地址](http://www.bkill.com/download/153533.html)
3. python export_report.py


## 前后端接口
todo。。。


## 定制化需求
可以采用不同的报告模板进行渲染，这些模板位于/templates目录下。</br>
目前只有default_template.html这一种模板。


## todo
* 增加图表类型
* 增加模板类型
* pdf导出功能
* 扩充模板类型
* 完善readme


## 问题
* 导出pdf格式的报告时报错
```
IOError: No wkhtmltopdf executable found: ""
```
当前运行环境是在Windows下，通过.exe执行文件在本机安装了wkhtmltopdf。
在export_report.py中，修改约第18行位置的**path_wk**这一参数，指向wkhtmltopdf安装位置。注意如果路径中的bin前面使用双斜杠，因为单斜杠会视为将字母b转义。
```
path_wk = r'D:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe'
```
网上说修改系统变量、保证wkhtmltopdf和python版本一致等做法，试过没有用，依旧读取不到wkhtmltopdf.exe，所以这里采用在程序中指定的方式。<font color=red>希望有更好的解决方案。</font>
