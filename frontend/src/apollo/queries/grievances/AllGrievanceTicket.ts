import { gql } from 'apollo-boost';

export const AllGrievanceTicket = gql`
  query AllGrievanceTicket(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $id: UUID
    $category: String
    $issueType: String
    $businessArea: String!
    $search: String
    $status: [String]
    $fsp: String
    $createdAtRange: String
    $admin: [ID]
    $orderBy: String
    $registrationDataImport: ID
    $assignedTo: ID
    $cashPlan: String
    $scoreMin: String
    $scoreMax: String
    $household: String
    $preferredLanguage: String
  ) {
    allGrievanceTicket(
      before: $before
      after: $after
      first: $first
      last: $last
      id: $id
      category: $category
      issueType: $issueType
      businessArea: $businessArea
      search: $search
      status: $status
      fsp: $fsp
      createdAtRange: $createdAtRange
      orderBy: $orderBy
      admin: $admin
      registrationDataImport: $registrationDataImport
      assignedTo: $assignedTo
      cashPlan: $cashPlan
      scoreMin: $scoreMin
      scoreMax: $scoreMax
      household: $household
      preferredLanguage: $preferredLanguage
    ) {
      totalCount
      pageInfo {
        startCursor
        endCursor
      }
      edges {
        cursor
        node {
          id
          status
          assignedTo {
            id
            firstName
            lastName
            email
          }
          createdBy {
            id
          }
          category
          issueType
          createdAt
          userModified
          admin
          household {
            unicefId
            id
          }
          unicefId
          relatedTickets {
            id
          }
        }
      }
    }
  }
`;
