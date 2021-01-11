import { gql } from 'apollo-boost';

export const ALL_LOG_ENTRIES_QUERY = gql`
  query AllLogEntries(
    $objectId: String
    $after: String
    $before: String
    $first: Int
    $last: Int
  ) {
    allLogEntries(
      after: $after
      before: $before
      first: $first
      last: $last
      objectId: $objectId
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
          id
          action
          changesDisplayDict
          objectRepr
          timestamp
          contentType{
            id
            appLabel
            model
          }
          actor {
            id
            firstName
            lastName
          }
        }
      }
    }
  }
`;
