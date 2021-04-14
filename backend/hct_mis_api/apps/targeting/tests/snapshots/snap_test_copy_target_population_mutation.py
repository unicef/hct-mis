# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCopyTargetPopulationMutation::test_copy_empty_target_1_0_with_permission 1'] = {
    'data': {
        'copyTargetPopulation': {
            'targetPopulation': {
                'candidateListTargetingCriteria': None,
                'candidateListTotalHouseholds': 0,
                'candidateListTotalIndividuals': None,
                'finalListTargetingCriteria': None,
                'finalListTotalHouseholds': None,
                'finalListTotalIndividuals': None,
                'name': 'test_copy_empty_target_1',
                'status': 'DRAFT'
            }
        }
    }
}

snapshots['TestCopyTargetPopulationMutation::test_copy_empty_target_1_1_without_permission 1'] = {
    'data': {
        'copyTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'copyTargetPopulation'
            ]
        }
    ]
}

snapshots['TestCopyTargetPopulationMutation::test_copy_target_0_with_permission 1'] = {
    'data': {
        'copyTargetPopulation': {
            'targetPopulation': {
                'candidateListTargetingCriteria': {
                    'rules': [
                        {
                            'filters': [
                                {
                                    'arguments': [
                                        1
                                    ],
                                    'comparisionMethod': 'EQUALS',
                                    'fieldName': 'size',
                                    'isFlexField': False
                                }
                            ]
                        }
                    ]
                },
                'candidateListTotalHouseholds': 1,
                'candidateListTotalIndividuals': 1,
                'finalListTargetingCriteria': None,
                'finalListTotalHouseholds': None,
                'finalListTotalIndividuals': None,
                'name': 'Test New Copy Name',
                'status': 'DRAFT'
            }
        }
    }
}

snapshots['TestCopyTargetPopulationMutation::test_copy_target_1_without_permission 1'] = {
    'data': {
        'copyTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'copyTargetPopulation'
            ]
        }
    ]
}
