# ProxyHelper

这是一款可以辅助使用代理池的脚本工具。通过ProxyHelper，我们在使用代理池时，只需要像设置普通的代理那样将代理设置为ProxyHelper监听的端口，ProxyHelper会自动帮我们随机使用代理池中的代理去访问目标机器，并且如果代理不可用，ProxyHelper会自动尝试使用其他代理，这些对使用代理的人来说都是隐式完成的。

主要实现了以下功能：

* 在本地开启代理端口，需要使用代理池的人只需要像设置普通代理那样设置为该端口即可在底层使用代理池。
* 隐式地完成代理的随机取用以及代理失效时切换其他代理，这对代理的使用者而言是无感的。
* 可配置的代理池来源。
* 支持http代理和https代理

# 关于代理池

getRandomProxy函数定义了如何获取随机的代理，只需要将这里的返回值设置为随机从代理池中取用的代理即可，返回的格式是`["xxx.xxx.xxx.xxx", xxx]`，前者是str，后者是int

默认是结合ProxyPool项目获取随机代理的代码。

# 使用

在设置好代理池之后，还需要在代码中指定当前代理的类型是http还是https，然后执行：

```python
python3 ProxyHelper.py
```

此时会开启127.0.0.1，端口为8080的代理。只需要设置代理为127.0.0.0:8080，即可实现隐式使用代理池的效果。
