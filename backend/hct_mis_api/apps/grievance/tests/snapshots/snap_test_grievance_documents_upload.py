# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['MutationTestCase::test_some_mutation 1'] = {
    'data': {
        'uploadDocuments': {
            'success': True
        }
    }
}
