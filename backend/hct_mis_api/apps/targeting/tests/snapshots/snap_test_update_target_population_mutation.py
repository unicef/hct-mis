# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_0_wrong_args_count 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': "['Comparision method - EQUALS expect 1 arguments, 2 given']",
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_1_wrong_comparison_method 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': "['size is INTEGER type filter and does not accept - CONTAINS comparision method']",
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_2_unknown_comparison_method 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': "['Unknown comparision method - BLABLA']",
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_3_unknown_flex_field_name 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': '["Can\'t find any flex field attribute associated with foo_bar field name"]',
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_4_unknown_core_field_name 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': '["Can\'t find any core field attribute associated with foo_bar field name"]',
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_update_mutation_correct_variables_0_with_permission_draft 1'] = {
    'data': {
        'updateTargetPopulation': {
            'targetPopulation': {
                'candidateListTargetingCriteria': {
                    'rules': [
                        {
                            'filters': [
                                {
                                    'arguments': [
                                        3
                                    ],
                                    'comparisionMethod': 'EQUALS',
                                    'fieldName': 'size',
                                    'isFlexField': False
                                }
                            ]
                        }
                    ]
                },
                'candidateListTotalHouseholds': 2,
                'candidateListTotalIndividuals': 6,
                'finalListTargetingCriteria': None,
                'finalListTotalHouseholds': None,
                'finalListTotalIndividuals': None,
                'name': 'with_permission_draft updated',
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestUpdateTargetPopulationMutation::test_update_mutation_correct_variables_1_without_permission_draft 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_update_mutation_correct_variables_2_with_permission_approved 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': '["Name can\'t be changed when Target Population is in APPROVED status"]',
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_update_mutation_correct_variables_3_without_permission_approved 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}
