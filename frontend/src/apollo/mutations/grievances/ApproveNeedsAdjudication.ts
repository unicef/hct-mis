import { gql } from 'apollo-boost';

export const ApproveDeleteIndividualDataChange = gql`
  mutation ApproveNeedsAdjudication(
    $grievanceTicketId: ID!
    $selectedIndividualId: ID
    $selectedIndividualIds: [ID]
  ) {
    approveNeedsAdjudication(
      grievanceTicketId: $grievanceTicketId
      selectedIndividualId: $selectedIndividualId
      selectedIndividualIds: $selectedIndividualIds
    ) {
      grievanceTicket {
        id
        status
      }
    }
  }
`;
