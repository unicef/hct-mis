# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 3,
                    'consent': True,
                    'description': 'Test Feedback',
                    'issueType': 12,
                    'language': 'Polish, English',
                    'sensitiveTicketDetails': {
                        'household': None,
                        'individual': None,
                        'paymentRecord': None
                    }
                }
            ]
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 12
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'sensitiveTicketDetails',
                'household'
            ]
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 15
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'sensitiveTicketDetails',
                'individual'
            ]
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 18
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'sensitiveTicketDetails',
                'paymentRecord'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
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
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_with_two_payment_records_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 3,
                    'consent': True,
                    'description': 'Test Feedback',
                    'issueType': 12,
                    'language': 'Polish, English',
                    'sensitiveTicketDetails': {
                        'household': None,
                        'individual': None,
                        'paymentRecord': None
                    }
                },
                {
                    'admin': 'City Test',
                    'category': 3,
                    'consent': True,
                    'description': 'Test Feedback',
                    'issueType': 12,
                    'language': 'Polish, English',
                    'sensitiveTicketDetails': {
                        'household': None,
                        'individual': None,
                        'paymentRecord': None
                    }
                }
            ]
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 12
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'sensitiveTicketDetails',
                'household'
            ]
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 12
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                1,
                'sensitiveTicketDetails',
                'household'
            ]
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 15
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'sensitiveTicketDetails',
                'individual'
            ]
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 15
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                1,
                'sensitiveTicketDetails',
                'individual'
            ]
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 18
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'sensitiveTicketDetails',
                'paymentRecord'
            ]
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 18
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                1,
                'sensitiveTicketDetails',
                'paymentRecord'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_with_two_payment_records_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
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
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_extras_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 3,
                    'consent': True,
                    'description': 'Test Feedback',
                    'issueType': 12,
                    'language': 'Polish, English',
                    'sensitiveTicketDetails': {
                        'household': None,
                        'individual': None,
                        'paymentRecord': None
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_extras_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
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
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_household_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 3,
                    'consent': True,
                    'description': 'Test Feedback',
                    'issueType': 12,
                    'language': 'Polish, English',
                    'sensitiveTicketDetails': {
                        'household': None,
                        'individual': None,
                        'paymentRecord': None
                    }
                }
            ]
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 15
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'sensitiveTicketDetails',
                'individual'
            ]
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 18
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'sensitiveTicketDetails',
                'paymentRecord'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_household_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
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
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_individual_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 3,
                    'consent': True,
                    'description': 'Test Feedback',
                    'issueType': 12,
                    'language': 'Polish, English',
                    'sensitiveTicketDetails': {
                        'household': None,
                        'individual': None,
                        'paymentRecord': None
                    }
                }
            ]
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 12
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'sensitiveTicketDetails',
                'household'
            ]
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 18
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'sensitiveTicketDetails',
                'paymentRecord'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_individual_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
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
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_issue_type_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'You have to provide issue_type in 3',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_issue_type_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
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
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_payment_record_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 3,
                    'consent': True,
                    'description': 'Test Feedback',
                    'issueType': 12,
                    'language': 'Polish, English',
                    'sensitiveTicketDetails': {
                        'household': None,
                        'individual': None,
                        'paymentRecord': None
                    }
                }
            ]
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 12
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'sensitiveTicketDetails',
                'household'
            ]
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 15
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'sensitiveTicketDetails',
                'individual'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_payment_record_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
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
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_wrong_extras_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "You can't provide extras.category.grievance_complaint_ticket_extras in 3",
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_wrong_extras_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
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
                'createGrievanceTicket'
            ]
        }
    ]
}
