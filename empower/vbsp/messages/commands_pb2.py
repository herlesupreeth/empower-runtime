# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: commands.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='commands.proto',
  package='',
  syntax='proto2',
  serialized_pb=_b('\n\x0e\x63ommands.proto\"\x87\x01\n\rctrl_handover\x12\x0c\n\x04rnti\x18\x01 \x02(\r\x12\x11\n\ts_cell_id\x18\x02 \x01(\x05\x12\x10\n\x08s_eNB_id\x18\x03 \x01(\r\x12\x11\n\tt_cell_id\x18\x04 \x01(\x05\x12\x10\n\x08t_eNB_id\x18\x05 \x02(\r\x12\x1e\n\x05\x63\x61use\x18\x06 \x02(\x0e\x32\x0f.handover_cause\"H\n\x17\x63ontroller_commands_req\x12!\n\x07\x63trl_ho\x18\x01 \x01(\x0b\x32\x0e.ctrl_handoverH\x00\x42\n\n\x08\x63trl_cmd\"@\n\x18\x63ontroller_commands_repl\x12$\n\ncmd_status\x18\x01 \x02(\x0e\x32\x10.ctrl_cmd_status\"\x82\x01\n\x13\x63ontroller_commands\x12\'\n\x03req\x18\x01 \x01(\x0b\x32\x18.controller_commands_reqH\x00\x12)\n\x04repl\x18\x02 \x01(\x0b\x32\x19.controller_commands_replH\x00\x42\x17\n\x15\x63ontroller_commands_m*D\n\x0ehandover_cause\x12\x14\n\x10HC_TIME_CRITICAL\x10\x00\x12\x1c\n\x18HC_RESOURCE_OPTIMIZATION\x10\x01*?\n\x0f\x63trl_cmd_status\x12\x15\n\x11\x43TRLCMDST_SUCCESS\x10\x00\x12\x15\n\x11\x43TRLCMDST_FAILURE\x10\x01')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_HANDOVER_CAUSE = _descriptor.EnumDescriptor(
  name='handover_cause',
  full_name='handover_cause',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='HC_TIME_CRITICAL', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='HC_RESOURCE_OPTIMIZATION', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=429,
  serialized_end=497,
)
_sym_db.RegisterEnumDescriptor(_HANDOVER_CAUSE)

handover_cause = enum_type_wrapper.EnumTypeWrapper(_HANDOVER_CAUSE)
_CTRL_CMD_STATUS = _descriptor.EnumDescriptor(
  name='ctrl_cmd_status',
  full_name='ctrl_cmd_status',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='CTRLCMDST_SUCCESS', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CTRLCMDST_FAILURE', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=499,
  serialized_end=562,
)
_sym_db.RegisterEnumDescriptor(_CTRL_CMD_STATUS)

ctrl_cmd_status = enum_type_wrapper.EnumTypeWrapper(_CTRL_CMD_STATUS)
HC_TIME_CRITICAL = 0
HC_RESOURCE_OPTIMIZATION = 1
CTRLCMDST_SUCCESS = 0
CTRLCMDST_FAILURE = 1



_CTRL_HANDOVER = _descriptor.Descriptor(
  name='ctrl_handover',
  full_name='ctrl_handover',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='rnti', full_name='ctrl_handover.rnti', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='s_cell_id', full_name='ctrl_handover.s_cell_id', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='s_eNB_id', full_name='ctrl_handover.s_eNB_id', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='t_cell_id', full_name='ctrl_handover.t_cell_id', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='t_eNB_id', full_name='ctrl_handover.t_eNB_id', index=4,
      number=5, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cause', full_name='ctrl_handover.cause', index=5,
      number=6, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=19,
  serialized_end=154,
)


_CONTROLLER_COMMANDS_REQ = _descriptor.Descriptor(
  name='controller_commands_req',
  full_name='controller_commands_req',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ctrl_ho', full_name='controller_commands_req.ctrl_ho', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='ctrl_cmd', full_name='controller_commands_req.ctrl_cmd',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=156,
  serialized_end=228,
)


_CONTROLLER_COMMANDS_REPL = _descriptor.Descriptor(
  name='controller_commands_repl',
  full_name='controller_commands_repl',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='cmd_status', full_name='controller_commands_repl.cmd_status', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=230,
  serialized_end=294,
)


