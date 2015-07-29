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
	minithresh=60
	maxthresh=100
	pmin=0.1
	pmax=0.9

	loop = 0
	swcount = 0
	dpid_datapath={(1):[]}
	dpidlib=[]
	activeFlows=[]
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
	hostports={ '10.0.0.1':[1,1],#host ip -> dpid,port
				'10.0.0.2':[2,4],
				'10.0.0.3':[3,3],
				'10.0.0.4':[4,4],
				'10.0.0.5':[5,5],
				'10.0.0.6':[6,3],
				'10.0.0.7':[7,1],
				'10.0.0.8':[7,4],
				}

	hosts_port={(1):[1],#dpid->port link to host
				(2):[4],
				(3):[3],
				(4):[4],
				(5):[5],
				(6):[3],
				(7):[1,4]
	}
	toto_entry_num={
	(1):10,
	(2):10,
	(3):10,
	(4):10,
	(5):10,
	(6):10,
	(7):10
	}

	# entry_mun=[100,200,300,400,500,600,700]

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
		# self.threads.append(hub.spawn(self.main))
		self.threads.append(hub.spawn(self.send_table_stats_request))
		self.threads.append(hub.spawn(self.exp_main))

	def addWord(self,theIndex,word,pagenumber): 
		theIndex.setdefault(word, [ ]).append(pagenumber)
	# def numtochar(self,lie):

	def P_spread(self, t):#t is entry num,p is P of spread
		if t>self.minithresh:
			if t<self.maxthresh:
				p=self.pmax*(t-self.minithresh)/(self.maxthresh-self.minithresh)+self.pmin
			else:
				p=1
		else:
			p=0
		return p

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

	def mun_to_6str(self,mun):
		
		str0={	(1):"0",
				(2):"00",
				(3):"000",
				(4):"0000",
				(5):"00000",
				(6):"000000"}
		if mun < 0:
			mun = 0
		mun = int(mun)
		string=str(mun)
		# int(string)
		# string=str(mun)
		if len(string)>3:
			if string[-2]=='.':
				string=string[:-2]
		if len(string)<6:
			string = str0[(6-len(string))]+string
		return string

	def get_sw_neighber(self,dpid):
		# dpid = 4
		nb=[]
		n = len(self.graph[0])
		# print self.linkports.keys()
		for i in self.linkports.keys():
			if i[0] == dpid:
				nb.append(i[1])
		# print nb
		return nb
	
	def to_nb_port(self,dpid,nb):
		to_nb_port = []
		for i in nb:
			port = self.linkports[(dpid,i)]
			to_nb_port.append(port)
		return to_nb_port
	
	def add_flow_next(self,switch_src,msg):
		datapath = msg.datapath
		parser = datapath.ofproto_parser
		in_port = msg.match['in_port']
		pkt = packet.Packet(msg.data)
		unknown_dst=pkt.get_protocols(ipv4.ipv4)[0].dst
		switch_dst,switch_port_dst=self.hostports[unknown_dst]
		if switch_src != switch_dst:
			route=self.dijkstra(switch_src,switch_dst)
			outport = self.linkports[(route[0],route[1])]
			actions = [parser.OFPActionOutput(outport)]
			match = parser.OFPMatch(ipv4_dst=unknown_dst,eth_type=0x0800)
			self.add_flow(datapath,16, match, actions)

			out = parser.OFPPacketOut(
			datapath=datapath,
			buffer_id=msg.buffer_id,
			in_port=in_port,
			actions=actions)
			datapath.send_msg(out)
		else:
			datapath_obj = self.dpid_datapath[(switch_dst)][0]
			match = parser.OFPMatch(ipv4_dst=unknown_dst,eth_type=0x0800)
			actions = [parser.OFPActionOutput(switch_port_dst)]
			self.add_flow(datapath_obj,16, match, actions)

			out = parser.OFPPacketOut(
			datapath=datapath,
			buffer_id=msg.buffer_id,
			in_port=in_port,
			actions=actions)
			datapath.send_msg(out)
		pass

	def add_flow_route(self,switch_src,msg):
		datapath = msg.datapath
		parser = datapath.ofproto_parser
		in_port = msg.match['in_port']
		pkt = packet.Packet(msg.data)
		unknown_dst=pkt.get_protocols(ipv4.ipv4)[0].dst
		switch_dst,switch_port_dst=self.hostports[unknown_dst]
		if switch_src != switch_dst:
			route=self.dijkstra(switch_src,switch_dst)
			# print "route:",route,"len of route:",len(route)
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

			firstpktoutport=self.linkports[(route[0],route[1])]
			actions = [parser.OFPActionOutput(firstpktoutport)]
			out = parser.OFPPacketOut(
			datapath=datapath,
			buffer_id=msg.buffer_id,
			in_port=in_port,
			actions=actions)
			time.sleep(0.1)
			datapath.send_msg(out)
		else:
			datapath_obj = self.dpid_datapath[(switch_dst)][0]
			match = parser.OFPMatch(ipv4_dst=unknown_dst,eth_type=0x0800)
			actions = [parser.OFPActionOutput(switch_port_dst)]
			self.add_flow(datapath_obj,16, match, actions)

			out = parser.OFPPacketOut(
			datapath=datapath,
			buffer_id=msg.buffer_id,
			in_port=in_port,
			actions=actions)
			datapath.send_msg(out)		
		pass

	def gen_exp_data(self,exp_data):
		exp_x2_data=[
					[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
					[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
					[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
					[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
					[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
					[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
					[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
					[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
				]
		data=''

		temp_exp = 0
		for i in range(len(exp_data)):
			if sum(exp_data[i])==1:
				for j in range(len(exp_data[0])):
					exp_data[i][j] *=100000
					if exp_data[i][j]==0:
						exp_x2_data[i][2*j]=0
						# print exp_x2_data[i][2*j],
						data+=self.mun_to_6str(exp_x2_data[i][2*j])
						print self.mun_to_6str(exp_x2_data[i][2*j]),
						exp_x2_data[i][2*j+1]=0
						# print exp_x2_data[i][2*j+1],
						data+=self.mun_to_6str(exp_x2_data[i][2*j+1])
						print self.mun_to_6str(exp_x2_data[i][2*j+1]),
					else:
						exp_x2_data[i][2*j]=temp_exp+1
						# print exp_x2_data[i][2*j],
						data+=self.mun_to_6str(exp_x2_data[i][2*j])
						print self.mun_to_6str(exp_x2_data[i][2*j]),
						exp_x2_data[i][2*j+1]=exp_x2_data[i][2*j]+exp_data[i][j]-1
						# print exp_x2_data[i][2*j+1],
						data+=self.mun_to_6str(exp_x2_data[i][2*j+1])
						print self.mun_to_6str(exp_x2_data[i][2*j+1]),
						temp_exp=exp_x2_data[i][2*j+1]
				temp_exp=0
				print
			else:
				print "exp_data err P sum !=1,",sum(exp_data[i])
				return 0
 		# print data
		return data		

	def get_neighber_active_table_all(self,nb):
		'''nb is a list of neighbor'''
		result=[]
		for i in nb:
			result.append(self.activeFlows[i-1])
		return result

	def calculate_exp_data(self,dpid_entry_num,exp_data,dpid):
		#first deal with host spread pkt
		nb = self.get_sw_neighber(dpid)#get dpid's neighber
		nb_tb=self.get_neighber_active_table_all(nb)#get neighber's activetable
		# nb_tb.append(self.activeFlows[dpid-1])#the last one is this dpid's num of entry
		
		# print "tb mun of neighber and self",nb_tb
		if len(self.hosts_port[(dpid)])>0:
			for i in self.hosts_port[(dpid)]:#dpid->port link that to host
				exp_data[i-1][8]=1.0-self.P_spread(dpid_entry_num)
				nb_port = self.to_nb_port(dpid,nb)
				# print "dpid:",dpid, "has a host in port:",i,",nb dpid is ",nb,",this switch's nb port is ",nb_port					
				P_sum=0
				P_each=[0]*len(nb)
				free_tb=[0]*len(nb)
				for j in range(len(nb)):
					free_tb[j]=self.toto_entry_num[(nb[j])] - nb_tb[j]#nb's free num of tb entry
					P_sum+=free_tb[j]
				# print "P_sum :",P_sum
				# print "free_tb:",free_tb
				for j in range(len(nb)):
					P_each[j]=1.0*free_tb[j]/P_sum*(self.P_spread(dpid_entry_num))
					exp_data[i-1][nb_port[j]-1]=P_each[j]
					# print P_each[j],
				# print exp_data[i-1]
		else:
			print "no host linked to dpid:",dpid
			return 0
		#second deal with host spread pkt
		if len(nb)>0:
			for i in range(len(nb)):
				exp_data[nb_port[i]-1][8]=1.0-self.P_spread(dpid_entry_num)
				# print "nb:",nb
				nb_without_in=self.get_sw_neighber(dpid)
				# in_nb=nb_without_in[i]
				# in_nb_port=nb_port
				del nb_without_in[i]
				port_without_in=self.to_nb_port(dpid,nb_without_in)
				# print "nb_without_in", nb_without_in
				# print "port_without_in", port_without_in
				P_each=[0]*len(nb_without_in)
				P_sum=0
				free_tb=[0]*len(nb_without_in)
				for j in range(len(nb_without_in)):
					free_tb[j]=self.toto_entry_num[(nb[j])] - nb_tb[j]#nb's free num of tb entry
					P_sum+=free_tb[j]
				for j in range(len(nb_without_in)):
					P_each[j]=1.0*free_tb[j]/P_sum*(self.P_spread(dpid_entry_num))
					exp_data[nb_port[i]-1][port_without_in[j]-1]=P_each[j]
			return exp_data
		else:
			print "no switch linked to dpid:",dpid
			return 0
		pass

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
		self.activeFlows.append(0)
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
		pkt = packet.Packet(msg.data)

		eth_type = pkt.get_protocols(ethernet.ethernet)[0].ethertype
		arp_pkt = pkt.get_protocol(arp.arp)
		ip_pkt = pkt.get_protocol(ipv4.ipv4)

		if arp_pkt:
			print "an arp packet",
			# print "===Dpid:",datapath.id,"ryu get a packet in",time.ctime(),
			# arp_src_ip = arp_pkt.src_ip
			arp_dst_ip = arp_pkt.dst_ip
			# print "arp_pkt_dst_ip is",arp_dst_ip
			switch_dst,switch_port_dst=self.hostports[arp_dst_ip]
			# print "switch_dst is",switch_dst,"switch_port_dst is",switch_port_dst
			datapath_obj = self.dpid_datapath[(switch_dst)][0]
			# print "out dpid is",datapath_obj.id
			actions = [parser.OFPActionOutput(switch_port_dst)]
			data = msg.data
			out = parser.OFPPacketOut(
				datapath=datapath_obj,
				buffer_id=ofproto.OFP_NO_BUFFER,
				in_port=ofproto.OFPP_CONTROLLER,
				actions=actions,
				data=data)
			print "icmp msg:",msg
			datapath_obj.send_msg(out)
			print "send out"


		elif ip_pkt:
			print "an ip packet"
			# print "===Dpid:",datapath.id,"ryu get a packet in",time.ctime()
			ipv4_hdr = pkt.get_protocols(ipv4.ipv4)[0]
			switch_src = datapath.id
			#print "switch_src=",switch_src,"switch_dst=",switch_dst
			# self.add_flow_route(switch_src,msg)
			self.add_flow_next(switch_src,msg)
			pass

		else:

			# print ""
			pass
	
	@set_ev_cls(ofp_event.EventOFPTableStatsReply, MAIN_DISPATCHER)
	def table_stats_reply_handler(self, ev):
		tables=[]
		# print "dpid:",ev.msg.datapath.id,ev.msg.body[0].active_count
		self.activeFlows[ev.msg.datapath.id - 1]=ev.msg.body[0].active_count
		# 	tables.append(stat)
		# msg = ev.msg
		# dp = msg.datapath
		# self.activeFlows[dp.id - 1]=tables[0].active_count
			# print stat
		pass

	def send_table_stats_request(self):
		hub.sleep(5)
		n=len(self.graph[0])
		while True:
			# self.get_sw_neighber()
			for i in range(n):
			# 	datapath = self.dpid_datapath[(i)][0]
			# 	#print datapathTuple[0]
			# 	ofp = datapath.ofproto
			# 	ofp_parser = datapath.ofproto_parser
			# 	req = ofp_parser.OFPTableStatsRequest(datapath, 0)
			# 	datapath.send_msg(req)
				datapath = self.dpid_datapath[(i+1)][0]
				ofp = datapath.ofproto
				ofp_parser = datapath.ofproto_parser
				req = ofp_parser.OFPTableStatsRequest(datapath, 0)
				datapath.send_msg(req)
			print "============"
			print self.activeFlows

			hub.sleep(5)

	def exp_main(self):
		hub.sleep(5)
		while True:
			dpid = 5
			for dpid in range(7):
				dpid+=1
				print "dpid============",dpid
				dpid_entry_num = self.activeFlows[dpid-1]#This switch's entry number
				dpid_entry_num = 62
				# print "ps:",self.P_spread(dpid_entry_num)
				# print "get the P_s",self.P_spread(64)
				if self.P_spread(dpid_entry_num) == 0:
					exp_data=[	[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1]]
					data=self.gen_exp_data(exp_data)
					print "no spread"
				
				else:
					exp_data=[	[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1]]
					exp_data=self.calculate_exp_data(dpid_entry_num,exp_data,dpid)
					data=self.gen_exp_data(exp_data)
			hub.sleep(5)
	
	def main(self):
		# lie = [[0,100,0,0,0,0,0,0,0],[]]
		hub.sleep(5)
		
		# if self.dpidlib[0] == 1:
		# 	dpid = 1
		# else:
		# 	dpid = 5
		dpid = 5
		exp_type = 2
		data = '000000000000000000100000444444555555666666111111222222333333444444555555666666111111222222444444555555666666\
000000100000444444555555666666111111222222333333444444555555666666111111222222333333444444555555666666888888\
222222333333444444555555666666111111222222333333444444555555666666111111222222333333444444555555666666888888\
222222333333444444555555666666111111222222333333444444555555666666111111222222333333444444555555666666888888\
222222333333444444555555666666111111222222333333444444555555666666111111222222333333444444555555666666888888\
222222333333444444555555666666111111222222333333444444555555666666111111222222333333444444555555666666888888\
222222333333444444555555666666111111222222333333444444555555666666111111222222333333444444555555666666888888\
222222333333444444555555666666111111222222333333444444555555666666111111222222333333444444555555666666888888'
# 		data = '000000000000000000000000000001050000000000000000000000000000000000000000000000000000000000000000050001100000\
# 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001100000\
# 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001100000\
# 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001100000\
# 000000000000000000000000000001037500000000000000000000000000000000000000000000000000000000000000037501100000\
# 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001100000\
# 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001100000\
# 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001100000'
		self.send_experimenter(dpid,exp_type,data)
		print "aoao"
		hub.sleep(1)
		

		datapath_obj = self.dpid_datapath[(4)][0]
		parser = datapath_obj.ofproto_parser
		actions = [parser.OFPActionOutput(1)]
		match = parser.OFPMatch(ipv4_dst='10.0.0.6',eth_type=0x0800)
		self.add_flow(datapath_obj,16, match, actions)		


		datapath_obj = self.dpid_datapath[(7)][0]
		parser = datapath_obj.ofproto_parser
		actions = [parser.OFPActionOutput(1)]
		match = parser.OFPMatch(ipv4_dst='10.0.0.6',eth_type=0x0800)
		self.add_flow(datapath_obj,16, match, actions)
