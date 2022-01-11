# ESP32-Arduino-HighSpeed-Encoder-Reader
使用ESP32编写的旋转编码器读值-上传数据通讯的项目。可以在极短的时间内0.1ms采样数据，并周期性上传一定数量的数据。

使用了ESP32的硬件脉冲计数器模块pcnt进行计数，精确到80MHz。

同时使用硬件时钟进行定时采样存储。

附带了一个上位机代码，展示了如何解码数据并以示波器的形式展示。
![image](https://user-images.githubusercontent.com/58870893/148884687-7368cae5-f25e-4bf2-960c-1b5910d7d847.png)

【注意】串口信息请提前在config.json中设置，再运行代码。
