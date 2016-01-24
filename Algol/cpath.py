#!/usr/bin/env python
# Copyright (c) 2015 Angel Terrones (<angelterrones@gmail.com>)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from myhdl import Signal
from myhdl import always
from myhdl import always_comb
from myhdl import modbv
from myhdl import instances
from myhdl import concat
from consts import Consts
from alu import ALUFunction
from memIO import MemPortIO
from memIO import MemoryOpConstant
from csr import CSRCommand
from csr import CSRExceptionCode
from csr import CSRModes


class CtrlSignals:
    # Control signals
    #                  Illegal                                                                 Valid memory operation                                                                    OP1 select
    #                  |      ecall                                                            |      Memory Function (type)                                                             |                OP2 select
    #                  |      |      ebreak                                                    |      |                      Memory type                                                 |                |                Branch/Jump
    #                  |      |      |      eret                                               |      |                      |                       ALU operation                       |                |                |
    #                  |      |      |      |      RF WE                                       |      |                      |                       |                    IMM type       |                |                |
    #                  |      |      |      |      |      Sel dat to WB                        |      |                      |                       |                    |              |                |                |
    #                  |      |      |      |      |      |              CSR command           |      |                      |                       |                    |              |                |                |
    #                  |      |      |      |      |      |              |                     |      |                      |                       |                    |              |                |                |
    #                  |      |      |      |      |      |              |                     |      |                      |                       |                    |              |                |                |
    #                  |      |      |      |      |      |              |                     |      |                      |                       |                    |              |                |                |
    NOP       = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_X,    Consts.OP2_X,    Consts.BR_N)
    INVALID   = concat(True,  False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_X,    Consts.OP2_X,    Consts.BR_N)

    LUI       = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_U,  Consts.OP1_ZERO, Consts.OP2_ZERO, Consts.BR_N)
    AUIPC     = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_U,  Consts.OP1_PC,   Consts.OP2_IMM,  Consts.BR_N)

    JAL       = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_UJ, Consts.OP1_PC,   Consts.OP2_FOUR, Consts.BR_N)
    JALR      = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_I,  Consts.OP1_PC,   Consts.OP2_FOUR, Consts.BR_N)
    BEQ       = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_SB, Consts.OP1_X,    Consts.OP2_X,    Consts.BR_EQ)
    BNE       = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_SB, Consts.OP1_X,    Consts.OP2_X,    Consts.BR_NE)
    BLT       = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_SB, Consts.OP1_X,    Consts.OP2_X,    Consts.BR_LT)
    BGE       = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_SB, Consts.OP1_X,    Consts.OP2_X,    Consts.BR_GE)
    BLTU      = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_SB, Consts.OP1_X,    Consts.OP2_X,    Consts.BR_LTU)
    BGEU      = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_SB, Consts.OP1_X,    Consts.OP2_X,    Consts.BR_GEU)

    LB        = concat(False, False, False, False, True,  Consts.WB_MEM, CSRCommand.CSR_IDLE,  True,  MemoryOpConstant.M_RD, MemoryOpConstant.MT_B,  ALUFunction.OP_ADD,  Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    LH        = concat(False, False, False, False, True,  Consts.WB_MEM, CSRCommand.CSR_IDLE,  True,  MemoryOpConstant.M_RD, MemoryOpConstant.MT_H,  ALUFunction.OP_ADD,  Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    LW        = concat(False, False, False, False, True,  Consts.WB_MEM, CSRCommand.CSR_IDLE,  True,  MemoryOpConstant.M_RD, MemoryOpConstant.MT_W,  ALUFunction.OP_ADD,  Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    LBU       = concat(False, False, False, False, True,  Consts.WB_MEM, CSRCommand.CSR_IDLE,  True,  MemoryOpConstant.M_RD, MemoryOpConstant.MT_BU, ALUFunction.OP_ADD,  Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    LHU       = concat(False, False, False, False, True,  Consts.WB_MEM, CSRCommand.CSR_IDLE,  True,  MemoryOpConstant.M_RD, MemoryOpConstant.MT_HU, ALUFunction.OP_ADD,  Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    SB        = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  True,  MemoryOpConstant.M_WR, MemoryOpConstant.MT_B,  ALUFunction.OP_ADD,  Consts.IMM_S,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    SH        = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  True,  MemoryOpConstant.M_WR, MemoryOpConstant.MT_H,  ALUFunction.OP_ADD,  Consts.IMM_S,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    SW        = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  True,  MemoryOpConstant.M_WR, MemoryOpConstant.MT_W,  ALUFunction.OP_ADD,  Consts.IMM_S,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)

    ADDI      = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    SLTI      = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_SLT,  Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    SLTIU     = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_SLTU, Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    XORI      = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_XOR,  Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    ORI       = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_OR,   Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    ANDI      = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_AND,  Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    SLLI      = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_SLL,  Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    SRLI      = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_SRL,  Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)
    SRAI      = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_SRA,  Consts.IMM_I,  Consts.OP1_RS1,  Consts.OP2_IMM,  Consts.BR_N)

    ADD       = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_RS1,  Consts.OP2_RS2,  Consts.BR_N)
    SUB       = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_SUB,  Consts.IMM_X,  Consts.OP1_RS1,  Consts.OP2_RS2,  Consts.BR_N)
    SLL       = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_SLL,  Consts.IMM_X,  Consts.OP1_RS1,  Consts.OP2_RS2,  Consts.BR_N)
    SLT       = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_SLT,  Consts.IMM_X,  Consts.OP1_RS1,  Consts.OP2_RS2,  Consts.BR_N)
    SLTU      = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_SLTU, Consts.IMM_X,  Consts.OP1_RS1,  Consts.OP2_RS2,  Consts.BR_N)
    XOR       = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_XOR,  Consts.IMM_X,  Consts.OP1_RS1,  Consts.OP2_RS2,  Consts.BR_N)
    SRL       = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_SRL,  Consts.IMM_X,  Consts.OP1_RS1,  Consts.OP2_RS2,  Consts.BR_N)
    SRA       = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_SRA,  Consts.IMM_X,  Consts.OP1_RS1,  Consts.OP2_RS2,  Consts.BR_N)
    OR        = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_OR,   Consts.IMM_X,  Consts.OP1_RS1,  Consts.OP2_RS2,  Consts.BR_N)
    AND       = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_AND,  Consts.IMM_X,  Consts.OP1_RS1,  Consts.OP2_RS2,  Consts.BR_N)

    FENCE     = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_X,    Consts.OP2_X,    Consts.BR_N)
    FENCE_I   = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_X,    Consts.OP2_X,    Consts.BR_N)

    CSRRW     = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_WRITE, False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_CSR,  Consts.OP2_ZERO, Consts.BR_N)
    CSRRS     = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_SET,   False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_CSR,  Consts.OP2_ZERO, Consts.BR_N)
    CSRRC     = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_CLEAR, False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_CSR,  Consts.OP2_ZERO, Consts.BR_N)
    CSRRWI    = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_WRITE, False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_CSR,  Consts.OP2_ZERO, Consts.BR_N)
    CSRRSI    = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_SET,   False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_CSR,  Consts.OP2_ZERO, Consts.BR_N)
    CSRRCI    = concat(False, False, False, False, True,  Consts.WB_ALU, CSRCommand.CSR_CLEAR, False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_CSR,  Consts.OP2_ZERO, Consts.BR_N)

    ECALL     = concat(False, True,  False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_X,    Consts.OP2_X,    Consts.BR_N)
    EBREAK    = concat(False, False, True,  False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_X,    Consts.OP2_X,    Consts.BR_N)
    ERET      = concat(False, False, False, True,  False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_X,    Consts.OP2_X,    Consts.BR_N)

    MRTS      = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_X,    Consts.OP2_X,    Consts.BR_N)
    MRTH      = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_X,    Consts.OP2_X,    Consts.BR_N)
    HRTS      = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_X,    Consts.OP2_X,    Consts.BR_N)
    WFI       = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_X,    Consts.OP2_X,    Consts.BR_N)
    SFENCE_VM = concat(False, False, False, False, False, Consts.WB_X,   CSRCommand.CSR_IDLE,  False, MemoryOpConstant.M_X,  MemoryOpConstant.MT_X,  ALUFunction.OP_ADD,  Consts.IMM_X,  Consts.OP1_X,    Consts.OP2_X,    Consts.BR_N)


