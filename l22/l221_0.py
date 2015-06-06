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
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import udp
from ryu.lib.packet import ipv4
import time



class L22(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
       
    linkports={(1,2):(3),(2,1):(3),
               (1,3):(2),(3,1):(2),
               (3,4):(1),(4,3):(3),
               (2,4):(1),(4,2):(2),
               (2,5):(2),(5,2):(4),
               (4,5):(1),(5,4):(1),
               (5,6):(3),(6,5):(2),
               (6,7):(1),(7,6):(2),
               (5,7):(2),(7,5):(3)
    }

    hostports={ '10.0.0.1':[1,1],
                '10.0.0.2':[2,4],
                '10.0.0.3':[3,3],
                '10.0.0.4':[4,4],
                '10.0.0.5':[5,5],
                '10.0.0.6':[6,3],
                '10.0.0.7':[7,1],
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
    
    dpid_datapath={(1):[]}

    conter = 0
    conterflow = [0]*7
    unknown_dst = []
    
    def __init__(self, *args, **kwargs):
        super(L22, self).__init__(*args, **kwargs)
        #self.mac_to_port = {}

    def addWord(self,theIndex,word,pagenumber): 
        theIndex.setdefault(word, [ ]).append(pagenumber)

    def advanceroute(self,conterflow):
        # print conterflow
        n=len(self.graph[0])
        for j in range(n):
            # temp = conterflow[j]
            for i in range(n):
                a = self.graph[i][j]
                if a != 0 and a != 99:
                    self.graph[i][j] = 2*conterflow[j]
        # for j in range(n):
        #     print self.graph[j][:]
        print "advanceroute()"



    def dijkstra(self,k,e):
        k=k-1
        e=e-1
        # graph = self.graph

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
            # if k==i:#
            #     return
            flag[k]=True
            for i in range(n):
                if dis[i]>dis[k]+self.graph[k][i]:
                    dis[i]=dis[k]+self.graph[k][i]
                    pre[i]=k
        # print "from[",start+1,"]dis=",dis
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
        print datapath,datapath.id#,self.dpid_datapath[(datapath.id)]
        # if len(self.dpid_datapath[datapath.id]) == 0:
        self.addWord(self.dpid_datapath,datapath.id,datapath)
        # self.addWord(self.dpid_datapath,datapath.id,datapath)
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
        print "Install table-miss flow entry to dp:",datapath.id##qsy
        print self.conterflow
        #print "self.graph[3][2]=",self.graph[3][2]
       # self.advanceroute(self.conterflow)
        # print "self.dpid_datapath[(datapath.id)]=",self.dpid_datapath[(datapath.id)][0]
            #<ryu.controller.controller.Datapath object at 0x32f5310>

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


    @set_ev_cls(ofp_event.EventOFPPacketIn,MAIN_DISPATCHER)
    def packet_in_handler(self,ev):
        

        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        
        dpid = datapath.id
        # print "No.",self.conter,"packetin========","dpid=",dpid,"=====================",time.ctime()
        
        #print pkt.get_protocols(ipv4.ipv4)
        if len(pkt.get_protocols(ipv4.ipv4)) != 0:
            self.conter = self.conter + 1
            print "No.",self.conter,"packetin========","dpid=",dpid,"=====================",time.ctime()
            ipv4_hdr = pkt.get_protocols(ipv4.ipv4)[0]
            unknown_dst=pkt.get_protocols(ipv4.ipv4)[0].dst#'10.0.0.2'
            switch_dst,switch_port_dst=self.hostports[unknown_dst]
            switch_src = dpid
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


            print "flowentry Num in each SDNSwitchs",self.conterflow
            firstpktoutport=self.linkports[(route[0],route[1])]
            actions = [parser.OFPActionOutput(firstpktoutport)]
            out = parser.OFPPacketOut(
            datapath=datapath,buffer_id=msg.buffer_id,in_port=in_port,
            actions=actions)
            time.sleep(0.5)
            self.advanceroute(self.conterflow)
            datapath.send_msg(out)

            

        else :
            if len(pkt.get_protocols(ethernet.ethernet)) != 0:
                pass

