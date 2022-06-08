import { gql } from 'apollo-boost';

export const ALL_ADMIN_AREAS_QUERY = gql`
  query AllAdminAreas(
    $name: String
    $businessArea: String
    $level: Int
    $first: Int
  ) {
    allAdminAreas(
      name_Istartswith: $name
      businessArea: $businessArea
      first: $first
      level: $level
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        endCursor
        startCursor
      }
      edges {
        node {
          id
          name
          pCode
        }
      }
    }
  }
`;
