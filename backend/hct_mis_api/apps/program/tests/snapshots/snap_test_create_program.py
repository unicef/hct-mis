# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCreateProgram::test_create_program_authenticated_0_with_permission 1'] = {
    'data': {
        'createProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000',
                'cashPlus': True,
                'dataCollectingType': {
                    'active': True,
                    'code': '1',
                    'description': 'Partial individuals collected',
                    'individualFiltersAvailable': True
                },
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'Test',
                'populationGoal': 150000,
                'scope': 'UNICEF',
                'sector': 'EDUCATION',
                'startDate': '2019-12-20',
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCreateProgram::test_create_program_authenticated_1_without_permission 1'] = {
    'data': {
        'createProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_authenticated_2_with_permission_but_invalid_dates 1'] = {
    'data': {
        'createProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Start date cannot be greater than the end date.',
            'path': [
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_not_authenticated 1'] = {
    'data': {
        'createProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User is not authenticated.',
            'path': [
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_programme_code_should_be_unique_among_the_same_business_area 1'] = {
    'data': {
        'createProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['Programme code is already used.']",
            'path': [
                'createProgram'
            ]
        }
    ]
}
