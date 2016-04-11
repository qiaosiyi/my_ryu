# my_ryu
my SDN lab src in project my_ryu

amming at ryu route
实验环境配置
系统：
  Ubuntu12.04
  安装各种依赖包:
      #apt-get install cmake libpcap-dev libxerces-c2-dev libpcre3-dev flex bison pkg-config autoconf libtool libboost-dev g++ scons wireshark libglib2.0-dev wireshark-dev python-eventlet python-routes python-webob python-paramiko python-dev python-lxml python-pip libxml2-dev libxslt1-dev python-dev python-mysqldb vim ssh
      
  安装git：
  
      #apt-get install git
      
      #git init
      
      #apt-get install upgrade git
      
      #git init

  下载mininet：
  
      #git clone git://github.com/mininet/mininet
      
      #cd mininet
      
      git tag #注释 list available versions
      
      git checkout -b 2.2.0 2.2.0 #注释 or whatever version you wish to install  
                                  #We have to chose 2.2.0 to implement our lab.                  
      
      cd ..
      
      #mininet/util/install.sh -nfv
      
  下载cpqd：
  
      #git clone https://github.com/CPqD/ofsoftswitch13.git
      
      #unzip nbeesrc-jan-10-2013.zip
      
      #cd src/
      
      #cmake .
      
      #make
      
      #cp ../bin/libn*.so /usr/local/lib

      #sudo ldconfig
      
      #cp -r ../include/* /usr/include/
      
      #cd ofsoftswitch13/
      
      #./boot.sh
      
      #./configure
      
      #make
      
      #make install

  下载ryu：
      #pip install ryu
      
      ##pip装完后在/usr/local/lib/python2.7/dist-packages/ryu/里。
      
      #git clone git://github.com/osrg/ryu.git
      
      #cd ryu/
      
      #python ./setup.py install
      





实验步骤：
1.运行控制器
进入ryu/app 运行：ryu-manager xx.py
2.在mininet仿真环境下运行交换机拓扑
3.运行查看topo的py
4.使用tcpreplay -i eth xx.pcap发包测试

  
一.建立传统最短路由实验环境
1.开启Ryu控制器（3.15），其支持OpenFlow1.3协议。
	Ryu控制器安装在Ubuntu12.04（64）中。
		# cd /usr/local/lib/python2.7/dist-packages/ryu/app
		# Ryu-manager l22.py
	启动了Ryu控制器,运行l22.py的ryu app。L22的主要功能是处理packetin消息计算路由并下发流表项。

2.建立SDN交换机实验环境，使用mininet。
	Mininet软件（2.2.0）安装在Ubuntu12.04（64）中。
		打开另一个终端。
		# cd /usr/qsy/mininet
		# mn –custom ./route_topo.py –topo routetopo –controller=remote,ip=127.0.0.1,port=6633 –switch=user
		其中route_topo.py文件放在mininet目录下。route_topo.py文件在附录中给出。
	建立了拓扑并建立了H10 H11 H13 H14 它们分别连接在dpid=3、4、6、7的交换机上。H10的ip是10.0.0.6；h11的ip是10.0.0.4；h13的ip是10.0.0.6；h14的ip是10.0.0.7；本实验的路由均根据目的ip进行计算。
	此时可以看到控制器终端显示已经安装好tablemiss流表项。

  7个1表示拓扑中的7台交换机内各自有1条流表项。
	在mininet终端内打开拓扑中的两台host h10 和 h11
		Mininet> xterm h10 h11
首先在h11内向h14、h13发送流
	H11# tcpreplay –i h11-eth0 ping7_1packet.pcap
	H11# tcpreplay –i h11-eth0 ping6_1packet.pcap

  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
