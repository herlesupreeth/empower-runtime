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

"""Signal strength visulization app."""

import random

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD
from empower.main import RUNTIME
from empower.vbsp.ue_handover import ue_handover
from empower.events.vbsup import vbsup
from empower.events.vbsdown import vbsdown
import tornado.ioloop

from empower.main import RUNTIME

GRAPH_TOP_BOTTOM_MARGIN = 40
GRAPH_LEFT_RIGHT_MARGIN = 40
GRAPH_MAX_WIDTH = 1130 - GRAPH_LEFT_RIGHT_MARGIN
GRAPH_MAX_HEIGHT = 750 - GRAPH_TOP_BOTTOM_MARGIN
MIN_DISTANCE = 70
N_XY = 300


class HandoverManager(EmpowerApp):
    """Handover Manager app.

    Command Line Parameters:

        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:

        ./empower-runtime.py apps.handovermanager.handovermanager \
            --tenant_id=8f83e794-1d07-4430-b5bd-db45d670c8f0
    """

    def __init__(self, **kwargs):

        # Flag to enable or disable load balacing algorithm
        self.__load_balance = True
        # Source cell downlink utilization threshold in percentage
        self.__s_dl_thr = 10
        # Source cell uplink utilization threshold in percentage
        self.__s_ul_thr = 10
        # Target cell downlink utilization threshold in percentage
        self.__t_dl_thr = 30
        # Target cell downlink utilization threshold in percentage
        self.__t_ul_thr = 30
        # RSRQ threshold to be handed over to a cell
        self.__rsrq_thr = -20
        # Minimum number of UEs above which eNB becomes eligible to handover UEs
        self.__min_ue = 1
        # Maximum number of handovers that can performed from a cell at
        # each evaluation period
        self.__max_ho_from = 1
        # Maximum number of handovers that can performed to a cell at
        # each evaluation period
        self.__max_ho_to = 1
        # Base auth parameter for API requests
        self.base_auth_usr = None
        self.base_auth_pwd = None

        EmpowerApp.__init__(self, **kwargs)

        self.graphData = {}

        # List of VBSes active
        self.vbses = []

        # Generating inital coordinates for the graph nodes
        self.coord = self.get_coordinates()

        vbsup(tenant_id=self.tenant.tenant_id, callback=self.vbs_up_callback)
        vbsdown(tenant_id=self.tenant.tenant_id, callback=self.vbs_down_callback)

    @property
    def load_balance(self):
        """Return flag to enable or disable load balacing algorithm."""

        return self.__load_balance

    @load_balance.setter
    def load_balance(self, value):
        """Set flag to enable or disable load balacing algorithm."""

        if bool(value) != True and bool(value) != False:
            raise ValueError("Invalid value for load balacing flag")

        self.__load_balance = bool(value)

    @property
    def s_dl_thr(self):
        """Return source cell downlink utilization threshold."""

        return self.__s_dl_thr

    @s_dl_thr.setter
    def s_dl_thr(self, value):
        """Set source cell downlink utilization threshold."""

        thr = float(value)

        if thr < 0 or thr > 100:
            raise ValueError("Invalid value for source cell DL util. threshold")

        self.__s_dl_thr = thr

    @property
    def s_ul_thr(self):
        """Return source cell uplink utilization threshold."""

        return self.__s_ul_thr

    @s_ul_thr.setter
    def s_ul_thr(self, value):
        """Set source cell uplink utilization threshold."""

        thr = float(value)

        if thr < 0 or thr > 100:
            raise ValueError("Invalid value for source cell UL util. threshold")

        self.__s_ul_thr = thr

    @property
    def t_dl_thr(self):
        """Return target cell downlink utilization threshold."""

        return self.__t_dl_thr

    @t_dl_thr.setter
    def t_dl_thr(self, value):
        """Set target cell downlink utilization threshold."""

        thr = float(value)

        if thr < 0 or thr > 100:
            raise ValueError("Invalid value for target cell DL util. threshold")

        self.__t_dl_thr = thr

    @property
    def t_ul_thr(self):
        """Return target cell uplink utilization threshold."""

        return self.__t_ul_thr

    @t_ul_thr.setter
    def t_ul_thr(self, value):
        """Set target cell uplink utilization threshold."""

        thr = float(value)

        if thr < 0 or thr > 100:
            raise ValueError("Invalid value for target cell UL util. threshold")

        self.__t_ul_thr = thr

    @property
    def rsrq_thr(self):
        """Return RSRQ threshold to be handed over to a cell."""

        return self.__rsrq_thr

    @rsrq_thr.setter
    def rsrq_thr(self, value):
        """Set RSRQ threshold to be handed over to a cell."""

        thr = float(value)
        # RSRQ values ranges from -3 to -19.5
        if thr > -3 or thr < -20:
            raise ValueError("Invalid value for RSRQ threshold threshold")

        self.__rsrq_thr = thr

    @property
    def min_ue(self):
        """
            Return minimum number of UEs above which eNB becomes eligible to
            handover UEs.
        """

        return self.__min_ue

    @min_ue.setter
    def min_ue(self, value):
        """
            Set minimum number of UEs above which eNB becomes eligible to
            handover UEs.
        """

        self.__min_ue = int(value)

    @property
    def max_ho_from(self):
        """
            Return maximum number of handovers that can performed from a eNB at
            each evaluation period.
        """

        return self.__max_ho_from

    @max_ho_from.setter
    def max_ho_from(self, value):
        """
            Set maximum number of handovers that can performed from a eNB at
            each evaluation period.
        """

        self.__max_ho_from = int(value)

    @property
    def max_ho_to(self):
        """
            Return maximum number of handovers that can performed to a eNB at
            each evaluation period.
        """

        return self.__max_ho_to

    @max_ho_to.setter
    def max_ho_to(self, value):
        """
            Set maximum number of handovers that can performed to a eNB at
            each evaluation period.
        """

        self.__max_ho_to = int(value)

    def get_coordinates(self):

        rangeX = (GRAPH_LEFT_RIGHT_MARGIN, GRAPH_MAX_WIDTH)
        rangeY = (GRAPH_TOP_BOTTOM_MARGIN, GRAPH_MAX_HEIGHT)

        deltas = set()
        for x in range(-MIN_DISTANCE, MIN_DISTANCE + 1):
            for y in range(-MIN_DISTANCE, MIN_DISTANCE + 1):
                if (x * x) + (y * y) >= MIN_DISTANCE * MIN_DISTANCE:
                    deltas.add((x,y))

        randPoints = []
        excluded = set()
        count = 0
        while count < N_XY:
            x = random.randrange(*rangeX)
            y = random.randrange(*rangeY)

            if (x, y) in excluded:
                continue

            randPoints.append((x, y))
            count += 1

            excluded.update((x + dx, y + dy) for (dx, dy) in deltas)

        return randPoints

    def to_dict(self):
        """Return json-serializable representation of the object."""

        out = super().to_dict()
        out['graphData'] = self.graphData
        out['base_auth_usr'] = self.base_auth_usr
        out['base_auth_pwd'] = self.base_auth_pwd

        return out

    def vbs_up_callback(self, vbs):
        """Called when an VBS connects to a tenant."""

        # Append VBS to list of active VBSs
        if vbs not in self.vbses:
            self.vbses.append(vbs)

    def vbs_down_callback(self, vbs):
        """Called when an VBS disconnects from a tenant."""

        # Removes VBS from list of active VBSs
        if vbs in self.vbses:
            self.vbses.remove(vbs)

    def load_balance_algo(self):
        """ Load balancing algorithm. """

        tenant = RUNTIME.tenants[self.tenant.tenant_id]

        # Dictionary containing VBS which qualifies for performing handover
        ho_from_vbses = {}
        # Dictionary containing VBS which qualifies to receive handed over UEs
        ho_to_vbses = {}

        self.log.info("Running load balancing algorithm...")

        # Check the condition cellUtilDL > dl_thr or cellUtilUL > ul_thr.
        for vbs in self.tenant.vbses.values():

            if vbs.connection and vbs.cell_stats:

                # Check the PRB utilization for each cell
                for cell, stat in vbs.cell_stats.items():
                    #
                    #
                    self.log.info("VBS {0}, registered PRB usage:".format(vbs.enb_id))
                    if ("perc_prbs" in stat["dl_prb_utilz"] and stat["dl_prb_utilz"]["perc_prbs"]):
                    	self.log.info("DL: {0} / {1} / {2}".format(stat["dl_prb_utilz"]["perc_prbs"], self.s_dl_thr, self.t_dl_thr))
                    if ("perc_prbs" in stat["ul_prb_utilz"] and stat["ul_prb_utilz"]["perc_prbs"]):
                    	self.log.info("UL: {0} / {1} / {2}".format(stat["ul_prb_utilz"]["perc_prbs"], self.s_ul_thr, self.t_ul_thr))
                    #
                    #

                    if ("dl_prb_utilz" in stat and \
                        "perc_prbs" in stat["dl_prb_utilz"] and \
                        stat["dl_prb_utilz"]["perc_prbs"] > self.s_dl_thr) \
                        or ("ul_prb_utilz" in stat and \
                        "perc_prbs" in stat["ul_prb_utilz"] and \
                        stat["ul_prb_utilz"]["perc_prbs"] > self.s_ul_thr):

                        if vbs.addr not in ho_from_vbses:

                            ho_from_vbses[vbs.addr] = ({
                                                            "vbs": vbs,
                                                            "cells": [cell],
                                                            "ues": [],
                                                            "max_ho_from": 0,
                                                            "num_ues": 0
                                                        })
                        else:
                            ho_from_vbses[vbs.addr]["cells"].append(cell)
                        #
                        #
                        self.log.info("Condition: DL > dl_thr OR UL > ul_thr")
                        # if ("dl_prb_utilz" in stat and "perc_prbs" in stat["dl_prb_utilz"]):
                        #    self.log.info("    DL: {0} / {1}".format(stat["dl_prb_utilz"]["perc_prbs"], self.s_dl_thr))
                        # if ("ul_prb_utilz" in stat and "perc_prbs" in stat["ul_prb_utilz"]):
                        #    self.log.info("    UL: {0} / {1}".format(stat["ul_prb_utilz"]["perc_prbs"], self.s_ul_thr))
                        self.log.info("    Status:")
                        self.log.info("    {0}".format(ho_from_vbses[vbs.addr]["cells"]))
                        #
                        #

                    if ("dl_prb_utilz" in stat and \
                        "perc_prbs" in stat["dl_prb_utilz"] and \
                        stat["dl_prb_utilz"]["perc_prbs"] < self.t_dl_thr) \
                        and ("ul_prb_utilz" in stat and \
                        "perc_prbs" in stat["ul_prb_utilz"] and \
                        stat["ul_prb_utilz"]["perc_prbs"] < self.t_ul_thr):

                        if vbs.addr not in ho_to_vbses:

                            ho_to_vbses[vbs.addr] = ({
                                                            "vbs": vbs,
                                                            "cells": [cell],
                                                            "ues": [],
                                                            "max_ho_to": 0,
                                                            "num_ues": 0
                                                    })
                        else:
                            ho_to_vbses[vbs.addr]["cells"].append(cell)
                        #
                        #
                        self.log.info("Condition: DL < dl_thr AND UL < ul_thr")
                        # self.log.info("    DL: {0} / {1}".format(stat["dl_prb_utilz"]["perc_prbs"], self.t_dl_thr))
                        # self.log.info("    UL: {0} / {1}".format(stat["ul_prb_utilz"]["perc_prbs"], self.t_ul_thr))
                        self.log.info("    Status:")
                        self.log.info("    {0}".format(ho_to_vbses[vbs.addr]["cells"]))
                        #
                        #

        # Check the condition number of UEs served by VBS >= min_ue.
        for ue in self.tenant.ues.values():
            if ue.vbs.addr in ho_from_vbses:
                ho_from_vbses[ue.vbs.addr]["ues"].append(ue)
                ho_from_vbses[ue.vbs.addr]["num_ues"] += 1
            if ue.vbs.addr in ho_to_vbses:
                ho_to_vbses[ue.vbs.addr]["ues"].append(ue)
                ho_to_vbses[ue.vbs.addr]["num_ues"] += 1

        vbses_info = ho_from_vbses.copy()
        for value in vbses_info.values():
            if len(value["ues"]) <= self.min_ue:
                #
                #
                self.log.info("Condition: UEs < min_ue")
                self.log.info("    Removing...")
                #
                #
                del ho_from_vbses[value["vbs"].addr]

        # At most max_ho_from times, and while number of UEs >= min_ue, find
        # UEs and neighboring cells satisfying the handover conditions
        ue_ho_info = {}

        for svbs, sinfo in ho_from_vbses.items():

            for ue in ho_from_vbses[svbs]["ues"]:
                #
                #
                # self.log.info("{0}".format(ue))
                #
                #
                ho_flag = 0

                for tvbs, tinfo in ho_to_vbses.items():
                    #
                    #
                    # self.log.info("    {0}".format(tinfo))
                    #
                    #

                    if sinfo["max_ho_from"] >= self.max_ho_from:
                        #
                        #
                        self.log.info("Condition: source max_ho_from > given limit")
                        self.log.info("    {0} > {1}".format(sinfo["max_ho_from"], self.max_ho_from))
                        #
                        #
                        continue

                    if sinfo["num_ues"] <= self.min_ue:
                        #
                        #
                        self.log.info("Condition: num_ue < min_ue")
                        self.log.info("    {0} < {1}".format(sinfo["num_ues"], self.min_ue))
                        #
                        #
                        continue

                    if tinfo["max_ho_to"] >= self.max_ho_to:
                        #
                        #
                        self.log.info("Condition: target max_ho_to > given limit")
                        self.log.info("    {0} > {1}".format(tinfo["max_ho_to"], self.max_ho_to))
                        #
                        #
                        continue

                    for cell in tinfo["cells"]:

                        self.log.info("RRC ", ue.rrc_meas)

                        if (cell in ue.rrc_meas.keys()) and \
                            "rsrq" in ue.rrc_meas[cell] and \
                            ue.rrc_meas[cell]["rsrq"] > self.rsrq_thr:

                            ho_flag = 1
                            # UE is assumed to be connected to first cell in VBS
                            ue_ho_info[ue.addr] = {
                                                    "ue": ue,
                                                    "s_vbs": svbs,
                                                    "t_vbs": tvbs,
                                                    "s_cell": sinfo["cells"][0],
                                                    "t_cell": cell
                                                }
                            #
                            #
                            self.log.info("Condition: UE RRC RSRQ > RSRQ threshold")
                            self.log.info("    UE RNTI: ", ue.rnti)
                            self.log.info("    HO info: ", ue_ho_info[ue.addr])
                            #
                            #
                            break
                        else:
                            if (cell in ue.rrc_meas.keys()) and \
                            "rsrq" in ue.rrc_meas[cell]:
                                #
                                #
                                self.log.info("UE {0} RSRQ at {1}".format(ue.rnti, ue.rrc_meas[cell]["rsrq"]))
                                #
                                #

                    if ho_flag == 1:
                        tinfo["num_ues"] += 1
                        sinfo["num_ues"] -= 1
                        tinfo["max_ho_to"] += 1
                        sinfo["max_ho_from"] += 1
                        break

        # Handover the UEs
        for key, value in ue_ho_info.items():

            ho_param = {
                "src_vbs": value["s_vbs"].to_str(),
                "dst_vbs": value["t_vbs"].to_str(),
                "src_cell_id": value["s_cell"],
                "dst_cell_id": value["t_cell"],
                "cause": "resource_optimization"
            }
            #
            #
            self.log.info("Condition: Emitting HO")
            self.log.info("    HO parameters: ", ho_param)
            #
            #
            ue_handover(tenant_id=value["ue"].tenant.tenant_id,
                          ue=value["ue"].rnti,
                          ho_param=ho_param)

    def loop(self):
        """ Periodic job. """

        self.base_auth_usr = RUNTIME.accounts[self.tenant.owner].username
        self.base_auth_pwd = RUNTIME.accounts[self.tenant.owner].password

        if self.load_balance == True:
            self.load_balance_algo()

        node_id = 0
        # Contains all links between cells and UEs
        graph_links = []
        # Contains all nodes in the graph
        graph_nodes = {}

        tenant = RUNTIME.tenants[self.tenant.tenant_id]

        # Populate existing VBSes
        for vbs in self.tenant.vbses.values():
            if vbs.connection and vbs not in self.vbses:
                self.vbses.append(vbs)

        for vbs in self.vbses:

            cells = []
            stats = {}
            if vbs.cell_stats:
                for cell, stat in vbs.cell_stats.items():
                    cells.append(cell)
                    stats[cell] = {}

                    if "dl_prb_utilz" in stat and \
                        "perc_prbs" in stat["dl_prb_utilz"]:
                        stats[cell]["DL"] = \
                                    "%.2f" % stat["dl_prb_utilz"]["perc_prbs"]

                    if "ul_prb_utilz" in stat and \
                        "perc_prbs" in stat["ul_prb_utilz"]:
                        stats[cell]["UL"] = \
                                    "%.2f" % stat["ul_prb_utilz"]["perc_prbs"]

            if vbs.cells:
                for cell in vbs.cells:
                    if cell["phys_cell_id"] not in cells:
                        cells.append(cell["phys_cell_id"])

            graph_nodes["enb" + vbs.addr.to_str()] = \
                                            {
                                                "id": node_id,
                                                "node_id": vbs.enb_id,
                                                "vbs_id": vbs.addr.to_str(),
                                                "entity": "enb",
                                                "tooltip": "PCI",
                                                "cells": cells,
                                                "stats": stats,
                                                "x": self.coord[node_id][0],
                                                "y": self.coord[node_id][1]
                                            }
            node_id += 1

        for ue in tenant.ues.values():

            # Append the UE's info
            graph_nodes["ue" + ue.vbs.addr.to_str() + str(ue.rnti)] = \
                                            {
                                                "id": node_id,
                                                "node_id": ue.rnti,
                                                "vbs_id": ue.vbs.addr.to_str(),
                                                "entity": "ue",
                                                "tooltip": "RNTI",
                                                "x": self.coord[node_id][0],
                                                "y": self.coord[node_id][1]
                                            }

            # Index of UE in nodes array
            ue_index = node_id

            # Link between UE and serving eNB (VBS)
            graph_links.append({
                                    "src": graph_nodes["enb" + ue.vbs.addr.to_str()]["id"],
                                    "dst": ue_index,
                                    "rsrp": ue.pcell_rsrp,
                                    "rsrq": ue.pcell_rsrq,
                                    "color": "orange",
                                    "width": 6
                                })

            node_id += 1

            # Add each link for a measured neighbor cell
            measurements = ue.rrc_meas

            for key, m in measurements.items():
                for n_id, n_info in graph_nodes.items():
                    if "cells" in n_info and key in n_info["cells"]:
                        graph_links.append({
                                                "src": n_info["id"],
                                                "dst": ue_index,
                                                "rsrp": m["rsrp"],
                                                "rsrq": m["rsrq"],
                                                "entity": "lte",
                                                "color": "black",
                                                "width": 4
                                           })
                        break

        self.graphData = {
                            "nodes": graph_nodes.values(),
                            "links": graph_links
                          }

def launch(
            tenant_id,
            every=DEFAULT_PERIOD,
            load_balance=True,
            s_dl_thr=10,
            s_ul_thr=10,
            t_dl_thr=30,
            t_ul_thr=30,
            rsrq_thr=-20,
            min_ue=1,
            max_ho_from=1,
            max_ho_to=1):
    """ Initialize the module. """

    return HandoverManager(
                            tenant_id=tenant_id,
                            every=every,
                            load_balance=load_balance,
                            s_dl_thr=s_dl_thr,
                            s_ul_thr=s_ul_thr,
                            t_dl_thr=t_dl_thr,
                            t_ul_thr=t_ul_thr,
                            rsrq_thr=rsrq_thr,
                            min_ue=min_ue,
                            max_ho_from=max_ho_from,
                            max_ho_to=max_ho_to)
