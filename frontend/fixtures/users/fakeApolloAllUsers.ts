import { AllUsersDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllUsers = [
  {
    request: {
      query: AllUsersDocument,
      variables: {
        businessArea: 'afghanistan',
        first: 10,
        orderBy: '-status',
      },
    },
    result: {
      data: {
        allUsers: {
          pageInfo: {
            hasNextPage: true,
            hasPreviousPage: false,
            endCursor: 'YXJyYXljb25uZWN0aW9uOjk=',
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            __typename: 'PageInfo',
          },
          edges: [
            {
              node: {
                id:
                  'VXNlck5vZGU6NzVmNmNkOTMtY2FhZC00NjQ1LWFjNzAtNjNhZTM2NGQ0MGI3',
                firstName: '',
                lastName: '',
                username: 'wojciech.nosal@tivix.com',
                email: 'wojciech.nosal@tivix.com',
                isActive: true,
                lastLogin: '2021-04-27T09:29:43.275926',
                status: 'ACTIVE',
                partner: { name: 'UNICEF', __typename: 'PartnerType' },
                userRoles: [
                  {
                    businessArea: {
                      name: 'Global',
                      __typename: 'UserBusinessAreaNode',
                    },
                    role: {
                      name: 'Basic User',
                      permissions: ['DASHBOARD_VIEW_COUNTRY'],
                      __typename: 'RoleNode',
                    },
                    __typename: 'UserRoleNode',
                  },
                  {
                    businessArea: {
                      name: 'Afghanistan',
                      __typename: 'UserBusinessAreaNode',
                    },
                    role: {
                      name: 'Role with all permissions',
                      permissions: [
                        'RDI_VIEW_LIST',
                        'RDI_VIEW_DETAILS',
                        'RDI_IMPORT_DATA',
                        'RDI_RERUN_DEDUPE',
                        'RDI_MERGE_IMPORT',
                        'RDI_REFUSE_IMPORT',
                        'POPULATION_VIEW_HOUSEHOLDS_LIST',
                        'POPULATION_VIEW_HOUSEHOLDS_DETAILS',
                        'POPULATION_VIEW_INDIVIDUALS_LIST',
                        'POPULATION_VIEW_INDIVIDUALS_DETAILS',
                        'PROGRAMME_VIEW_LIST_AND_DETAILS',
                        'PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS',
                        'PROGRAMME_CREATE',
                        'PROGRAMME_UPDATE',
                        'PROGRAMME_REMOVE',
                        'PROGRAMME_ACTIVATE',
                        'PROGRAMME_FINISH',
                        'TARGETING_VIEW_LIST',
                        'TARGETING_VIEW_DETAILS',
                        'TARGETING_CREATE',
                        'TARGETING_UPDATE',
                        'TARGETING_DUPLICATE',
                        'TARGETING_REMOVE',
                        'TARGETING_LOCK',
                        'TARGETING_UNLOCK',
                        'TARGETING_SEND',
                        'PAYMENT_VERIFICATION_VIEW_LIST',
                        'PAYMENT_VERIFICATION_VIEW_DETAILS',
                        'PAYMENT_VERIFICATION_CREATE',
                        'PAYMENT_VERIFICATION_UPDATE',
                        'PAYMENT_VERIFICATION_ACTIVATE',
                        'PAYMENT_VERIFICATION_DISCARD',
                        'PAYMENT_VERIFICATION_FINISH',
                        'PAYMENT_VERIFICATION_EXPORT',
                        'PAYMENT_VERIFICATION_IMPORT',
                        'PAYMENT_VERIFICATION_VERIFY',
                        'PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS',
                        'USER_MANAGEMENT_VIEW_LIST',
                        'DASHBOARD_VIEW_COUNTRY',
                        'DASHBOARD_EXPORT',
                        'GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE',
                        'GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR',
                        'GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER',
                        'GRIEVANCES_VIEW_LIST_SENSITIVE',
                        'GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR',
                        'GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER',
                        'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE',
                        'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR',
                        'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER',
                        'GRIEVANCES_VIEW_DETAILS_SENSITIVE',
                        'GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR',
                        'GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER',
                        'GRIEVANCES_VIEW_HOUSEHOLD_DETAILS',
                        'GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR',
                        'GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER',
                        'GRIEVANCES_VIEW_INDIVIDUALS_DETAILS',
                        'GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR',
                        'GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER',
                        'GRIEVANCES_CREATE',
                        'GRIEVANCES_UPDATE',
                        'GRIEVANCES_UPDATE_AS_CREATOR',
                        'GRIEVANCES_UPDATE_AS_OWNER',
                        'GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE',
                        'GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR',
                        'GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER',
                        'GRIEVANCES_ADD_NOTE',
                        'GRIEVANCES_ADD_NOTE_AS_CREATOR',
                        'GRIEVANCES_ADD_NOTE_AS_OWNER',
                        'GRIEVANCES_SET_IN_PROGRESS',
                        'GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR',
                        'GRIEVANCES_SET_IN_PROGRESS_AS_OWNER',
                        'GRIEVANCES_SET_ON_HOLD',
                        'GRIEVANCES_SET_ON_HOLD_AS_CREATOR',
                        'GRIEVANCES_SET_ON_HOLD_AS_OWNER',
                        'GRIEVANCES_SEND_FOR_APPROVAL',
                        'GRIEVANCES_SEND_FOR_APPROVAL_AS_CREATOR',
                        'GRIEVANCES_SEND_FOR_APPROVAL_AS_OWNER',
                        'GRIEVANCES_SEND_BACK',
                        'GRIEVANCES_SEND_BACK_AS_CREATOR',
                        'GRIEVANCES_SEND_BACK_AS_OWNER',
                        'GRIEVANCES_APPROVE_DATA_CHANGE',
                        'GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR',
                        'GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER',
                        'GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK',
                        'GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR',
                        'GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER',
                        'GRIEVANCES_CLOSE_TICKET_FEEDBACK',
                        'GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR',
                        'GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER',
                        'GRIEVANCES_APPROVE_FLAG_AND_DEDUPE',
                        'GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR',
                        'GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER',
                        'GRIEVANCE_ASSIGN',
                        'REPORTING_EXPORT',
                        'ALL_VIEW_PII_DATA_ON_LISTS',
                        'ACTIVITY_LOG_VIEW',
                        'ACTIVITY_LOG_DOWNLOAD',
                      ],
                      __typename: 'RoleNode',
                    },
                    __typename: 'UserRoleNode',
                  },
                ],
                __typename: 'UserNode',
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjc=',
              __typename: 'UserNodeEdge',
            },
          ],
          totalCount: 13,
          edgeCount: 10,
          __typename: 'UserNodeConnection',
        },
      },
    },
  },
];
