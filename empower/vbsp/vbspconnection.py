#!/usr/bin/env python3
#
# Copyright (c) 2016 Supreeth Herle
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

"""VBSP Connection."""

import time
import tornado.ioloop
import socket
import sys

from protobuf_to_dict import protobuf_to_dict

from empower.vbsp import EMAGE_VERSION
from empower.vbsp import UE_RRC_STATS_REPORT_INTERVAL
from empower.vbsp import PRT_UE_JOIN
from empower.vbsp import PRT_UE_LEAVE
from empower.vbsp import PRT_VBSP_HELLO
from empower.vbsp import PRT_VBSP_BYE
from empower.vbsp import PRT_VBSP_REGISTER
from empower.vbsp import PRT_VBSP_TRIGGER_EVENT
from empower.vbsp import PRT_VBSP_AGENT_SCHEDULED_EVENT
from empower.vbsp import PRT_VBSP_SINGLE_EVENT
from empower.vbsp.messages import main_pb2
from empower.vbsp.messages import configs_pb2
from empower.core.utils import hex_to_ether
from empower.core.utils import ether_to_hex
from empower.core.ue import UE

from empower.main import RUNTIME

import empower.logger
LOG = empower.logger.get_logger()


def create_header(t_id, b_id, header):
    """Create message header."""

    if not header:
        LOG.error("header parameter is None")

    header.vers = EMAGE_VERSION
    # Set the transaction identifier (module id)
    header.t_id = t_id
    # Set the Base station identifier
    header.b_id = b_id
    # Start the sequence number for messages from zero
    header.seq = 0


def serialize_message(message):
    """Serialize message."""

    if not message:
        LOG.error("message parameter is None")
        return None

    return message.SerializeToString()


def deserialize_message(serialized_data):
    """De-Serialize message."""

    if not serialized_data:
        LOG.error("Received serialized data is None")
        return None

    msg = main_pb2.emage_msg()
    msg.ParseFromString(serialized_data)

    return msg


