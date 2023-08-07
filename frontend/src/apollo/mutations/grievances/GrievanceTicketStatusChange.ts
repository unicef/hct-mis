import { gql } from 'apollo-boost';

export const GRIEVANCE_TICKET_STATUS_CHANGE = gql`
  mutation GrievanceTicketStatusChange($grievanceTicketId: ID, $status: Int) {
    grievanceStatusChange(
      grievanceTicketId: $grievanceTicketId
      status: $status
    ) {
      grievanceTicket {
        ...grievanceTicketDetailed
      }
    }
  }
`;
