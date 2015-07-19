# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
from ryu.lib.packet import arp
from ryu.ofproto.ofproto_v1_3_parser import OFPExperimenter
import time



class experimenter(app_manager.RyuApp):
	_CONTEXTS = {
		'dpset': dpset.DPSet,

	}
	loop = 0
	swcount = 0
	dpid_datapath={(1):[]}
	dpidlib=[]
	conterflow = [0]*7
	linkports={(1,2):(3),(2,1):(3),
				(1,3):(2),(3,1):(2),
				(3,4):(1),(4,3):(3),
				(2,4):(1),(4,2):(2),
				(2,5):(2),(5,2):(4),
				(4,5):(1),(5,4):(1),
				(5,6):(3),(6,5):(2),
				(6,7):(1),(7,6):(2),
				(5,7):(2),(7,5):(3),
	}
	hostports={ '10.0.0.1':[1,1],
				'10.0.0.2':[2,4],
				'10.0.0.3':[3,3],
				'10.0.0.4':[4,4],
				'10.0.0.5':[5,5],
				'10.0.0.6':[6,3],
				'10.0.0.7':[7,1],
				'10.0.0.8':[7,4],
				}
	graph=[
			[0,1,1 ,99,99,99,99],
			[1,0,99,1,1,99,99],
			[1,99,0,1,99,99,99],
			[99,1,1,0,1,99,99],
			[99,1,99,1,0,1,1],
			[99,99,99,99,1,0,1],
			[99,99,99,99,1,1,0]
		]			
	
	def __init__(self, *args, **kwargs):
		super(experimenter, self).__init__(*args, **kwargs)
		self.dpset = kwargs['dpset']
		#self.threads.append(hub.spawn(self.main))

	def addWord(self,theIndex,word,pagenumber): 
		theIndex.setdefault(word, [ ]).append(pagenumber)
	# def numtochar(self,lie):

	def add_flow(self, datapath, priority, match, actions, buffer_id=None):
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
		if buffer_id:
			mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
									priority=priority, match=match,
									instructions=inst)
		else:
			mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
									match=match, instructions=inst)
		datapath.send_msg(mod)
		print "sending flowentry to dp:",datapath.id##qsy
		self.conterflow[datapath.id-1] = self.conterflow[datapath.id-1] +1

	def send_experimenter(self,dpid,exp_type,data):

		# enum qsy_type {##########exp_type
		#   QXT_ENABLE=1,			
		# 	QXT_ACT_SET_CONFIG=2,
		# 	QXT_DISABLE=3
		#  };
		####################
		# struct qx_config{
		# 	struct qsy_header qxh;
		# 	//uint32_t neighbor;
		# 	//uint16_t neighbor_table_utilization[PORTNUM][TTPORTNUM*2];	
		#     uint16_t neighbor_table_utilization[8][18];
		# };
		# OFP_ASSERT(sizeof(struct qx_config) == (304));///34
		#time.ctime() Sat Jul  4 11:05:31 2015
		experimenter = 0x00900305
		datapath = self.dpid_datapath[(dpid)][0]
		if exp_type == 1:
			enumtype = "QXT_ENABLE"
		elif exp_type == 2:
			enumtype = "QXT_ACT_SET_CONFIG"
		elif exp_type == 3:
			enumtype = "QXT_DISABLE"
		print "|",time.ctime()[11:19],"| Send a",enumtype,"exp_message to dpid(",dpid,")"
		
		if exp_type == 1:
			if len(data) == 4:
				ofp = datapath.ofproto
				ofp_parser = datapath.ofproto_parser
				req = ofp_parser.OFPExperimenter(datapath, experimenter, exp_type, data)
				datapath.send_msg(req)
			else:
				print "send ",enumtype," has wrong len(",len(data),")  Should be 4."
		elif exp_type == 2:
			if len(data) == 864:
				ofp = datapath.ofproto
				ofp_parser = datapath.ofproto_parser
				req = ofp_parser.OFPExperimenter(datapath, experimenter, exp_type, data)
				datapath.send_msg(req)		
			else:
				print "data:",data,"has wrong len(",len(data),")  Should be 720."
		elif exp_type == 3:
			if len(data) == 4:
				ofp = datapath.ofproto
				ofp_parser = datapath.ofproto_parser
				req = ofp_parser.OFPExperimenter(datapath, experimenter, exp_type, data)
				datapath.send_msg(req)		
			else:
				print "data:",data,"has wrong len(",len(data),")  Should be 4."
	def dijkstra(self,k,e):
		k=k-1
		e=e-1

		n=len(self.graph[0])
		dis=[0]*n  
		flag=[False]*n
		pre=[k]*n
		flag[k]=True
		start=k
		listpro=[]
		for i in range(n):
			listpro.append([i])
		for i in range(n):
			dis[i]=self.graph[k][i]
		for j in range(n-1):
			mini=99
			for i in range(n):
				if dis[i]<mini and not flag[i]:
					mini=dis[i]
					k=i

			flag[k]=True
			for i in range(n):
				if dis[i]>dis[k]+self.graph[k][i]:
					dis[i]=dis[k]+self.graph[k][i]
					pre[i]=k
		for i in range(n):
			listpro[i].append(pre[i])
		for i in range(n):
			for j in range(n):
				if listpro[j][-1] != start:
					listpro[j].append(listpro[listpro[j][-1]][1])
		for i in range(n):
			listpro[i].reverse()
		for i in range(len(listpro[e])):
			listpro[e][i]=listpro[e][i] + 1
		return listpro[e]			

	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		datapath = ev.msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		print "Adding a dpid:",datapath.id,datapath#,self.dpid_datapath[(datapath.id)]
		# if len(self.dpid_datapath[datapath.id]) == 0:
		self.addWord(self.dpid_datapath,datapath.id,datapath)
		self.dpidlib.append(datapath.id)
		# install table-miss flow entry
		#
		# We specify NO BUFFER to max_len of the output action due to
		# OVS bug. At this moment, if we specify a lesser number, e.g.,
		# 128, OVS will send Packet-In with invalid buffer_id and
		# truncated packet data. In that case, we cannot output packets
		# correctly.  The bug has been fixed in OVS v2.1.0.
		match = parser.OFPMatch()
		actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
						ofproto.OFPCML_NO_BUFFER)]
		self.add_flow(datapath, 15, match, actions)
		print "Install table-miss flow entry to dp:",datapath.id,time.ctime()
		print
		## No table miss entry
		# print self.conterflow
		###################################################
		# enum qsy_type {
		#     QXT_ENABLE=1,
		# 	//QXT_ENABLE_GOOD,
			
		# 	QXT_ACT_SET_CONFIG,
		# 	//QXT_ACT_SET_CONFIG_GOOD,
			
		# 	QXT_DISABLE,
		# 	//QXT_DISABLE_GOOD
		#  };
		###################################################
	
	@set_ev_cls(ofp_event.EventOFPPacketIn,MAIN_DISPATCHER)
	def packet_in_handler(self,ev):
		
		if ev.msg.msg_len < ev.msg.total_len:
			self.logger.debug("packet truncated: only %s of %s bytes",
								ev.msg.msg_len, ev.msg.total_len)
		msg = ev.msg
		datapath = msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		in_port = msg.match['in_port']
		# print "in_port:",in_port,
		pkt = packet.Packet(msg.data)

		eth_type = pkt.get_protocols(ethernet.ethernet)[0].ethertype
		arp_pkt = pkt.get_protocol(arp.arp)
		ip_pkt = pkt.get_protocol(ipv4.ipv4)



		# print "===Dpid:",datapath.id,"ryu get a packet in",time.ctime(),
		if arp_pkt:
			print "an arp packet",
			print "===Dpid:",datapath.id,"ryu get a packet in",time.ctime(),
			# arp_src_ip = arp_pkt.src_ip
			arp_dst_ip = arp_pkt.dst_ip
			print "arp_pkt_dst_ip is",arp_dst_ip
			switch_dst,switch_port_dst=self.hostports[arp_dst_ip]
			print "switch_dst is",switch_dst,"switch_port_dst is",switch_port_dst
			datapath_obj = self.dpid_datapath[(switch_dst)][0]
			print "out dpid is",datapath_obj.id
			actions = [parser.OFPActionOutput(switch_port_dst)]
			data = msg.data
			out = parser.OFPPacketOut(
				datapath=datapath_obj,
				buffer_id=ofproto.OFP_NO_BUFFER,
				in_port=ofproto.OFPP_CONTROLLER,
				actions=actions,
				data=data)
			datapath_obj.send_msg(out)
			print "send out"


		elif ip_pkt:
			print "an ip packet",
			print "===Dpid:",datapath.id,"ryu get a packet in",time.ctime()
			
			ipv4_hdr = pkt.get_protocols(ipv4.ipv4)[0]
			unknown_dst=pkt.get_protocols(ipv4.ipv4)[0].dst#'10.0.0.2'
			switch_dst,switch_port_dst=self.hostports[unknown_dst]
			switch_src = datapath.id
			#print "switch_src=",switch_src,"switch_dst=",switch_dst
			route=self.dijkstra(switch_src,switch_dst)
			for i in range(len(route)-1):
				outport = self.linkports[(route[i],route[i+1])]
				# print "routedoutport=",outport
				actions = [parser.OFPActionOutput(outport)]
				match = parser.OFPMatch(ipv4_dst=unknown_dst,eth_type=0x0800)
				datapath_obj = self.dpid_datapath[(route[i])][0]
				# print "datapath_obj=",self.dpid_datapath[(route[i])][0]
				self.add_flow(datapath_obj,16, match, actions)
			swdst,swportdst = self.hostports[unknown_dst]
			outport = swportdst
			actions = [parser.OFPActionOutput(outport)]
			match = parser.OFPMatch(ipv4_dst=unknown_dst,eth_type=0x0800)
			datapath_obj = self.dpid_datapath[(swdst)][0]
			self.add_flow(datapath_obj,16, match, actions)
            # print swdst,swportdst
            # print
            #for i in range(len())

			print "flowentry Num in each SDNSwitchs",self.conterflow
			firstpktoutport=self.linkports[(route[0],route[1])]
			actions = [parser.OFPActionOutput(firstpktoutport)]
			out = parser.OFPPacketOut(
			datapath=datapath,
			buffer_id=msg.buffer_id,
			in_port=in_port,
			actions=actions)
			time.sleep(0.5)
			datapath.send_msg(out)
			pass

		else:

			# print ""
			pass



