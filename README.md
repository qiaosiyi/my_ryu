# my_ryu
my SDN lab src in project my_ryu

amming at ryu route
实验环境配置
系统：
  Ubuntu12.04
  安装各种依赖包:
      #apt-get install cmake libpcap-dev libxerces-c2-dev libpcre3-dev flex bison pkg-config autoconf libtool libboost-dev g++ scons wireshark libglib2.0-dev wireshark-dev python-eventlet python-routes python-webob python-paramiko python-dev python-lxml python-pip libxml2-dev libxslt1-dev python-dev python-mysqldb vim ssh
      
  安装git:
      #apt-get install git
      #git init
      #apt-get install upgrade git
      #git init

  下载mininet:
      #git clone git://github.com/mininet/mininet
      #mininet/util/install.sh -a
      
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

  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
