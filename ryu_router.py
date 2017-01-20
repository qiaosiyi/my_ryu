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
#fattree;

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
from ryu.ofproto.ether import ETH_TYPE_IP, ETH_TYPE_ARP
import time

class experimenter(app_manager.RyuApp):
	_CONTEXTS = {
		'dpset': dpset.DPSet,

	}
	Numofswitch = 20
	MaxEntryNum = 100
	NumofswitchPort = 8
	
	minithresh=[0.9,0.9,0.9,0.9,\
				0.1,0.9,0.9,0.9,\
				0.9,0.9,0.9,0.9,\
				0.9,0.9,0.9,0.9,\
				0.9,0.9,0.9,0.9	]
	maxthresh= [0.9,0.9,0.9,0.9,\
			    0.9,0.9,0.9,0.9,\
			    0.9,0.9,0.9,0.9,\
				0.9,0.9,0.9,0.9,\
				0.9,0.9,0.9,0.9	]
	pmin=[0.5,0.5,0.5,0.5,\
		  0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,\
		  0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5]
	pmax=[0.9,0.9,0.9,0.9,\
		  0.9,0.9,0.9,0.9,0.9,0.9,0.9,0.9,\
		  0.9,0.9,0.9,0.9,0.9,0.9,0.9,0.9]

	loop = 0
	swcount = 0
	dpid_datapath={(1):[]}
	dpidlib=[]
	activeFlows=[]
	conterflow = [0]*Numofswitch
	linkports={(1,5):(1),(5,1):(1),
				(1,9):(2),(9,1):(1),
				(1,13):(3),(13,1):(1),
				(1,17):(4),(17,1):(1),
				(2,5):(1),(5,2):(4),
				(2,9):(2),(9,2):(4),
				(2,13):(3),(13,2):(4),
				(2,17):(4),(17,2):(4),
				(3,6):(1),(6,3):(4),
				(3,10):(2),(10,3):(1),
				(3,14):(3),(14,3):(1),
				(3,18):(4),(18,3):(4),
				(4,6):(1),(6,4):(4),
				(4,10):(2),(10,4):(4),
				(4,14):(3),(14,4):(4),
				(4,18):(4),(18,4):(4),
				(5,7):(2),(7,5):(1),
				(5,8):(3),(8,5):(1),
				(9,11):(2),(11,9):(1),
				(9,12):(3),(12,9):(1),
				(13,15):(2),(15,13):(1),
				(13,16):(3),(16,13):(1),
				(17,19):(2),(19,17):(1),
				(17,20):(3),(20,17):(1),
				(6,7):(2),(7,6):(4),
				(6,8):(3),(8,6):(4),
				(10,11):(2),(11,10):(4),
				(10,12):(3),(12,10):(4),
				(14,15):(2),(15,14):(4),
				(14,16):(3),(16,14):(4),
				(18,19):(2),(19,18):(4),
				(18,20):(3),(20,18):(4),}

	hostports={ '10.0.0.1':[7,2],
				'10.0.0.2':[7,3],
				'10.0.0.3':[8,2],
				'10.0.0.4':[8,3],
				'10.0.0.5':[11,2],
				'10.0.0.6':[11,3],
				'10.0.0.7':[12,2],
				'10.0.0.8':[12,3],
				'10.0.0.9':[15,2],
				'10.0.0.10':[15,3],
				'10.0.0.11':[16,2],
				'10.0.0.12':[16,3],
				'10.0.0.13':[19,2],
				'10.0.0.14':[19,3],
				'10.0.0.15':[20,2],
				'10.0.0.16':[20,3],}

	hosts_port={(1):[],
				(2):[],
				(3):[],
				(4):[],
				(5):[],
				(6):[],
				(9):[],
				(10):[],
				(13):[],
				(14):[],
				(17):[],
				(18):[],
				(7):[2,3],#dpid->port link to host
				(8):[2,3],
				(11):[2,3],
				(12):[2,3],
				(15):[2,3],
				(16):[2,3],
				(19):[2,3],
				(20):[2,3]}

	toto_entry_num={
		(1):MaxEntryNum,
		(2):MaxEntryNum,
		(3):MaxEntryNum,
		(4):MaxEntryNum,
		(5):MaxEntryNum,
		(6):MaxEntryNum,
		(7):MaxEntryNum,
		(8):MaxEntryNum,
		(9):MaxEntryNum,
		(10):MaxEntryNum,
		(11):MaxEntryNum,
		(12):MaxEntryNum,
		(13):MaxEntryNum,
		(14):MaxEntryNum,
		(15):MaxEntryNum,
		(16):MaxEntryNum,
		(17):MaxEntryNum,
		(18):MaxEntryNum,
		(19):MaxEntryNum,
		(20):MaxEntryNum}
		
	graph=[
			[0,99,99,99,1,99,99,99,1,99,99,99,1,99,99,99,1,99,99,99],
			[99,0,99,99,1,99,99,99,1,99,99,99,1,99,99,99,1,99,99,99],
			[99,99,0,99,99,1,99,99,99,1,99,99,99,1,99,99,99,1,99,99],
			[99,99,99,0,99,1,99,99,99,1,99,99,99,1,99,99,99,1,99,99],
			[1,1,99,99,0,99,1,1,99,99,99,99,99,99,99,99,99,99,99,99],
			[99,99,1,1,99,0,1,1,99,99,99,99,99,99,99,99,99,99,99,99],
			[99,99,99,99,1,1,0,99,99,99,99,99,99,99,99,99,99,99,99,99],
			[99,99,99,99,1,1,99,0,99,99,99,99,99,99,99,99,99,99,99,99],
			[1,1,99,99,99,99,99,99,0,99,1,1,99,99,99,99,99,99,99,99],
			[99,99,1,1,99,99,99,99,99,0,1,1,99,99,99,99,99,99,99,99],
			[99,99,99,99,99,99,99,99,1,1,0,99,99,99,99,99,99,99,99,99],
			[99,99,99,99,99,99,99,99,1,1,99,0,99,99,99,99,99,99,99,99],
			[1,1,99,99,99,99,99,99,99,99,99,99,0,99,1,1,99,99,99,99],
			[99,99,1,1,99,99,99,99,99,99,99,99,99,0,1,1,99,99,99,99],
			[99,99,99,99,99,99,99,99,99,99,99,99,1,1,0,99,99,99,99,99],
			[99,99,99,99,99,99,99,99,99,99,99,99,1,1,99,0,99,99,99,99],
			[1,1,99,99,99,99,99,99,99,99,99,99,99,99,99,99,0,99,1,1],
			[99,99,1,1,99,99,99,99,99,99,99,99,99,99,99,99,99,0,1,1],
			[99,99,99,99,99,99,99,99,99,99,99,99,99,99,99,99,1,1,0,99],
			[99,99,99,99,99,99,99,99,99,99,99,99,99,99,99,99,1,1,99,0]]

	def __init__(self, *args, **kwargs):
		super(experimenter, self).__init__(*args, **kwargs)
		self.dpset = kwargs['dpset']
		# self.threads.append(hub.spawn(self.main))
		self.threads.append(hub.spawn(self.send_table_stats_request))
		self.threads.append(hub.spawn(self.exp_main))

	def addWord(self,theIndex,word,pagenumber): 
		theIndex.setdefault(word, [ ]).append(pagenumber)

	def add_flow(self, datapath, priority, match, actions, buffer_id=None):
		dpid = datapath.id
		# print "self.activeFlows[",dpid,"-1]=",self.activeFlows[dpid -1]
		# print "self.toto_entry_num[(",dpid,"-1)]=",self.toto_entry_num[(dpid)]
		if self.activeFlows[dpid -1] < self.toto_entry_num[(dpid)]:
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
										idle_timeout=6000,match=match,##seting a timeout value.
										instructions=inst)
			datapath.send_msg(mod)
			#print "sending flowentry to dp:",datapath.id,"actions:",actions##qsy
			self.conterflow[datapath.id-1] = self.conterflow[datapath.id-1] +1
		else:
			print "dpid:",dpid,"is full of Tb_Entry,can not add anymore entry now."

	def add_flow_no_time_out(self, datapath, priority, match, actions, buffer_id=None):
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
									match=match,instructions=inst)
		datapath.send_msg(mod)
		print "sending flowentry to dp:",datapath.id##qsy
		self.conterflow[datapath.id-1] = self.conterflow[datapath.id-1] +1

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

	def add_flow_next(self,msg):
		datapath = msg.datapath
		parser = datapath.ofproto_parser
		in_port = msg.match['in_port']
		pkt = packet.Packet(msg.data)
		 
		ip_pkt_src = pkt.get_protocols(ipv4.ipv4)[0].src
		unknown_dst=pkt.get_protocols(ipv4.ipv4)[0].dst
		switch_src = datapath.id
		switch_dst,switch_port_dst=self.hostports[unknown_dst]
		# file_obja = open('/usr/local/lib/python2.7/dist-packages/ryu/app/fattree/data_outa.txt','a+')
		# file_obj1 = open('/usr/local/lib/python2.7/dist-packages/ryu/app/fattree/data_out1.txt','a+')
		# file_obj2 = open('/usr/local/lib/python2.7/dist-packages/ryu/app/fattree/data_out2.txt','a+')
		# file_obj3 = open('/usr/local/lib/python2.7/dist-packages/ryu/app/fattree/data_out3.txt','a+')
		file_obja = open('/usr/local/lib/python2.7/dist-packages/ryu/app/fattree/sdata_outa.txt','a+')
		file_obj1 = open('/usr/local/lib/python2.7/dist-packages/ryu/app/fattree/sdata_out1.txt','a+')
		file_obj2 = open('/usr/local/lib/python2.7/dist-packages/ryu/app/fattree/sdata_out2.txt','a+')
		file_obj3 = open('/usr/local/lib/python2.7/dist-packages/ryu/app/fattree/sdata_out3.txt','a+')
		if switch_src != switch_dst:
			# print "src dst=",switch_src,switch_dst,
			route=self.dijkstra(switch_src,switch_dst)
			
			outport = self.linkports[(route[0],route[1])]
			print "ip  dst=",unknown_dst,"    entry_num  ",self.conterflow[4],"     total entry_num  ",sum(self.conterflow)
			file_obja.write(str(switch_src) + '\t'+ '\t'+ip_pkt_src + '\t'+ unknown_dst + '\t'+ str(self.conterflow[4]) + '\t'+ str(sum(self.conterflow)) + '\t'+ str(route) + '\n')
			file_obj1.write(ip_pkt_src + unknown_dst + '\n')
			file_obj2.write(str(self.conterflow[4]) + '\n')
			file_obj3.write(str(sum(self.conterflow)) + '\n')

			file_obja.close()
			file_obj1.close()
			file_obj2.close()
			file_obj3.close()

			actions = [parser.OFPActionOutput(outport)]
			match = parser.OFPMatch(ipv4_src=ip_pkt_src,ipv4_dst=unknown_dst,eth_type=0x0800)
			self.add_flow(datapath,16, match, actions)

			out = parser.OFPPacketOut(
			datapath=datapath,
			buffer_id=msg.buffer_id,
			in_port=in_port,
			actions=actions)
			datapath.send_msg(out)
		else:
			datapath_obj = self.dpid_datapath[(switch_dst)][0]
			match = parser.OFPMatch(ipv4_src=ip_pkt_src,ipv4_dst=unknown_dst,eth_type=0x0800)
			actions = [parser.OFPActionOutput(switch_port_dst)]
			self.add_flow(datapath_obj,16, match, actions)
			print "ip  dst=",unknown_dst,"    entry_num  ",self.conterflow[4],"     total entry_num  ",sum(self.conterflow)
			
			file_obja.write(str(switch_src) + '\t'+ '\t'+ip_pkt_src + '\t'+ unknown_dst + '\t'+ str(self.conterflow[4]) + '\t'+ str(sum(self.conterflow)) + '\t'+ str(datapath_obj.id)  + '\n')
			file_obj1.write(ip_pkt_src + unknown_dst + '\n')
			file_obj2.write(str(self.conterflow[4]) + '\n')
			file_obj3.write(str(sum(self.conterflow)) + '\n')

			file_obja.close()
			file_obj1.close()
			file_obj2.close()
			file_obj3.close()

			out = parser.OFPPacketOut(
			datapath=datapath,
			buffer_id=msg.buffer_id,
			in_port=in_port,
			actions=actions)
			datapath.send_msg(out)
		pass



