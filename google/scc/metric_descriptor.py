# Copyright 2016, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""metric_descriptor provides funcs for working with `MetricDescriptor` instances.

:class:`KnownMetrics` is an :class:`enum.Enum` that defines the list of known
`MetricDescriptor` instances.  It is a complex enumeration that includes various
attributes including

- the full metric name
- the kind of the metric
- the value type of the metric
- a func for updating :class:`Operation`s from a `ReportRequestInfo`

"""

from __future__ import absolute_import

import google.apigen.servicecontrol_v1_messages as messages

from enum import Enum
from . import distribution, MetricKind, ValueType
from .aggregators import metric_value


def _add_metric_value(name, value, an_op):
    an_op.metricValueSets.append(
        messages.MetricValueSet(metricName=name, metricValues=[value]))


def _add_int64_metric_value(name, value, an_op):
    _add_metric_value(
        name, metric_value.create(int64Value=value), an_op)


def _set_int64_metric_to_constant_1(name, dummy_info, op):
    _add_int64_metric_value(name, 1, op)


def _set_int64_metric_to_constant_1_if_http_error(name, info, op):
    if info.response_code >= 400:
        _add_int64_metric_value(name, 1, op)


def _add_distribution_metric_value(name, value, an_op, distribution_args):
    d = distribution.create_exponential(*distribution_args)
    distribution.add_sample(value, d)
    _add_metric_value(
        name, metric_value.create(distributionValue=d), an_op)


_SIZE_DISTRIBUTION_ARGS = (8, 10.0, 1e6)


def _set_distribution_metric_to_request_size(name, info, an_op):
    if info.request_size >= 0:
        _add_distribution_metric_value(name, info.request_size, an_op,
                                       _SIZE_DISTRIBUTION_ARGS)


def _set_distribution_metric_to_response_size(name, info, an_op):
    if info.response_size >= 0:
        _add_distribution_metric_value(name, info.response_size, an_op,
                                       _SIZE_DISTRIBUTION_ARGS)


_TIME_DISTRIBUTION_ARGS = (8, 10.0, 1)


def _set_distribution_metric_to_request_time(name, info, an_op):
    if info.request_time:
        _add_distribution_metric_value(name, info.request_time.seconds, an_op,
                                       _TIME_DISTRIBUTION_ARGS)


def _set_distribution_metric_to_backend_time(name, info, an_op):
    if info.backend_time:
        _add_distribution_metric_value(name, info.backend_time.seconds, an_op,
                                       _TIME_DISTRIBUTION_ARGS)


def _set_distribution_metric_to_overhead_time(name, info, an_op):
    if info.overhead_time:
        _add_distribution_metric_value(name, info.overhead_time.seconds, an_op,
                                       _TIME_DISTRIBUTION_ARGS)


class KnownMetrics(Enum):
    """Enumerates the known metrics."""

    CONSUMER_REQUEST_COUNT = (
        'serviceruntime.googleapis.com/api/consumer/request_count',
        MetricKind.DELTA,
        ValueType.INT64,
        _set_int64_metric_to_constant_1,
    )
    PRODUCER_REQUEST_COUNT = (
        'serviceruntime.googleapis.com/api/producer/request_count',
        MetricKind.DELTA,
        ValueType.INT64,
        _set_int64_metric_to_constant_1,
    )
    PRODUCER_BY_CONSUMER_REQUEST_COUNT = (
        'serviceruntime.googleapis.com/api/producer/by_consumer/request_count',
        MetricKind.DELTA,
        ValueType.INT64,
        _set_int64_metric_to_constant_1,
    )
    CONSUMER_REQUEST_SIZES = (
        'serviceruntime.googleapis.com/api/consumer/request_sizes',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_request_size,
    )
    PRODUCER_REQUEST_SIZES = (
        'serviceruntime.googleapis.com/api/producer/request_sizes',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_request_size,
    )
    PRODUCER_BY_CONSUMER_REQUEST_SIZES = (
        'serviceruntime.googleapis.com/api/producer/by_consumer/request_sizes',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_request_size,
    )
    CONSUMER_RESPONSE_SIZES = (
        'serviceruntime.googleapis.com/api/consumer/response_sizes',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_response_size,
    )
    PRODUCER_RESPONSE_SIZES = (
        'serviceruntime.googleapis.com/api/producer/response_sizes',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_response_size,
    )
    PRODUCER_BY_CONSUMER_RESPONSE_SIZES = (
        'serviceruntime.googleapis.com/api/producer/by_consumer/response_sizes',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_response_size,
    )
    CONSUMER_ERROR_COUNT = (
        'serviceruntime.googleapis.com/api/consumer/error_count',
        MetricKind.DELTA,
        ValueType.INT64,
        _set_int64_metric_to_constant_1_if_http_error,
    )
    PRODUCER_ERROR_COUNT = (
        'serviceruntime.googleapis.com/api/producer/error_count',
        MetricKind.DELTA,
        ValueType.INT64,
        _set_int64_metric_to_constant_1_if_http_error,
    )
    PRODUCER_BY_CONSUMER_ERROR_COUNT = (
        'serviceruntime.googleapis.com/api/producer/by_consumer/error_count',
        MetricKind.DELTA,
        ValueType.INT64,
        _set_int64_metric_to_constant_1_if_http_error,
    )
    CONSUMER_TOTAL_LATENCIES = (
        'serviceruntime.googleapis.com/api/consumer/total_latencies',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_request_time,
    )
    PRODUCER_TOTAL_LATENCIES = (
        'serviceruntime.googleapis.com/api/producer/total_latencies',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_request_time,
    )
    PRODUCER_BY_CONSUMER_TOTAL_LATENCIES = (
        'serviceruntime.googleapis.com/api/producer/by_consumer/'
        'total_latencies',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_request_time,
    )
    CONSUMER_BACKEND_LATENCIES = (
        'serviceruntime.googleapis.com/api/consumer/backend_latencies',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_backend_time,
    )
    PRODUCER_BACKEND_LATENCIES = (
        'serviceruntime.googleapis.com/api/producer/backend_latencies',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_backend_time,
    )
    PRODUCER_BY_CONSUMER_BACKEND_LATENCIES = (
        'serviceruntime.googleapis.com/api/producer/by_consumer/'
        'backend_latencies',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_backend_time,
    )
    CONSUMER_REQUEST_OVERHEAD_LATENCIES = (
        'serviceruntime.googleapis.com/api/consumer/request_overhead_latencies',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_overhead_time,
    )
    PRODUCER_REQUEST_OVERHEAD_LATENCIES = (
        'serviceruntime.googleapis.com/api/producer/request_overhead_latencies',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_overhead_time,
    )
    PRODUCER_BY_CONSUMER_REQUEST_OVERHEAD_LATENCIES = (
        'serviceruntime.googleapis.com/api/producer/by_consumer/'
        'request_overhead_latencies',
        MetricKind.DELTA,
        ValueType.DISTRIBUTION,
        _set_distribution_metric_to_overhead_time,
    )

    def __init__(self, metric_name, kind, value_type, update_op_func):
        """Constructor.

        update_op_func is used to when updating an `Operation` from a
        `ReportRequestInfo`.

        Args:
           metric_name (str): the name of the metric descriptor
           kind (:class:`MetricKind`): the ``kind`` of the described metric
           value_type (:class:`ValueType`): the `value type` of the described metric
           update_op_func (function): the func to update an operation

        """
        self.kind = kind
        self.metric_name = metric_name
        self.update_op_func = update_op_func
        self.value_type = value_type

    def matches(self, desc):
        """Determines if a given metric descriptor matches this enum instance

        Args:
           desc (:class:`google.apigen.servicecontrol_v1_messages.MetricDescriptor`): the
              instance to test

        Return:
           `True` if desc is supported, otherwise `False`

        """
        return (self.metric_name == desc.name and
                self.kind == desc.metricKind and
                self.value_type == desc.valueType)

    def do_operation_update(self, info, an_op):
        """Updates an operation using the assigned update_op_func

        Args:
           info: (:class:`google.scc.aggregator.report_request.Info`): the
              info instance to update
           an_op: (:class:`google.scc.aggregator.report_request.Info`): the
              info instance to update

        Return:
           `True` if desc is supported, otherwise `False`

        """
        self.update_op_func(self.metric_name, info, an_op)

    @classmethod
    def is_supported(cls, desc):
        """Determines if the given metric descriptor is supported.

        Args:
           desc (:class:`google.apigen.servicecontrol_v1_messages.MetricDescriptor`): the
             metric descriptor to test

        Return:
           `True` if desc is supported, otherwise `False`

        """
        for m in cls:
            if m.matches(desc):
                return True
        return False
