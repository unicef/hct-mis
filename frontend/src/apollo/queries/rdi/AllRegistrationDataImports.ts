import { gql } from 'apollo-boost';

export const ALL_REGISTRATION_DATA_IMPORT_QUERY = gql`
  query AllRegistrationDataImports(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $search: String
    $importedBy: UUID
    $status: String
    $importDate: Date
    $businessArea: String
    $importDateRange: String
    $size: String
  ) {
    allRegistrationDataImports(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      name_Startswith: $search
      importedBy_Id: $importedBy
      status: $status
      importDate: $importDate
      businessArea: $businessArea
      importDateRange: $importDateRange
      size: $size
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
      edges {
        cursor
        node {
          ...registrationMinimal
        }
      }
    }
  }
`;