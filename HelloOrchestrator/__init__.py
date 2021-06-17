# This function is not intended to be invoked directly. Instead it will be
# triggered by an HTTP starter function.
# Before running this sample, please:
# - create a Durable activity function (default name is "Hello")
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import json
from datetime import timedelta

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    result1 = yield context.call_activity('Hello', "Tokyo")
    result2 = yield context.call_activity('Hello', "Seattle")
    result3 = yield context.call_activity('Hello', "London")

    polling_interval = 5
    expiry_time = context.current_utc_datetime + timedelta(minutes=10)

    # Monitor Loop, checking a simulated status
    while context.current_utc_datetime < expiry_time:
        job_status = yield context.call_activity("GetStatus", "")
        if job_status == "Completed":
            # Perform an action when a condition is met.
            result4 = yield context.call_activity("Goodbye", "completed")
            break

        # Orchestration sleeps until this time.
        next_check = context.current_utc_datetime + timedelta(seconds=polling_interval)
        yield context.create_timer(next_check)

    result5 = yield context.call_activity("Goodbye", "!")

    return [result1, result2, result3, result4, result5]

main = df.Orchestrator.create(orchestrator_function)