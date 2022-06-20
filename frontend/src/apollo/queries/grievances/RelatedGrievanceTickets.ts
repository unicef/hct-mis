import { gql } from 'apollo-boost';

export const RelatedGrievanceTickets = gql`
  query RelatedGrievanceTickets($id: ID!) {
    grievanceTicket(id: $id) {
      relatedTickets {
        id
        status
        category
        issueType
        unicefId
      }
      existingTickets {
        id
        status
        category
        issueType
        unicefId
      }
    }
  }
`;