class CtrlIO:
    def __init__(self):
        self.id_instruction     = Signal(modbv(0)[32:])
        self.if_kill            = Signal(False)
        self.id_stall           = Signal(False)
        self.id_kill            = Signal(False)
        self.full_stall         = Signal(False)
        self.pipeline_kill      = Signal(False)
        self.pc_select          = Signal(modbv(0)[Consts.SZ_PC_SEL])
        self.id_op1_select      = Signal(modbv(0)[Consts.SZ_OP1])
        self.id_op2_select      = Signal(modbv(0)[Consts.SZ_OP2])
        self.id_sel_imm         = Signal(modbv(0)[Consts.SZ_IMM])
        self.id_alu_funct       = Signal(modbv(0)[ALUFunction.SZ_OP])
        self.id_mem_type        = Signal(modbv(0)[MemoryOpConstant.SZ_MT])
        self.id_mem_funct       = Signal(modbv(0)[MemoryOpConstant.SZ_M])
        self.id_mem_valid       = Signal(False)
        self.id_csr_cmd         = Signal(modbv(0)[CSRCommand.SZ_CMD])
        self.id_mem_data_sel    = Signal(modbv(0)[Consts.SZ_WB])
        self.id_wb_we           = Signal(False)
        self.id_fwd1_select     = Signal(modbv(0)[Consts.SZ_FWD])
        self.id_fwd2_select     = Signal(modbv(0)[Consts.SZ_FWD])
        self.id_rs1_addr        = Signal(modbv(0)[5:])
        self.id_rs2_addr        = Signal(modbv(0)[5:])
        self.id_op1             = Signal(modbv(0)[32:])
        self.id_op2             = Signal(modbv(0)[32:])
        self.ex_wb_addr         = Signal(modbv(0)[5:])
        self.ex_wb_we           = Signal(False)
        self.mem_wb_addr        = Signal(modbv(0)[5:])
        self.mem_wb_we          = Signal(False)
        self.wb_wb_addr         = Signal(modbv(0)[5:])
        self.wb_wb_we           = Signal(False)
        self.csr_eret           = Signal(False)
        self.csr_prv            = Signal(modbv(0)[CSRModes.SZ_MODE:])
        self.csr_illegal_access = Signal(False)
        self.csr_interrupt      = Signal(False)
        self.csr_interrupt_code = Signal(modbv(0)[CSRExceptionCode.SZ_ECODE:])
        self.csr_exception      = Signal(False)
        self.csr_exception_code = Signal(modbv(0)[CSRExceptionCode.SZ_ECODE:])
        self.csr_retire         = Signal(False)
        self.imem_pipeline      = MemPortIO()
        self.dmem_pipeline      = MemPortIO()