class VBSPConnection(object):
    """VBSP Connection.

    Represents a connection to a ENB (EUTRAN Base Station) using
    the VBSP Protocol. One VBSPConnection object is created for every
    ENB in the network. The object implements the logic for handling
    incoming messages. The currently supported messages are:

    Attributes:
        stream: The stream object used to talk with the ENB.
        address: The connection source address, i.e. the ENB IP address.
        server: Pointer to the server object.
        vbs: Pointer to a VBS object.
    """

    def __init__(self, stream, addr, server):
        self.stream = stream
        self.stream.set_nodelay(True)
        self.addr = addr
        self.server = server
        self.vbs = None
        self.seq = 0
        self.stream.set_close_callback(self._on_disconnect)
        self.__buffer = b''
        self._hb_interval_ms = 500
        self._hb_worker = tornado.ioloop.PeriodicCallback(self._heartbeat_cb,
                                                          self._hb_interval_ms)
        self.endian = sys.byteorder
        self._hb_worker.start()
        self._wait()

    def to_dict(self):
        """ Return dict representation of object """

        return self.addr

    def _heartbeat_cb(self):
        """ Check if connection is still active """

        if self.vbs and not self.stream.closed():
            timeout = (self.vbs.period / 1000) * 3
            if (self.vbs.last_seen_ts + timeout) < time.time():
                LOG.info('Client inactive %s at %r', self.vbs.addr, self.addr)
                self.stream.close()

    def stream_send(self, message):
        """ Send message """

        # Update the sequence number of the messages
        message.head.seq = self.seq + 1

        size = message.ByteSize()

        print(message.__str__())

        size_bytes = (socket.htonl(size)).to_bytes(4, byteorder=self.endian)
        send_buff = serialize_message(message)
        buff = size_bytes + send_buff

        if buff is None:
            LOG.error("errno %u occured")

        self.stream.write(buff)

    def _on_read(self, line):
        """ Appends bytes read from socket to a buffer. Once the full packet
        has been read the parser is invoked and the buffers is cleared. The
        parsed packet is then passed to the suitable method or dropped if the
        packet type in unknown. """

        self.__buffer = b''

        if line is not None:

            self.__buffer = self.__buffer + line

            if len(line) == 4:
                temp_size = int.from_bytes(line, byteorder=self.endian)
                size = socket.ntohl(int(temp_size))
                self.stream.read_bytes(size, self._on_read)
                return

            deserialized_msg = deserialize_message(line)

            # Update the sequency number from received message
            self.seq = deserialized_msg.head.seq

            # print(deserialized_msg.__str__())

            self._trigger_message(deserialized_msg)
            self._wait()

    def _trigger_message(self, deserialized_msg):

        event_type = deserialized_msg.WhichOneof("event_types")

        if event_type == PRT_VBSP_SINGLE_EVENT:
            msg_type = deserialized_msg.se.WhichOneof("events")
        elif event_type == PRT_VBSP_AGENT_SCHEDULED_EVENT:
            msg_type = deserialized_msg.sche.WhichOneof("events")
        elif event_type == PRT_VBSP_TRIGGER_EVENT:
            msg_type = deserialized_msg.te.WhichOneof("events")
        else:
            LOG.error("Unknown message event type %s", event_type)

        if not msg_type or msg_type not in self.server.pt_types:
            LOG.error("Unknown message type %s", msg_type)
            return

        if msg_type != PRT_VBSP_HELLO and not self.vbs:
            return

        # Print messages other than hello messages
        if msg_type != PRT_VBSP_HELLO:
            print(deserialized_msg.__str__())

        handler_name = "_handle_%s" % self.server.pt_types[msg_type]

        if hasattr(self, handler_name):
            handler = getattr(self, handler_name)
            handler(deserialized_msg)

        if msg_type in self.server.pt_types_handlers:
            for handler in self.server.pt_types_handlers[msg_type]:
                handler(deserialized_msg)

    def _handle_hello(self, main_msg):
        """ Handle an incoming HELLO message

        Args:
            main_msg, a emage_msg containing HELLO message
        Returns:
            None
        """

        enb_id = main_msg.head.b_id
        vbs_id = hex_to_ether(enb_id)

        try:
            vbs = RUNTIME.vbses[vbs_id]
        except KeyError:
            LOG.error("Hello from unknown VBS (%s)", (vbs_id))
            return

        LOG.info("Hello from %s VBS %s seq %u", self.addr[0], vbs.addr,
                 main_msg.head.seq)

        # New connection
        if not vbs.connection:

            # set pointer to pnfdev object
            self.vbs = vbs

            # set connection
            vbs.connection = self

            # send tenants information to VBS
            self.send_vbs_tenants_info()

            # request VBS Cells configuration information
            self.send_vbs_cells_conf_req()

            # request registered UEs
            self.send_ues_id_req()

            # request VBS for RAN sharing information
            self.send_vbs_ran_sh_conf_req()

            # generate register message
            self.send_register_message_to_self()

        # Update VBSP params
        vbs.period = main_msg.se.mHello.repl.period
        vbs.last_seen = main_msg.head.seq
        vbs.last_seen_ts = time.time()

    def _handle_ues_id_repl(self, main_msg):
        """ Handle an incoming UEs ID reply

        Args:
            message, a emage_msg containing UE IDs (RNTIs)
        Returns:
            None
        """

        active_ues = {}
        inactive_ues = {}

        event_type = main_msg.WhichOneof("event_types")
        msg = protobuf_to_dict(main_msg)
        ues_id_msg_repl = msg[event_type]["mUEs_id"]["repl"]

        if ues_id_msg_repl["status"] != configs_pb2.CREQS_SUCCESS:
            return

        # List of active UEs
        if "active_ue_id" in ues_id_msg_repl:
            for ue in ues_id_msg_repl["active_ue_id"]:
                active_ues[(self.vbs.addr, ue["rnti"])] = {}
                if "imsi" in ue:
                    active_ues[(self.vbs.addr, ue["rnti"])]["imsi"] = \
                                                                ue["imsi"]
                else:
                    active_ues[(self.vbs.addr, ue["rnti"])]["imsi"] = ""
                if "plmn_id" in ue:
                    active_ues[(self.vbs.addr, ue["rnti"])]["plmn_id"] = \
                                                            ue["plmn_id"]
                else:
                    active_ues[(self.vbs.addr, ue["rnti"])]["plmn_id"] = ""

        # List of inactive UEs
        if "inactive_ue_id" in ues_id_msg_repl:
            for ue in ues_id_msg_repl["inactive_ue_id"]:
                inactive_ues[(self.vbs.addr, ue["rnti"])] = {}
                if "imsi" in ue:
                    inactive_ues[(self.vbs.addr, ue["rnti"])]["imsi"] = \
                                                                ue["imsi"]
                else:
                    inactive_ues[(self.vbs.addr, ue["rnti"])]["imsi"] = ""
                if "plmn_id" in ue:
                    inactive_ues[(self.vbs.addr, ue["rnti"])]["plmn_id"] = \
                                                            ue["plmn_id"]
                else:
                    inactive_ues[(self.vbs.addr, ue["rnti"])]["plmn_id"] = ""

        for vbs_id, rnti in active_ues.keys():

            ue_id = (self.vbs.addr, rnti)

            if ue_id not in RUNTIME.ues:
                new_ue = UE(ue_id, ue_id[1], self.vbs)
                RUNTIME.ues[ue_id] = new_ue

            ue = RUNTIME.ues[ue_id]

            imsi = active_ues[ue_id]["imsi"]
            plmn_id = active_ues[ue_id]["plmn_id"]

            # Setting IMSI of UE
            ue.imsi = imsi

            if ue.plmn_id == "" and plmn_id != "":

                # Setting tenant
                ue.tenant = RUNTIME.load_tenant_by_plmn_id(plmn_id)

                if ue.tenant:

                    # Adding UE to tenant
                    LOG.info("Adding %s to tenant %s", ue.addr,
                             ue.tenant.plmn_id)
                    ue.tenant.ues[ue.addr] = ue

                    # Raise UE join
                    self.server.send_ue_join_message_to_self(ue)

                    # Create a trigger for reporting RRC measurements config
                    from empower.ue_confs.ue_rrc_meas_confs import ue_rrc_meas_confs

                    conf_req = {
                        "event_type": "trigger"
                    }

                    ue_rrc_meas_confs(tenant_id=ue.tenant.tenant_id,
                                      vbs=ue.vbs.addr,
                                      ue=ue.rnti,
                                      conf_req=conf_req)

                    # Trigger UE RRC stats for the operating frequency of UE
                    from empower.ue_stats.ue_rrc_stats import ue_rrc_stats

                    if ue.vbs.cells and len(ue.vbs.cells) > 0 and \
                        "carrier_freq" in ue.vbs.cells[0] and \
                        "num_rbs_dl" in ue.vbs.cells[0] and \
                        ue.vbs.cells[0]["num_rbs_dl"] > 0:
                        # UE is assumed to be attached to Cell 0.
                        meas_req = {
                            "rat_type": "EUTRA",
                            "cell_to_measure": [],
                            "blacklist_cells": [],
                            "bandwidth": ue.vbs.cells[0]["num_rbs_dl"],
                            "carrier_freq": ue.vbs.cells[0]["carrier_freq"],
                            "report_type": "periodical_ref_signal",
                            "report_interval": UE_RRC_STATS_REPORT_INTERVAL,
                            "trigger_quantity": "RSRP",
                            "num_of_reports": "infinite",
                            "max_report_cells": 3,
                        }

                        ue_rrc_stats(tenant_id=ue.tenant.tenant_id,
                                      vbs=ue.vbs.addr,
                                      ue=ue.rnti,
                                      meas_req=meas_req)

            if ue.plmn_id != "" and plmn_id == "":

                # Raise UE leave
                self.server.send_ue_leave_message_to_self(ue)

                # Removing UE from tenant
                LOG.info("Removing %s from tenant %s", ue.addr,
                         ue.tenant.plmn_id)
                del ue.tenant.ues[ue.addr]

                # Resetting tenant
                ue.tenant = None

        existing_ues = []
        existing_ues.extend(RUNTIME.ues.keys())

        for ue_addr in existing_ues:

            if ue_addr[0] != hex_to_ether(main_msg.head.b_id):
                continue

            if ue_addr not in active_ues:
                RUNTIME.remove_ue(ue_addr)

    def _handle_rrc_meas_conf_repl(self, main_msg):
        """ Handle an incoming UE's RRC Measurements configuration reply

        Args:
            message, a message containing RRC Measurements configuration in UE
        Returns:
            None
        """

        event_type = main_msg.WhichOneof("event_types")
        msg = protobuf_to_dict(main_msg)
        rrc_m_conf_repl = msg[event_type][PRT_UE_RRC_MEAS_CONF]["repl"]

        rnti = rrc_m_conf_repl["rnti"]

        ue_id = (self.vbs.addr, rnti)

        if ue_id not in RUNTIME.ues:
            return

        ue = RUNTIME.ues[ue_id]

        if rrc_m_conf_repl["status"] != configs_pb2.CREQS_SUCCESS:
            return

        del rrc_m_conf_repl["rnti"]
        del rrc_m_conf_repl["status"]

        if "ue_rrc_state" in rrc_m_conf_repl:
            ue.rrc_state = rrc_m_conf_repl["ue_rrc_state"]
            del rrc_m_conf_repl["ue_rrc_state"]

        if "capabilities" in rrc_m_conf_repl:
            ue.capabilities = rrc_m_conf_repl["capabilities"]
            del rrc_m_conf_repl["capabilities"]

        # Trigger UE RRC stats for the operating frequency of UE
        from empower.ue_stats.ue_rrc_stats import ue_rrc_stats

        if "freq" in rrc_m_conf_repl and \
            ue.vbs.cells and len(ue.vbs.cells) > 0 and \
            "num_rbs_dl" in ue.vbs.cells[0] and \
            ue.vbs.cells[0]["num_rbs_dl"] > 0:
            # UE is assumed to be attached to Cell 0.
            meas_req = {
                "rat_type": "EUTRA",
                "cell_to_measure": [],
                "blacklist_cells": [],
                "bandwidth": ue.vbs.cells[0]["num_rbs_dl"],
                "carrier_freq": rrc_m_conf_repl["freq"],
                "report_type": "periodical_ref_signal",
                "report_interval": UE_RRC_STATS_REPORT_INTERVAL,
                "trigger_quantity": "RSRP",
                "num_of_reports": "infinite",
                "max_report_cells": 3,
            }

            ue_rrc_stats(tenant_id=ue.tenant.tenant_id,
                          vbs=ue.vbs.addr,
                          ue=ue.rnti,
                          meas_req=meas_req)

        ue.rrc_meas_config = rrc_m_conf_repl

    def _handle_vbs_cells_conf_repl(self, main_msg):
        """ Handle an incoming VBS cells configuration reply

        Args:
            message, a message containing VBS cells configuration requested
        Returns:
            None
        """

        event_type = main_msg.WhichOneof("event_types")
        msg = protobuf_to_dict(main_msg)
        conf_repl = msg[event_type]["mENB_cells"]["repl"]

        enb_id = msg["head"]["b_id"]

        if self.vbs.enb_id != enb_id:
            return

        if "cells" in conf_repl:
            self.vbs.cells = conf_repl["cells"]

            from empower.vbs_stats.vbs_cell_stats import vbs_cell_stats

            stats_req = {
                "event_type": "trigger",
                "stats_type": "prb_utilization"
            }

            # Initiate Cell PRB utilization stats in all the cells of VBS
            for cell in self.vbs.cells:
                for tenant_id in RUNTIME.tenants.keys():
                    if self.vbs.addr in RUNTIME.tenants[tenant_id].vbses:
                        vbs_cell_stats(tenant_id=tenant_id,
                                      vbs=self.vbs.addr,
                                      cell=cell["phys_cell_id"],
                                      stats_req=stats_req)

        if "ran_sh_i" in conf_repl:
            self.vbs.ran_sh_i = conf_repl["ran_sh_i"]

    def send_vbs_tenants_info(self):
        """ Send tenants information to VBS (eNB) """

        for tenant in RUNTIME.tenants.values():

            if tenant.plmn_id == "":
                continue

            if self.vbs.addr not in tenant.vbses:
                continue

            ran_sh_ctrl_req = main_pb2.emage_msg()

            enb_id = ether_to_hex(self.vbs.addr)
            # Transaction identifier is zero by default for single event request
            create_header(0, enb_id, ran_sh_ctrl_req.head)

            # Creating a single event message to control RAN sharing in VBS
            se_msg = ran_sh_ctrl_req.se

            ran_sh_ctrl_msg = se_msg.mRAN_sharing_ctrl
            ran_sh_ctrl_req_msg = ran_sh_ctrl_msg.req

            add_t = ran_sh_ctrl_req_msg.add_t
            add_t.plmn_id = tenant.plmn_id

            LOG.info("Sending Add tenant to VBS message %s (%u)",
                     self.vbs.addr, enb_id)

            self.stream_send(ran_sh_ctrl_req)

    def send_ues_id_req(self):
        """ Send request for UEs ID registered in VBS """

        ues_id_req = main_pb2.emage_msg()

        enb_id = ether_to_hex(self.vbs.addr)
        # Transaction identifier is one by default for trigger messages
        create_header(1, enb_id, ues_id_req.head)

        # Creating a trigger message to fetch UE RNTIs
        trigger_msg = ues_id_req.te
        trigger_msg.action = main_pb2.EA_ADD

        UEs_id_msg = trigger_msg.mUEs_id
        UEs_id_req_msg = UEs_id_msg.req

        UEs_id_req_msg.dummy = 1

        LOG.info("Sending UEs request to VBS %s (%u)",
                 self.vbs.addr, enb_id)

        self.stream_send(ues_id_req)

    def send_vbs_cells_conf_req(self):
        """ Send request for configuration about cells in VBS (eNB) """

        eNB_cells_req = main_pb2.emage_msg()

        enb_id = ether_to_hex(self.vbs.addr)
        # Transaction identifier is zero by default for single event requests
        create_header(0, enb_id, eNB_cells_req.head)

        # Creating a single event message to fetch cells information in VBS
        se_msg = eNB_cells_req.se

        eNB_cells_msg = se_msg.mENB_cells
        eNB_cells_req_msg = eNB_cells_msg.req

        eNB_cells_req_msg.enb_info_types = 0 | configs_pb2.ENB_CELLS_INFO

        LOG.info("Sending VBS (eNB) cells conf request to VBS %s (%u)",
                 self.vbs.addr, enb_id)

        self.stream_send(eNB_cells_req)

    def send_vbs_ran_sh_conf_req(self):
        """ Send request for configuration about RAN sharing in VBS (eNB) """

        eNB_cells_req = main_pb2.emage_msg()

        enb_id = ether_to_hex(self.vbs.addr)
        # Transaction identifier is 1 by default for schedule event requests
        create_header(1, enb_id, eNB_cells_req.head)

        # Creating a schedule event message to fetch cells information in VBS
        sche_msg = eNB_cells_req.sche
        sche_msg.interval = 10000
        sche_msg.action = main_pb2.EA_ADD

        eNB_cells_msg = sche_msg.mENB_cells
        eNB_cells_req_msg = eNB_cells_msg.req

        eNB_cells_req_msg.enb_info_types = 0 | configs_pb2.ENB_RAN_SHARING_INFO

        LOG.info("Sending VBS (eNB) RAN sharing conf request to VBS %s (%u)",
                 self.vbs.addr, enb_id)

        self.stream_send(eNB_cells_req)

    def send_rrc_meas_conf_req(self, ue):
        """ Sends a request for RRC measurements configuration of UE """

        rrc_m_conf_req = main_pb2.emage_msg()
        enb_id = ether_to_hex(self.vbs.addr)

        # Transaction identifier is one by default
        create_header(1, enb_id, rrc_m_conf_req.head)

        # Creating a trigger message to fetch UE RNTIs
        trigger_msg = rrc_m_conf_req.te
        trigger_msg.action = main_pb2.EA_ADD

        rrc_m_conf_msg = trigger_msg.mUE_rrc_meas_conf
        rrc_m_conf_req_msg = rrc_m_conf_msg.req

        rrc_m_conf_req_msg.rnti = ue.rnti

        LOG.info("Sending UEs RRC measurement config request to VBS %s (%u)",
                 self.vbs.addr, enb_id)

        self.stream_send(rrc_m_conf_req)

    def _wait(self):
        """ Wait for incoming packets on signalling channel """
        self.stream.read_bytes(4, self._on_read)

    def _on_disconnect(self):
        """ Handle VBSP disconnection """

        if not self.vbs:
            return

        LOG.info("VBS disconnected: %s", self.vbs.addr)

        # remove hosted ues
        for addr in list(RUNTIME.ues.keys()):
            ue = RUNTIME.ues[addr]
            if ue.vbs == self.vbs:
                RUNTIME.remove_ue(ue.addr)

        # Send bye message
        self.send_bye_message_to_self()

        # reset state
        self.vbs.last_seen = 0
        self.vbs.connection = None
        self.vbs.ran_sh_i = None
        self.vbs.cells = None
        self.vbs.cell_stats = None
        self.vbs.ues = {}
        self.vbs.period = 0
        self.vbs = None

    def send_bye_message_to_self(self):
        """ Send a unsollicited BYE message to self """

        for handler in self.server.pt_types_handlers[PRT_VBSP_BYE]:
            handler(self.vbs)

    def send_register_message_to_self(self):
        """ Send a REGISTER message to self """

        for handler in self.server.pt_types_handlers[PRT_VBSP_REGISTER]:
            handler(self.vbs)
