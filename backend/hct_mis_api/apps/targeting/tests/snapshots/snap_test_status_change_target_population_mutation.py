# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestApproveTargetPopulationMutation::test_approve_fail_target_population 1'] = {
    'data': {
        'approveTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': "['Only Target Population with status DRAFT can be approved']",
            'path': [
                'approveTargetPopulation'
            ]
        }
    ]
}

snapshots['TestApproveTargetPopulationMutation::test_approve_target_population_0_with_permission 1'] = {
    'data': {
        'approveTargetPopulation': {
            'targetPopulation': {
                'households': {
                    'edges': [
                        {
                            'node': {
                                'residenceStatus': 'HOST',
                                'size': 1
                            }
                        },
                        {
                            'node': {
                                'residenceStatus': 'HOST',
                                'size': 2
                            }
                        }
                    ],
                    'totalCount': 2
                },
                'status': 'LOCKED'
            }
        }
    }
}

snapshots['TestApproveTargetPopulationMutation::test_approve_target_population_1_without_permission 1'] = {
    'data': {
        'approveTargetPopulation': None
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
                'approveTargetPopulation'
            ]
        }
    ]
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_fail_target_population 1'] = {
    'data': {
        'finalizeTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': "['Only Target Population with status APPROVED can be finalized']",
            'path': [
                'finalizeTargetPopulation'
            ]
        }
    ]
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_target_population_0_with_permission 1'] = {
    'data': {
        'finalizeTargetPopulation': {
            'targetPopulation': {
                'finalList': {
                    'edges': [
                        {
                            'node': {
                                'residenceStatus': 'HOST',
                                'size': 1
                            }
                        },
                        {
                            'node': {
                                'residenceStatus': 'HOST',
                                'size': 2
                            }
                        }
                    ]
                },
                'households': {
                    'edges': [
                        {
                            'node': {
                                'residenceStatus': 'HOST',
                                'size': 1
                            }
                        },
                        {
                            'node': {
                                'residenceStatus': 'HOST',
                                'size': 2
                            }
                        }
                    ],
                    'totalCount': 2
                },
                'status': 'PROCESSING'
            }
        }
    }
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_target_population_1_without_permission 1'] = {
    'data': {
        'finalizeTargetPopulation': None
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
                'finalizeTargetPopulation'
            ]
        }
    ]
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_target_population_with_final_criteria 1'] = {
    'data': {
        'finalizeTargetPopulation': {
            'targetPopulation': {
                'finalList': {
                    'edges': [
                        {
                            'node': {
                                'residenceStatus': 'HOST',
                                'size': 1
                            }
                        },
                        {
                            'node': {
                                'residenceStatus': 'HOST',
                                'size': 2
                            }
                        }
                    ]
                },
                'households': {
                    'edges': [
                        {
                            'node': {
                                'residenceStatus': 'HOST',
                                'size': 1
                            }
                        },
                        {
                            'node': {
                                'residenceStatus': 'HOST',
                                'size': 2
                            }
                        }
                    ],
                    'totalCount': 2
                },
                'status': 'PROCESSING'
            }
        }
    }
}

snapshots['TestUnapproveTargetPopulationMutation::test_unapprove_fail_target_population 1'] = {
    'data': {
        'unapproveTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': "['Only Target Population with status APPROVED can be unapproved']",
            'path': [
                'unapproveTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUnapproveTargetPopulationMutation::test_unapprove_target_population_0_with_permission 1'] = {
    'data': {
        'unapproveTargetPopulation': {
            'targetPopulation': {
                'households': {
                    'edges': [
                        {
                            'node': {
                                'residenceStatus': 'HOST',
                                'size': 1
                            }
                        },
                        {
                            'node': {
                                'residenceStatus': 'HOST',
                                'size': 2
                            }
                        }
                    ],
                    'totalCount': 2
                },
                'status': 'DRAFT'
            }
        }
    }
}

snapshots['TestUnapproveTargetPopulationMutation::test_unapprove_target_population_1_without_permission 1'] = {
    'data': {
        'unapproveTargetPopulation': None
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
                'unapproveTargetPopulation'
            ]
        }
    ]
}
