import { gql } from 'apollo-boost';

export const CandidateHouseholdsListByTargetingCriteria = gql`
  query candidateHouseholdsListByTargetingCriteria(
    $targetPopulation: ID!
    $first: Int
    $after: String
    $before: String
    $last: Int
    $orderBy: String
  ) {
    candidateHouseholdsListByTargetingCriteria(
      targetPopulation: $targetPopulation
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
    ) {
      edges {
        node {
          id
          headOfHousehold {
            id
            givenName
            familyName
          }
          size
          adminArea {
            id
            title
          }
          updatedAt
          address
          selection{
            vulnerabilityScore
          }
        }
        cursor
      }
      totalCount
      edgeCount
    }
  }
`;