####################################################### exp msg #####################################################
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
		for i in range(self.NumofswitchPort):
			if 1==1:#sum(exp_data[i])==1:
				for j in range(self.NumofswitchPort+1):#there also is a secure channel
					exp_data[i][j] *=100000
					if exp_data[i][j]==0:
						exp_x2_data[i][2*j]=0
						# print exp_x2_data[i][2*j],
						data+=self.mun_to_6str(exp_x2_data[i][2*j])
						# print self.mun_to_6str(exp_x2_data[i][2*j]),
						exp_x2_data[i][2*j+1]=0
						# print exp_x2_data[i][2*j+1],
						data+=self.mun_to_6str(exp_x2_data[i][2*j+1])
						# print self.mun_to_6str(exp_x2_data[i][2*j+1]),
					else:
						exp_x2_data[i][2*j]=temp_exp+1
						# print exp_x2_data[i][2*j],
						data+=self.mun_to_6str(exp_x2_data[i][2*j])
						# print self.mun_to_6str(exp_x2_data[i][2*j]),
						exp_x2_data[i][2*j+1]=exp_x2_data[i][2*j]+exp_data[i][j]-1
						# print exp_x2_data[i][2*j+1],
						data+=self.mun_to_6str(exp_x2_data[i][2*j+1])
						# print self.mun_to_6str(exp_x2_data[i][2*j+1]),
						temp_exp=exp_x2_data[i][2*j+1]
				temp_exp=0
				# print
			else:
				print "exp_data err P sum !=1,",sum(exp_data[i])
				return 0
 		# print data
		return data

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
		if len(self.hosts_port.get((dpid)))>0:
			for i in self.hosts_port[(dpid)]:#dpid->port link that to host
				exp_data[i-1][8]=1.0-self.P_spread(dpid_entry_num,dpid)
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
					P_each[j]=1.0*free_tb[j]/P_sum*(self.P_spread(dpid_entry_num,dpid))
					exp_data[i-1][nb_port[j]-1]=P_each[j]
					# print P_each[j],
				# print exp_data[i-1]
		# else:
		#	print "no host linked to dpid:",dpid
			#return #################################################################10/24 del this line
		#second deal with host spread pkt
		if len(nb)>0:
			nb_port = self.to_nb_port(dpid,nb)#######################################10/24 add this line
			for i in range(len(nb)):
				exp_data[nb_port[i]-1][8]=1.0-self.P_spread(dpid_entry_num,dpid)
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
					P_each[j]=1.0*free_tb[j]/P_sum*(self.P_spread(dpid_entry_num,dpid))
					exp_data[nb_port[i]-1][port_without_in[j]-1]=P_each[j]
			return exp_data
		else:
			print "no switch linked to dpid:",dpid
			return 0
		pass

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
		# print "|",time.ctime()[11:19],"| Send a",enumtype,"exp_message to dpid(",dpid,")"
		
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

	def P_spread(self, t,dpid):#t is entry num,p is P of spread
		t=1.0*t/self.toto_entry_num[(dpid)]#flowtable utilization of dp
		

		if t>self.minithresh[dpid-1]:
			if t<self.maxthresh[dpid-1]:
				p=self.pmax[dpid-1]*(t-self.minithresh[dpid-1])/(self.maxthresh[dpid-1]-self.minithresh[dpid-1])+self.pmin[dpid-1]
			else:
				p=1
		else:
			p=0
		#print "dpid=",dpid,"t=",t,"minithresh=",self.minithresh[dpid-1],"PMAX=",self.pmax[dpid-1],"p=",p
		return p

	def exp_main(self):
		hub.sleep(5)
		
		while True:
			for dpid in range(self.Numofswitch):
				dpid+=1 #range from 1 : [1,2,3,4,,,]
				# print "dpid============",dpid
				dpid_entry_num = self.activeFlows[dpid-1]# num of active entry of this dpid
				# print "P_spread=",self.P_spread(dpid_entry_num,dpid),"dpid=",dpid,"entry_num=",dpid_entry_num
				if self.P_spread(dpid_entry_num,dpid) == 0: #probability o

					exp_data=[	[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1]]
					data=self.gen_exp_data(exp_data)
					#print "no spread"
				else:

					exp_data=[	[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1],
								[0,0,0,0,0,0,0,0,1]]
					#print "dpid_entry_num",dpid_entry_num
					exp_data=self.calculate_exp_data(dpid_entry_num,exp_data,dpid)
					#print "exp_data",exp_data
					data=self.gen_exp_data(exp_data)
					# print "Ps=",self.P_spread(dpid_entry_num,dpid)
					self.send_experimenter(dpid,2,data)
					print "send a experimenter msg to dpid",dpid," P_spread=",self.P_spread(dpid_entry_num,dpid)
			
			hub.sleep(5)

	


	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		datapath = ev.msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		#print "Adding a dpid:",datapath.id#,datapath#,self.dpid_datapath[(datapath.id)]
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
		# match = parser.OFPMatch()
		match = parser.OFPMatch(eth_type=ETH_TYPE_ARP)
		actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
						ofproto.OFPCML_NO_BUFFER)]
		self.add_flow_no_time_out(datapath, 15, match, actions)
		print "Install table-miss flow entry"
		#print "Install table-miss flow entry to dp:",datapath.id,time.ctime()
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
		# print msg
		datapath = msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		pkt = packet.Packet(msg.data)
		# print pkt
		# eth_type = pkt.get_protocols(ethernet.ethernet)[0].ethertype
		arp_pkt = pkt.get_protocol(arp.arp)
		ip_pkt = pkt.get_protocol(ipv4.ipv4)

		if arp_pkt:
			# print "an arp packet",
			# print "===Dpid:",datapath.id,"ryu get a packet in",time.ctime(),
			# arp_src_ip = arp_pkt.src_ip
			arp_dst_ip = arp_pkt.dst_ip
			# print "arp_pkt_dst_ip is",arp_dst_ip
			switch_dst,switch_port_dst=self.hostports[arp_dst_ip]
			# print "switch_dst is",switch_dst,"switch_port_dst is",switch_port_dst
			datapath_dst = self.dpid_datapath[(switch_dst)][0]
			# print "out dpid is",datapath_dst.id
			actions = [parser.OFPActionOutput(switch_port_dst)]
			data = msg.data
			out = parser.OFPPacketOut(
				datapath=datapath_dst,
				buffer_id=ofproto.OFP_NO_BUFFER,
				in_port=ofproto.OFPP_CONTROLLER,
				actions=actions,
				data=data)
			# print "icmp msg:",msg
			datapath_dst.send_msg(out)
			# print "arp src=",arp_pkt.src_ip,"arp dst=",arp_pkt.dst_ip,"dpid=",datapath.id


		elif ip_pkt:
			ip_pkt_src = pkt.get_protocols(ipv4.ipv4)[0].src
			ip_pkt_dst = pkt.get_protocols(ipv4.ipv4)[0].dst
			
			# print "ip  src=",ip_pkt_src,"ip  dst=",ip_pkt_dst,"dpid=",datapath.id
			# print "===Dpid:",datapath.id,"ryu get a packet in",time.ctime()
			switch_src = datapath.id

			self.add_flow_next(msg)
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
		hub.sleep(17)
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
			print "=======activeFlow====="
			for i in range(4):
				print "   ", self.activeFlows[i-1],
			print
			j=5
			for i in range(4):
				
				print "   ", self.activeFlows[j-1],
				print "   ", self.activeFlows[j],
				j = j+4
			print
			j=7
			for i in range(4):
				
				print "   ", self.activeFlows[j-1],
				print "   ", self.activeFlows[j],
				j = j+4
			print
			print "entry_num",self.activeFlows[4],"total entry_num",sum(self.activeFlows)


			# print "======conterflow======"
			# for i in range(4):
			# 	print "   ", self.conterflow[i-1],
			# print
			# j=5
			# for i in range(4):
				
			# 	print "   ", self.conterflow[j-1],
			# 	print "   ", self.conterflow[j],
			# 	j = j+4
			# print
			# j=7
			# for i in range(4):
				
			# 	print "   ", self.conterflow[j-1],
			# 	print "   ", self.conterflow[j],
			# 	j = j+4
			# print
			# print "entry_num",self.conterflow[4],"total entry_num",sum(self.conterflow)
			#print self.activeFlows

			hub.sleep(10)


