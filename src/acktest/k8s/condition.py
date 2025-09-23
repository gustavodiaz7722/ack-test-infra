# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may
# not use this file except in compliance with the License. A copy of the
# License is located at
#
#	 http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

"""Utility functions to help processing Kubernetes resource conditions"""

import pytest

from . import resource

CONDITION_TYPE_ADOPTED = "ACK.Adopted"
CONDITION_TYPE_READY = "Ready"
CONDITION_TYPE_RESOURCE_SYNCED = "ACK.ResourceSynced"
CONDITION_TYPE_TERMINAL = "ACK.Terminal"
CONDITION_TYPE_RECOVERABLE = "ACK.Recoverable"
CONDITION_TYPE_ADVISORY = "ACK.Advisory"
CONDITION_TYPE_LATE_INITIALIZED = "ACK.LateInitialized"
CONDITION_TYPE_REFERENCES_RESOLVED = "ACK.ReferencesResolved"

TERMINAL_REASON = "Terminal error, the custom resource Spec needs to be updated before any further sync can occur"


def assert_type_status(
    ref: resource.CustomResourceReference,
    cond_type_match: str = CONDITION_TYPE_RESOURCE_SYNCED,
    cond_status_match: bool = True,
):
    """Asserts that the supplied resource has a condition of type
    ACK.ResourceSynced and that the Status of this condition is True.

    Usage:
        from acktest.k8s import resource
        from acktest.k8s import condition

        ref = resource.CustomResourceReference(
            CRD_GROUP, CRD_VERSION, RESOURCE_PLURAL,
            db_cluster_id, namespace="default",
        )
        resource.create_custom_resource(ref, resource_data)
        resource.wait_resource_consumed_by_controller(ref)
        condition.assert_type_status(
            ref,
            condition.CONDITION_TYPE_RESOURCE_SYNCED,
            False)

    Raises:
        pytest.fail when condition of the specified type is not found or is not
        in the supplied status.
    """
    cond = resource.get_resource_condition(ref, cond_type_match)
    if cond is None:
        msg = (f"Failed to find {cond_type_match} condition in "
               f"resource {ref}")
        pytest.fail(msg)

    cond_status = cond.get('status', None)
    if str(cond_status) != str(cond_status_match):
        msg = (f"Expected {cond_type_match} condition to "
               f"have status {cond_status_match} but found {cond_status}")
        pytest.fail(msg)

  
def assert_ready_status(
    ref: resource.CustomResourceReference,
    cond_status_match: bool,
):
    """Asserts that the supplied resource has a condition of type
    Ready and that the Status of this condition is True.

    Usage:
        from acktest.k8s import resource
        from acktest.k8s import condition

        ref = resource.CustomResourceReference(
            CRD_GROUP, CRD_VERSION, RESOURCE_PLURAL,
            db_cluster_id, namespace="default",
        )
        resource.create_custom_resource(ref, resource_data)
        resource.wait_resource_consumed_by_controller(ref)
        condition.assert_ready_status(ref, False)
        
    Raises:
        pytest.fail when Ready condition is not found or is not in
        a True status.
    """
    assert_type_status(ref, "Ready", cond_status_match)
    
def assert_ready(ref: resource.CustomResourceReference):
    """Asserts that the supplied resource has a condition of type
    Ready and that the Status of this condition is True.

    Usage:
        from acktest.k8s import resource
        from acktest.k8s import condition

        ref = resource.CustomResourceReference(
            CRD_GROUP, CRD_VERSION, RESOURCE_PLURAL,
            db_cluster_id, namespace="default",
        )
        resource.create_custom_resource(ref, resource_data)
        resource.wait_resource_consumed_by_controller(ref)
        condition.assert_ready(ref)
    Raises:
        pytest.fail when Ready condition is not found or is not in
        a True status.
    """
    return assert_ready_status(ref, True)
  
def assert_not_ready(ref: resource.CustomResourceReference):
    """Asserts that the supplied resource has a condition of type
    Ready and that the Status of this condition is False.

    Usage:
        from acktest.k8s import resource
        from acktest.k8s import condition

        ref = resource.CustomResourceReference(
            CRD_GROUP, CRD_VERSION, RESOURCE_PLURAL,
            db_cluster_id, namespace="default",
        )
        resource.create_custom_resource(ref, resource_data)
        resource.wait_resource_consumed_by_controller(ref)
        condition.assert_not_ready(ref)
    Raises:
        pytest.fail when Ready condition is not found or is not in
        a False status.
    """
    return assert_ready_status(ref, False)
  
def assert_terminal(ref: resource.CustomResourceReference, expected_message: str):
    """Asserts that the supplied resource has a condition of type
    Ready and that the Status of this condition is False. Also checks
    that the reason field contains the expected terminal reason.

    Usage:
        from acktest.k8s import resource
        from acktest.k8s import condition

        ref = resource.CustomResourceReference(
            CRD_GROUP, CRD_VERSION, RESOURCE_PLURAL,
            db_cluster_id, namespace="default",
        )
        resource.create_custom_resource(ref, resource_data)
        resource.wait_resource_consumed_by_controller(ref)
        condition.assert_terminal(ref)
        
    Raises:
        pytest.fail when Ready condition is not found or is not in
        a False status or the reason field does not contain the expected
        terminal reason.
        
    """
    assert_type_status(ref, "Ready", False)
    cond = resource.get_resource_condition(ref, "Ready")
    
    reason = cond.get('reason', None)
    if reason != TERMINAL_REASON:
        msg = (f"Expected Ready condition to "
               f"have reason '{TERMINAL_REASON}' but found '{reason}'")
        pytest.fail(msg)
    
    message = cond.get('message', None)
    if expected_message not in message:
        msg = (f"Expected Ready condition to "
               f"have message containing '{expected_message}' but found '{message}'")
        pytest.fail(msg)

