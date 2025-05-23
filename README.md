# frmpd

`frmpd` 是由FishROS出品的多协议传输控制器调试工具&Python 驱动。



下载使用

```
pip install git+https://github.com/fishros/frmpd.git
frmpd serial /dev/ttyUSB0  921600  # 串口协议
frmpd serial udp4  8888  # 网络协议
```