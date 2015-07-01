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

# class experimenter(app_manager.RyuApp):
#     _CONTEXTS = {
#         'dpset': dpset.DPSet,

#     }
        
#     def __init__(self, *args, **kwargs):
#         super(experimenter, self).__init__(*args, **kwargs)
#         self.threads.append(hub.spawn(self.send_experimenter))
   

#     def send_experimenter(self):
#         hub.sleep(5)
#         while True:
#             print "aoao"
#             hub.sleep(5)

class experimenter(app_manager.RyuApp):
	_CONTEXTS = {
		'dpset': dpset.DPSet,

	}

	def __init__(self, *args, **kwargs):
		super(experimenter, self).__init__(*args, **kwargs)
		self.threads.append(hub.spawn(self.send_experimenter))


	def send_experimenter(self):
		hub.sleep(3)
		while True:
			# print self.dpset.get_all()
			print "qsy"
			hub.sleep(3)

# class experimenter(app_manager.RyuApp):
# 	#OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    # _CONTEXTS = {
    #     'dpset': dpset.DPSet,

    # }
	# def __init__(self, *args, **kwargs):
		# super(experimenter, self).__init__(*args, **kwargs)
# 		# self.arg = arg
	

# 	def send_experimenter(self):
# 		hub.sleep(5)
# 		while True:
# 			print self.dpset.get_all()
# 			hub.sleep(5)


# class experimenter(app_manager.RyuApp):
    # _CONTEXTS = {
    #     'dpset': dpset.DPSet,

    # }

    # def __init__(self, *args, **kwargs):
    #     super(experimenter, self).__init__(*args, **kwargs)