_CONTROLLER_COMMANDS = _descriptor.Descriptor(
  name='controller_commands',
  full_name='controller_commands',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='req', full_name='controller_commands.req', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='repl', full_name='controller_commands.repl', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='controller_commands_m', full_name='controller_commands.controller_commands_m',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=297,
  serialized_end=427,
)

_CTRL_HANDOVER.fields_by_name['cause'].enum_type = _HANDOVER_CAUSE
_CONTROLLER_COMMANDS_REQ.fields_by_name['ctrl_ho'].message_type = _CTRL_HANDOVER
_CONTROLLER_COMMANDS_REQ.oneofs_by_name['ctrl_cmd'].fields.append(
  _CONTROLLER_COMMANDS_REQ.fields_by_name['ctrl_ho'])
_CONTROLLER_COMMANDS_REQ.fields_by_name['ctrl_ho'].containing_oneof = _CONTROLLER_COMMANDS_REQ.oneofs_by_name['ctrl_cmd']
_CONTROLLER_COMMANDS_REPL.fields_by_name['cmd_status'].enum_type = _CTRL_CMD_STATUS
_CONTROLLER_COMMANDS.fields_by_name['req'].message_type = _CONTROLLER_COMMANDS_REQ
_CONTROLLER_COMMANDS.fields_by_name['repl'].message_type = _CONTROLLER_COMMANDS_REPL
_CONTROLLER_COMMANDS.oneofs_by_name['controller_commands_m'].fields.append(
  _CONTROLLER_COMMANDS.fields_by_name['req'])
_CONTROLLER_COMMANDS.fields_by_name['req'].containing_oneof = _CONTROLLER_COMMANDS.oneofs_by_name['controller_commands_m']
_CONTROLLER_COMMANDS.oneofs_by_name['controller_commands_m'].fields.append(
  _CONTROLLER_COMMANDS.fields_by_name['repl'])
_CONTROLLER_COMMANDS.fields_by_name['repl'].containing_oneof = _CONTROLLER_COMMANDS.oneofs_by_name['controller_commands_m']
DESCRIPTOR.message_types_by_name['ctrl_handover'] = _CTRL_HANDOVER
DESCRIPTOR.message_types_by_name['controller_commands_req'] = _CONTROLLER_COMMANDS_REQ
DESCRIPTOR.message_types_by_name['controller_commands_repl'] = _CONTROLLER_COMMANDS_REPL
DESCRIPTOR.message_types_by_name['controller_commands'] = _CONTROLLER_COMMANDS
DESCRIPTOR.enum_types_by_name['handover_cause'] = _HANDOVER_CAUSE
DESCRIPTOR.enum_types_by_name['ctrl_cmd_status'] = _CTRL_CMD_STATUS

ctrl_handover = _reflection.GeneratedProtocolMessageType('ctrl_handover', (_message.Message,), dict(
  DESCRIPTOR = _CTRL_HANDOVER,
  __module__ = 'commands_pb2'
  # @@protoc_insertion_point(class_scope:ctrl_handover)
  ))
_sym_db.RegisterMessage(ctrl_handover)

controller_commands_req = _reflection.GeneratedProtocolMessageType('controller_commands_req', (_message.Message,), dict(
  DESCRIPTOR = _CONTROLLER_COMMANDS_REQ,
  __module__ = 'commands_pb2'
  # @@protoc_insertion_point(class_scope:controller_commands_req)
  ))
_sym_db.RegisterMessage(controller_commands_req)

controller_commands_repl = _reflection.GeneratedProtocolMessageType('controller_commands_repl', (_message.Message,), dict(
  DESCRIPTOR = _CONTROLLER_COMMANDS_REPL,
  __module__ = 'commands_pb2'
  # @@protoc_insertion_point(class_scope:controller_commands_repl)
  ))
_sym_db.RegisterMessage(controller_commands_repl)

controller_commands = _reflection.GeneratedProtocolMessageType('controller_commands', (_message.Message,), dict(
  DESCRIPTOR = _CONTROLLER_COMMANDS,
  __module__ = 'commands_pb2'
  # @@protoc_insertion_point(class_scope:controller_commands)
  ))
_sym_db.RegisterMessage(controller_commands)


# @@protoc_insertion_point(module_scope)
