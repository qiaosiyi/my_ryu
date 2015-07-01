from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import hub
from ryu.controller import dpset
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import udp
from ryu.lib.packet import ipv4
from ryu.ofproto.ofproto_v1_3_parser import OFPExperimenter
import time
#缩进有时候是tab 有时候是空格，容易导致未知错误
class experimenter(app_manager.RyuApp):
	_CONTEXTS = {
		'dpset': dpset.DPSet,

	}
	loop = 0
	swcount = 0

	def __init__(self, *args, **kwargs):
		super(experimenter, self).__init__(*args, **kwargs)
		self.dpset = kwargs['dpset']
		self.threads.append(hub.spawn(self.main))


	def send_experimenter(self,dpid):

			print "qsy"
			print "dpset:",
			print self.dpset.get_all()
			self.loop = self.loop + 1
			print "loop =",self.loop
			print "swcount =",self.swcount
			hub.sleep(3)

	def main(self):
		waiting = 5
		print "waiting",waiting,"secconds"
		for i in range(waiting):
			hub.sleep(1)
			
		self.swcount = 0
		
		for i in self.dpset.get_all():
			self.swcount = self.swcount + 1#获取网络中交换机的个数
		
		if self.swcount == 1:
			print "There is",self.swcount,"switche in the network"
		elif self.swcount > 1:
			print "There are",self.swcount,"switches in this network"
		else:
			print "There is no switches in the network"

		print "dpid(1)=",self.dpset.get(1)#用这个函数可以得到dpid交换机对应的datapath

		print "And then...?",









