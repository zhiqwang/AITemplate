#  Copyright (c) Meta Platforms, Inc. and affiliates.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

"""
Common codegen functions for gemm_bias_activation.
"""

from . import common, common_bias, gemm_rcr
from .layout import RCR

# pylint: disable=C0103,C0415,W0613,C0301,R1705,R1703


def gemm_rcr_config(func_attrs, dtype="float16"):
    common.make_fproc_f16(func_attrs, RCR)


def gen_profiler(
    func_attrs,
    workdir,
    dim_info_dict,
    problem_args_template,
    extra_code="",
):
    gemm_rcr.common_gen_profiler(
        func_attrs,
        workdir,
        dim_info_dict,
        common_bias.SRC_TEMPLATE,
        problem_args_template,
        bias_ptr_arg="memory_pool->RequestHalfTensorByIdx(3)",
        extra_code=extra_code,
    )


def gen_function(
    func_attrs,
    problem_args_template,
    exec_cond_template,
    dim_info_dict,
    extra_code="",
):
    input_ndims = len(func_attrs["input_accessors"][0].original_shapes)
    weight_ndims = len(func_attrs["input_accessors"][1].original_shapes)
    output_ndims = len(func_attrs["output_accessors"][0].original_shapes)
    problem_args = problem_args_template.render()
    return common.gen_function(
        func_attrs,
        common_bias.SRC_TEMPLATE,
        exec_cond_template,
        problem_args,
        input_ndims,
        weight_ndims,
        output_ndims,
        dim_info_dict,
        support_split_k=True,
        output_addr_calculator=common.OUTPUT_ADDR_CALCULATOR.render(
            stride_dim="N",
            output_accessor=func_attrs["output_accessors"][0],
        ),
        extra_code=extra_code,
    )


def gen_function_decl(func_attrs):
    func_name = func_attrs["name"]
    input_ndims = len(func_attrs["input_accessors"][0].original_shapes)
    weight_ndims = len(func_attrs["input_accessors"][1].original_shapes)
    return common_bias.FUNC_DECL_TEMPLATE.render(
        func_name=func_name,
        input_ndims=input_ndims,
        weight_ndims=weight_ndims,
        support_split_k=True,
    )


def gen_function_call(func_attrs, indent="  "):
    bias = func_attrs["inputs"][2]
    return common.gen_function_call(
        func_attrs, indent, bias_ptr_arg=bias._attrs["name"]
    )
