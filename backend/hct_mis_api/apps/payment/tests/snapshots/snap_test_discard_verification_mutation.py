# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDiscardVerificationMutation::test_discard_active 1'] = {
    'data': {
        'discardCashPlanPaymentVerification': {
            'cashPlan': {
                'name': 'TEST'
            }
        }
    }
}
