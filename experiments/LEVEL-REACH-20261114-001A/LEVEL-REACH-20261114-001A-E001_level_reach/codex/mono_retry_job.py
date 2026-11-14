"""Retry only the G-mono case that exceeded the original 2G case cap.

The scientific case function and 300-second budgets are unchanged. This
separate output allows the retry to coexist with the two unfinished gate
workers: 2G + 2G + 3G of worker allowances, below the total 8G envelope.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mono_job

RETRY_CASE = 'b7af5bcb77f74404b9e42ebf5b166c8a405073106163c3a2e171a0e416846dd4'


def setup(params):
    mono_job.setup(params)


def cases():
    for case_id, payload in mono_job.cases():
        if case_id == RETRY_CASE:
            yield case_id, payload


def run(case_id, payload):
    assert case_id == RETRY_CASE
    return mono_job.run(case_id, payload)