class Ctrlpath:
    def __init__(self,
                 clk:  Signal,
                 rst:  Signal,
                 io:   CtrlIO,
                 imem: MemPortIO,
                 dmem: MemPortIO):
        self.clk                = clk
        self.rst                = rst
        self.io                 = io
        self.imem               = imem
        self.dmem               = dmem

        self.id_br_type         = Signal(modbv(0)[Consts.SZ_BR])
        self.id_eq              = Signal(False)
        self.id_lt              = Signal(False)
        self.id_ltu             = Signal(False)

        self.id_eret            = Signal(False)
        self.id_ebreak          = Signal(False)
        self.id_ecall           = Signal(False)
        # Exception sources
        self.if_imem_misalign   = Signal(False)
        self.if_imem_fault      = Signal(False)
        self.id_illegal_inst    = Signal(False)
        self.id_breakpoint      = Signal(False)
        self.id_ecall_u         = Signal(False)
        self.id_ecall_s         = Signal(False)
        self.id_ecall_h         = Signal(False)
        self.id_ecall_m         = Signal(False)
        self.mem_ld_misalign    = Signal(False)
        self.mem_ld_fault       = Signal(False)
        self.mem_st_misalign    = Signal(False)
        self.mem_st_fault       = Signal(False)
        #  Auxiliary signals
        self.id_imem_misalign   = Signal(False)
        self.id_imem_fault      = Signal(False)
        self.ex_exception       = Signal(False)
        self.ex_exception_code  = Signal(modbv(0)[CSRExceptionCode.SZ_ECODE])
        self.ex_mem_funct       = Signal(modbv(0)[MemoryOpConstant.SZ_M])
        self.mem_exception      = Signal(False)
        self.mem_exception_code = Signal(modbv(0)[CSRExceptionCode.SZ_ECODE])
        self.control            = Signal(modbv(0)[28:])

    def CheckInvalidAddress(addr, mem_type):
        return (addr[0] if mem_type == MemoryOpConstant.MT_H or mem_type == MemoryOpConstant.MT_HU else
                (addr[0] or addr[1] if mem_type == MemoryOpConstant.MT_W else
                 (False)))

    def GetRTL(self):
        @always_comb
        def _ctrl_assignment():
            self.control.next = self.io.id_instruction[29:]

        @always_comb
        def _assignments():
            self.id_br_type.next         = self.control[2:0]
            self.io.id_op1_select.next   = self.control[4:2]
            self.io.id_op2_select.next   = self.control[6:4]
            self.io.id_sel_imm.next      = self.control[9:6]
            self.io.id_alu_funct.next    = self.control[13:9]
            self.io.id_mem_type.next     = self.control[16:13]
            self.io.id_mem_funct.next    = self.control[16]
            self.io.id_mem_valid.next    = self.control[17]
            self.io.id_csr_cmd.next      = self.control[21:18] if self.io.id_rs1_addr != 0 else CSRCommand.CSR_READ
            self.io.id_mem_data_sel.next = self.control[23:21]
            self.io.id_wb_we.next        = self.control[23]
            self.id_eret.next            = self.control[24]
            self.id_ebreak.next          = self.control[25]
            self.id_ecall.next           = self.control[26]

        @always_comb
        def _assignments2():
            self.io.csr_retire.next      = not self.io.full_stall and not self.io.csr_exception
            self.io.csr_eret.next        = self.id_eret and self.io.csr_prv != CSRModes.PRV_U

        @always_comb
        def _exc_assignments():
            self.if_imem_misalign.next = self.CheckInvalidAddress(self.io.imem_pipeline.req.addr,
                                                                  self.io.imem_pipeline.req.typ)
            self.if_imem_fault.next    = self.imem.resp.fault
            self.id_illegal_inst.next  = self.control[27] or (self.io.csr_prv == CSRModes.PRV_U and self.id_eret) or self.io.csr_illegal_access
            self.id_breakpoint.next    = self.id_ebreak
            self.id_ecall_u.next       = self.io.csr_prv == CSRModes.PRV_U and self.id_ecall
            self.id_ecall_s.next       = self.io.csr_prv == CSRModes.PRV_S and self.id_ecall
            self.id_ecall_h.next       = self.io.csr_prv == CSRModes.PRV_H and self.id_ecall
            self.id_ecall_m.next       = self.io.csr_prv == CSRModes.PRV_M and self.id_ecall
            self.mem_ld_misalign.next  = (self.io.dmem_pipeline.req.valid and
                                          self.io.dmem_pipeline.req.fcn == MemoryOpConstant.M_RD and
                                          self.CheckInvalidAddress(self.io.dmem_pipeline.req.addr,
                                                                   self.io.dmem_pipeline.req.typ))
            self.mem_ld_fault.next     = self.dmem.resp.fault
            self.mem_st_misalign.next  = (self.io.dmem_pipeline.req.valid and
                                          self.io.dmem_pipeline.req.fcn == MemoryOpConstant.M_WR and
                                          self.CheckInvalidAddress(self.io.dmem_pipeline.req.addr,
                                                                   self.io.dmem_pipeline.req.typ))
            self.mem_st_fault.next     = self.dmem.resp.fault

        @always(self.clk.posedge)
        def _ifid_register():
            if self.rst:
                self.id_imem_fault.next    = False
                self.id_imem_misalign.next = False
            else:
                if self.io.pipeline_kill or self.io.if_kill:
                    self.id_imem_fault.next    = False
                    self.id_imem_misalign.next = False
                elif not self.io.id_stall and not self.io.full_stall:
                    self.id_imem_fault.next    = self.if_imem_fault
                    self.id_imem_misalign.next = self.if_imem_misalign

        @always(self.clk.posedge)
        def _idex_register():
            if self.rst:
                self.ex_exception.next      = False
                self.ex_exception_code.next = CSRExceptionCode.E_ILLEGAL_INST
                self.ex_mem_funct.next      = MemoryOpConstant.M_X
            else:
                if self.io.pipeline_kill or self.io.id_kill or (self.io.id_stall and not self.io.full_stall):
                    self.ex_exception.next      = False
                    self.ex_exception_code.next = CSRExceptionCode.E_ILLEGAL_INST
                    self.ex_mem_funct.next      = MemoryOpConstant.M_X
                elif not self.io.id_stall and not self.io.full_stall:
                    self.ex_exception.next      = (self.id_imem_misalign or self.id_imem_fault or self.id_illegal_inst or
                                                   self.id_breakpoint or self.id_ecall_u or self.id_ecall_s or self.id_ecall_h or
                                                   self.id_ecall_m or self.csr_interrupt)
                    self.ex_exception_code.next = (self.csr_interrupt_code if self.csr_interrupt else
                                                   (CSRExceptionCode.E_INST_ADDR_MISALIGNED if self.id_imem_misalign else
                                                    (CSRExceptionCode.E_INST_ACCESS_FAULT if self.id_imem_fault else
                                                     (CSRExceptionCode.E_ILLEGAL_INST if self.id_illegal_inst else
                                                      (CSRExceptionCode.E_BREAKPOINT if self.id_breakpoint else
                                                       (CSRExceptionCode.E_ECALL_FROM_U if self.id_ecall_u else
                                                        (CSRExceptionCode.E_ECALL_FROM_S if self.id_ecall_s else
                                                         (CSRExceptionCode.E_ECALL_FROM_H if self.id_ecall_h else
                                                          (CSRExceptionCode.E_ECALL_FROM_M if self.id_ecall_m else
                                                           (CSRExceptionCode.E_ILLEGAL_INST))))))))))
                    self.ex_mem_funct.next      = self.io.id_mem_funct

        @always(self.clk.posedge)
        def _exmem_register():
            if self.rst:
                self.mem_exception.next      = False
                self.mem_exception_code.next = CSRExceptionCode.E_ILLEGAL_INST
            else:
                if self.io.pipeline_kill:
                    self.mem_exception.next      = False
                    self.mem_exception_code.next = CSRExceptionCode.E_ILLEGAL_INST
                elif not self.io.full_stall:
                    self.mem_exception.next      = (self.ex_exception or self.mem_ld_misalign or self.mem_ld_fault or
                                                    self.mem_st_misalign or self.mem_st_fault)
                    self.mem_exception_code.next = (self.ex_exception if self.ex_exception else
                                                    (CSRExceptionCode.E_AMO_ADDR_MISALIGNED if self.mem_ld_misalign else
                                                     (CSRExceptionCode.E_AMO_ACCESS_FAULT if self.mem_ld_fault else
                                                      (CSRExceptionCode.E_LOAD_ADDR_MISALIGNED if self.mem_st_misalign else
                                                       (CSRExceptionCode.E_LOAD_ACCESS_FAULT if self.mem_st_fault else
                                                        (self.ex_exception))))))

        @always_comb
        def _branch_detect():
            self.id_eq.next  = self.io.id_op1 == self.io.id_op2
            self.id_lt.next  = self.io.id_op1.signed() < self.io.id_op2.signed()
            self.id_ltu.next = self.io.id_op1 < self.io.id_op2

        @always_comb
        def _pc_select():
            self.io.pc_select.next = (Consts.PC_EXC if self.io.csr_exception or self.io.csr_eret else
                                      (Consts.PC_BRJMP if ((self.id_br_type == Consts.BR_NE and not self.id_eq) or
                                                           (self.id_br_type == Consts.BR_EQ and self.id_eq) or
                                                           (self.id_br_type == Consts.BR_LT and self.id_lt) or
                                                           (self.id_br_type == Consts.BR_LTU and self.id_ltu) or
                                                           (self.id_br_type == Consts.BR_GE and not self.id_lt) or
                                                           (self.id_br_type == Consts.BR_GEU and not self.id_ltu)) else
                                       (Consts.PC_JALR if self.id_br_type == Consts.BR_J else
                                        (Consts.PC_4))))

        @always_comb
        def _fwd_ctrl():
            self.io.id_fwd1_select.next = (Consts.FWD_EX if self.io.id_rs1_addr == self.io.ex_wb_addr and self.io.ex_wb_we else
                                           (Consts.FWD_MEM if self.io.id_rs1_addr == self.io.mem_wb_addr and self.io.mem_wb_we else
                                            (Consts.FWD_WB if self.io.id_rs1_addr == self.io.wb_wb_addr and self.io.wb_wb_we else
                                             Consts.FWD_N)))
            self.io.id_fwd2_select.next = (Consts.FWD_EX if self.io.id_rs2_addr == self.io.ex_wb_addr and self.io.ex_wb_we else
                                           (Consts.FWD_MEM if self.io.id_rs2_addr == self.io.mem_wb_addr and self.io.mem_wb_we else
                                            (Consts.FWD_WB if self.io.id_rs2_addr == self.io.wb_wb_addr and self.io.wb_wb_we else
                                             (Consts.FWD_N))))

        @always_comb
        def _ctrl_pipeline():
            self.io.if_kill.next       = self.io.pc_select != Consts.PC_4
            self.io.id_stall.next      = self.io.id_fwd1_select == Consts.FWD_EX and self.ex_mem_funct == MemoryOpConstant.M_WR
            self.io.id_kill.next       = False
            self.io.full_stall.next    = self.imem.req.valid or self.dmem.req.valid
            self.io.pipeline_kill.next = self.io.csr_exception

        @always_comb
        def _exc_detect():
            self.io.csr_exception.next      = self.mem_exception
            self.io.csr_exception_code.next = self.mem_exception_code

        @always_comb
        def _imem_assignment():
            self.imem.req.addr.next              = self.io.imem_pipeline.req.addr & ~0x03
            self.imem.req.data.next              = self.io.imem_pipeline.req.data
            self.imem.req.fcn.next               = self.io.imem_pipeline.req.fcn
            self.imem.req.typ.next               = self.io.imem_pipeline.req.typ
            self.io.imem_pipeline.resp.data.next = self.imem.resp.data

        @always_comb
        def _imem_control():
            self.imem.req.valid.next = (self.io.imem_pipeline.req.valid and (not self.imem.resp.valid) and
                                        not self.csr_exception)

        @always_comb
        def _dmem_assignment():
            self.dmem.req.addr.next              = self.io.dmem_pipeline.req.addr
            self.dmem.req.data.next              = self.io.dmem_pipeline.req.data
            self.dmem.req.fcn.next               = self.io.dmem_pipeline.req.fcn
            self.dmem.req.typ.next               = self.io.dmem_pipeline.req.typ
            self.io.dmem_pipeline.resp.data.next = self.dmem.resp.data

        @always_comb
        def _dmem_control():
            self.dmem.req.valid.next = (self.io.dmem_pipeline.req.valid and (not self.dmem.resp.valid) and
                                        not self.csr_exception)

        return instances()

# Local Variables:
# flycheck-flake8-maximum-line-length: 300
# flycheck-flake8rc: ".flake8rc"
# End:
