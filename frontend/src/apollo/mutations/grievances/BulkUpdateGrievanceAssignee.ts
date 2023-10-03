import { gql } from 'apollo-boost';
export const BulkUpdateGrievanceAssignee = gql`
  mutation BulkUpdateGrievanceAssignee(
    $grievanceTicketIds: [ID]
    $assignedTo: String
    $businessAreaSlug: String!
  ) {
    bulkUpdateGrievanceAssignee(
      grievanceTicketIds: $grievanceTicketIds
      assignedTo: $assignedTo
      businessAreaSlug: $businessAreaSlug
    ) {
      grievanceTickets {
        id
        assignedTo {
          firstName
          lastName
          email
        }
      }
    }
  }
`;
