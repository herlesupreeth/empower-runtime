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

"""RAN sharing Handler."""

import tornado.web

from empower.restserver.apihandlers import EmpowerAPIHandlerAdminUsers
from empower.datatypes.etheraddress import EtherAddress
from empower.core.utils import ether_to_hex
from empower.vbsp.vbspconnection import create_header
from empower.vbsp.messages import main_pb2
from empower.vbsp.messages import ran_sharing_pb2

from empower.main import RUNTIME


class RANSharingHandler(EmpowerAPIHandlerAdminUsers):
    """RAN sharing Handler."""

    HANDLERS = [(r"/api/v1/vbses/([a-zA-Z0-9:]*)/ran_sharing/?")]

    def initialize(self, server):
        self.server = server

    def get(self, *args, **kwargs):
        """List next associations.

        Args:
            [0]: the vbs id

        Example URLs:

            GET /api/v1/vbses/00:00:00:00:0E:21/ran_sharing
        """

        try:

            if len(args) < 1:
                raise ValueError("Invalid url")

            vbs_id = EtherAddress(args[0])

            if vbs_id not in RUNTIME.vbses:
                raise ValueError("Invalid VBS Id")

            vbs = RUNTIME.vbses[vbs_id]

            self.write_as_json(vbs.ran_sh_i)

        except ValueError as ex:
            self.send_error(400, message=ex)
        except KeyError as ex:
            self.send_error(404, message=ex)

        self.set_status(200, None)

    def post(self, *args, **kwargs):
        """Control RAN sharing in VBS.

        Args:
            [0]: the vbs id

        Example URLs:

            POST /api/v1/vbses/00:00:00:00:0E:21/ran_sharing
        """

        try:

            if len(args) < 1:
                raise ValueError("Invalid url")

            vbs_id = EtherAddress(args[0])

            if vbs_id not in RUNTIME.vbses:
                raise ValueError("Invalid VBS Id")

            vbs = RUNTIME.vbses[vbs_id]

            request = tornado.escape.json_decode(self.request.body)

            if "version" not in request:
                raise ValueError("missing version element")

            if "operation" not in request:
                raise ValueError("missing operation element")

            ran_sh_ctrl_req = main_pb2.emage_msg()

            enb_id = ether_to_hex(vbs.addr)
            # Transaction identifier is zero by default for single event request
            create_header(0, enb_id, ran_sh_ctrl_req.head)

            # Creating a single event message to control RAN sharing in VBS
            se_msg = ran_sh_ctrl_req.se

            ran_sh_ctrl_msg = se_msg.mRAN_sharing_ctrl
            ran_sh_ctrl_req_msg = ran_sh_ctrl_msg.req

            # For now support only static RBS allocation to tenants
            if request["operation"] == "static_t_alloc_DL":

                static_sched_dl = ran_sh_ctrl_req_msg.t_sched_sel.static_sched_dl

                if "params" not in request:
                    raise ValueError("missing params element")

                if "rbs_alloc_dl" not in request["params"]:
                    raise ValueError("missing rbs_alloc_dl element")

                alloc = request["params"]["rbs_alloc_dl"]

                if "phy_cell_id" not in alloc:
                    raise ValueError("missing phy_cell_id element")

                if "sf" not in alloc:
                    raise ValueError("missing sf element")

                cell = ran_sharing_pb2.rbs_alloc_per_cell()
                cell.phys_cell_id = alloc["phy_cell_id"]

                for sf_alloc in alloc["sf"]:
                    sf = ran_sharing_pb2.rbs_alloc_over_sf()
                    sf.rbs_alloc.extend(sf_alloc["rbs_alloc"])
                    cell.sf.extend([sf])

                static_sched_dl.cell.extend([cell])

            else:
                raise ValueError("unknown operation element")

            if not vbs.connection:
               raise ValueError("VBS not in connected state")

            vbs.connection.stream_send(ran_sh_ctrl_req)

            url = "/api/v1/vbses/%s/ran_sharing"
            tokens = (vbs_id)

            self.set_header("Location", url % tokens)

        except ValueError as ex:
            self.send_error(400, message=ex)
        except KeyError as ex:
            self.send_error(404, message=ex)

        self.set_status(201, None)

