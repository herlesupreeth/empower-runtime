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

"""VBSP Server module."""

from empower.vbsp.messages import commands_pb2

EMAGE_VERSION = 1

MAX_NUM_CCS = 1

# Every 5 seconds
UE_RRC_STATS_REPORT_INTERVAL = 5

PRT_UE_JOIN = "join"
PRT_UE_LEAVE = "leave"
PRT_VBSP_BYE = "bye"
PRT_VBSP_REGISTER = "register"
PRT_VBSP_TRIGGER_EVENT = "te"
PRT_VBSP_AGENT_SCHEDULED_EVENT = "sche"
PRT_VBSP_SINGLE_EVENT = "se"
PRT_VBSP_HELLO = "mHello"
PRT_VBSP_UES_ID = "mUEs_id"
PRT_UE_RRC_MEAS_CONF = "mUE_rrc_meas_conf"
PRT_VBSP_CELLS_CONF = "mENB_cells"
PRT_CTRL_COMMANDS = "mCtrl_cmds"
PRT_RAN_SHARE_CTRL = "mRAN_sharing_ctrl"

PRT_TYPES = {PRT_VBSP_BYE: None,
             PRT_VBSP_REGISTER: None,
             PRT_UE_JOIN: None,
             PRT_UE_LEAVE: None,
             PRT_VBSP_HELLO: "hello",
             PRT_VBSP_UES_ID: "ues_id_repl",
             PRT_UE_RRC_MEAS_CONF: None,
             PRT_VBSP_CELLS_CONF: "vbs_cells_conf_repl",
             PRT_RAN_SHARE_CTRL: None}


PRT_TYPES_HANDLERS = {PRT_VBSP_BYE: [],
                      PRT_VBSP_REGISTER: [],
                      PRT_UE_JOIN: [],
                      PRT_UE_LEAVE: [],
                      PRT_VBSP_HELLO: [],
                      PRT_VBSP_UES_ID: []}

UE_HANDOVER_CAUSE = {
    "time_critical": commands_pb2.HC_TIME_CRITICAL,
    "resource_optimization": commands_pb2.HC_RESOURCE_OPTIMIZATION
}
