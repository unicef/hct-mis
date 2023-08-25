import { AllRegistrationDataImportsDocument } from '../../src/__generated__/graphql';
import { fakeProgram } from '../programs/fakeProgram';

export const fakeApolloAllRegistrationDataImports = [
  {
    request: {
      query: AllRegistrationDataImportsDocument,
      variables: {
        businessArea: 'afghanistan',
        importDateRange: '{}',
        program:
          'UHJvZ3JhbU5vZGU6YzRkNTY1N2QtMWEyOS00NmUxLTgxOTAtZGY3Zjg1YTBkMmVm',
        size: '{}',
        first: 10,
        orderBy: '-import_date',
      },
    },
    result: {
      data: {
        allRegistrationDataImports: {
          pageInfo: {
            hasNextPage: true,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjk=',
            __typename: 'PageInfo',
          },
          totalCount: 27,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6ZjRmMGY4NjktNTllNS00YWI2LWJkYjEtYWJiMGVkMTU5YTRl',
                createdAt: '2023-06-12T11:14:35.582648+00:00',
                name: 'Lol123',
                status: 'IMPORT_ERROR',
                importDate: '2023-06-12T11:14:35.582685+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                dataSource: 'XLS',
                numberOfHouseholds: 2,
                numberOfIndividuals: 6,
                __typename: 'RegistrationDataImportNode',
              },
              __typename: 'RegistrationDataImportNodeEdge',
            },
          ],
          __typename: 'RegistrationDataImportNodeConnection',
        },
      },
    },
  },
];
