# UPYUN Python SDK

[![pypi package](https://badge.fury.io/py/upyun.png)](http://badge.fury.io/py/upyun) [![downloads](https://pypip.in/d/upyun/badge.png)](https://crate.io/packages/upyun/)

又拍云存储 Python SDK，基于 [又拍云存储 HTTP REST API 接口](http://wiki.upyun.com/index.php?title=HTTP_REST_API%E6%8E%A5%E5%8F%A3) 开发。

### 更新说明

1. 不再兼容 1.x 的版本，新版接口设计和实现更加 Pythonic ，且代码风格完全符合 [pep8](https://pypi.python.org/pypi/pep8) 规范。
2. 2.2.0 及以上版本同时兼容了 Python 2.6 / 2.7 / 3.3，但建议其对应修订版本号都升级到最新稳定版。

### 安装说明

> 可选依赖 [requests](https://github.com/kennethreitz/requests): HTTP for Humans，推荐！

```
pip install -r requirements.txt
```

#### 通过 pip 安装

```
pip install upyun
```

## 基本函数接口

### 初始化 UpYun

```python
import upyun

up = upyun.UpYun('bucket', 'username', 'password', timeout=30, endpoint=upyun.ED_AUTO)
```

其中，参数 `bucket` 为空间名称，`username` 和 `password` 分别为授权操作员帐号和密码，必选。

参数 `timeout` 为 HTTP 请求超时时间，默认 60 秒，可选。

以及，根据国内的网络情况，又拍云存储 API 目前提供了电信、联通网通、移动铁通三个接入点，在初始化时可由参数 `endpoint` 进行设置，其可选的值有：

```python
upyun.ED_AUTO     # 根据网络条件自动选择接入点，默认
upyun.ED_TELECOM  # 电信接入点
upyun.ED_CNC      # 联通网通接入点
upyun.ED_CTT      # 移动铁通接入点
```

默认设置为 `upyun.ED_AUTO` ， 但是我们推荐根据服务器网络状况，手动设置合理的接入点以获取最佳的访问速度。同时，也可通过：

```python
up.endpoint = upyun.ED_TELECOM
```

在对象使用过程中更改。

### 上传文件

#### 直接传递文件内容的形式上传

```python
up.put('/upyun-python-sdk/ascii.txt', 'abcdefghijklmnopqrstuvwxyz\n')
```

其中，方法 `up.put` 默认已开启相应目录的自动创建。

#### 数据流方式上传，可降低内存占用

```python
headers = { "x-gmkerl-rotate": "180"  }

with open('unix.png', 'rb') as f:
    res = up.put('/upyun-python-sdk/xinu.png', f, checksum=True, headers=headers)
```

其中，参数 `checksum` 和 `headers` 可选，前者默认 False，表示不进行 MD5 校验; 后者可根据需求设置自定义 HTTP Header，例如作图参数 x-gmkerl-*, 具体请参考 [标准 API 上传文件](http://wiki.upyun.com/index.php?title=%E6%A0%87%E5%87%86API%E4%B8%8A%E4%BC%A0%E6%96%87%E4%BB%B6) 。

上传成功，如果当前空间是图片空间，那么 `res` 返回的是一个包含图片长、宽、帧数和类型信息的 Python Dict 对象 (文件空间，返回一个空的 Dict)：

```
{'frames': '1', 'width': '1280', 'file-type': 'PNG', 'height': '800'}
```

上传失败，则抛出相应异常。

### 下载文件

#### 直接读取文件内容

```python
res = up.get('/upyun-python-sdk/ascii.txt')
```

下载成功，返回文件内容; 失败则抛出相应异常。

#### 使用数据流模式下载，节省内存占用

```python
with open('xinu.png', 'wb') as f:
    up.get('/upyun-python-sdk/xinu.png', f)
```

下载成功，返回 Python `None` 对象; 失败则抛出相应异常。

### 创建目录

```python
up.mkdir('/upyun-python-sdk/temp/')
```

创建成功，返回 Python `None` 对象; 失败则抛出相应异常。

### 删除目录或文件

```python
up.delete('/upyun-python-sdk/xinu.png')
up.delete('/upyun-python-sdk/temp/')
```

删除成功，返回 Python `None` 对象; 失败则抛出相应异常。注意删除目录时，必须保证目录为空。

### 获取目录文件列表

```python
res = up.getlist('/upyun-python-sdk/')
```

获取成功，返回一个包含该目录下所有目录或文件条目信息的 Python List 对象：

```
[{'time': '1363247311', 'type': 'F', 'name': 'temp', 'size': '0'}, {'time': '1363247311', 'type': 'N', 'name': 'xinu.png', 'size': '477908'}]
```

其中每个条目信息是又是一个 Python Dict 对象：

```python
item = res[0]
print item['name'] # 文件名称
print item['type'] # 文件类型
print item['size'] # 文件大小
print item['time'] # 创建时间
```

获取失败，则抛出相应的异常。该方法默认获取根目录列表信息。

### 获取文件信息

```python
res = up.getinfo('/upyun-python-sdk/xinu.png')
print res['file-type']
print res['file-size']
print res['file-date']
```

获取成功，返回一个 Python Dict 对象; 失败则抛出相应异常。

### 获取空间使用情况

```python
res = up.usage()
```

获取成功，始终返回该空间当前使用的总容量，单位 Bytes，值类型为 Python `String` 对象; 失败则抛出相应异常。

### 异常处理

```python
try:
    res = up.usage()

    # do something else

except upyun.UpYunServiceException as se:
    print "Except an UpYunServiceException ..."
    print "HTTP Status Code: " + str(se.status)
    print "Error Message:    " + se.msg + "\n"
except upyun.UpYunClientException as ce:
    print "Except an UpYunClientException ..."
    print "Error Message: " + ce.msg + "\n"
```

其中， `UpYunServiceException` 主要是又拍云存储端返回的错误信息，具体错误代码请参考 [标准 API 错误代码表](http://wiki.upyun.com/index.php?title=%E6%A0%87%E5%87%86API%E9%94%99%E8%AF%AF%E4%BB%A3%E7%A0%81%E8%A1%A8); 而 `UpYunClientException` 则主要是一些客户端环境的异常，例如客户端网络超时等。

## 高级特性

### 自定义数据流大小

```python
up = upyun.UpYun('bucket', 'username', 'password', chunksize=8192)
```

当通过数据流方式上传和下载文件时，`chunksize` 决定了每次读操作的缓存区大小，默认 8192 字节。

### 自定义文件上传和下载过程

> 例如，通过如下代码可以很容易实现上传下载的进度条显示：

```python
from progressbar import *

class ProgressBarHandler(object):
    def __init__(self, totalsize, params):
        widgets = [params, Percentage(), ' ',
                   Bar(marker='=', left='[', right=']'), ' ',
                   ETA(), ' ', FileTransferSpeed()]
        self.pbar = ProgressBar(widgets=widgets, maxval=totalsize).start()

    def update(self, readsofar):
        self.pbar.update(readsofar)

    def finish(self):
        self.pbar.finish()

with open('unix.png', 'rb') as f:
    res = up.put('xinu.png', f, handler=ProgressBarHandler, params="Uploading ")

with open('xinu.png', 'wb') as f:
    up.get('xinu.png', f, handler=ProgressBarHandler, params="Downloading ")
```

## 其他说明

具体请参考 `demo/try.py` 的代码，建议可在修改以下代码后直接运行该脚本，观察其输出情况，以便对整个 Python SDK 接口有个大致的了解：

```python
# ------------------ CONFIG ---------------------
BUCKETNAME = 'bucketname'
USERNAME = 'username'
PASSWORD = 'password'
# -----------------------------------------------
```
