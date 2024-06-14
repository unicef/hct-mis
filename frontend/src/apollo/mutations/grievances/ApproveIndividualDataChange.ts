import { gql } from '@apollo/client';

export const ApproveIndividualDataChange = gql`
  mutation ApproveIndividualDataChange(
    $grievanceTicketId: ID!
    $individualApproveData: JSONString
    $flexFieldsApproveData: JSONString
    $approvedDocumentsToCreate: [Int]
    $approvedDocumentsToRemove: [Int]
    $approvedDocumentsToEdit: [Int]
    $approvedIdentitiesToCreate: [Int]
    $approvedIdentitiesToEdit: [Int]
    $approvedIdentitiesToRemove: [Int]
    $approvedPaymentChannelsToCreate: [Int]
    $approvedPaymentChannelsToEdit: [Int]
    $approvedPaymentChannelsToRemove: [Int]
    $approvedDeliveryMechanismDataToCreate: [Int]
    $approvedDeliveryMechanismDataToEdit: [Int]
    $approvedDeliveryMechanismDataToRemove: [Int]
  ) {
    approveIndividualDataChange(
      grievanceTicketId: $grievanceTicketId
      individualApproveData: $individualApproveData
      flexFieldsApproveData: $flexFieldsApproveData
      approvedDocumentsToCreate: $approvedDocumentsToCreate
      approvedDocumentsToRemove: $approvedDocumentsToRemove
      approvedDocumentsToEdit: $approvedDocumentsToEdit
      approvedIdentitiesToCreate: $approvedIdentitiesToCreate
      approvedIdentitiesToEdit: $approvedIdentitiesToEdit
      approvedIdentitiesToRemove: $approvedIdentitiesToRemove
      approvedPaymentChannelsToCreate: $approvedPaymentChannelsToCreate
      approvedPaymentChannelsToEdit: $approvedPaymentChannelsToEdit
      approvedPaymentChannelsToRemove: $approvedPaymentChannelsToRemove
      approvedDeliveryMechanismDataToCreate: $approvedDeliveryMechanismDataToCreate
      approvedDeliveryMechanismDataToEdit: $approvedDeliveryMechanismDataToEdit
      approvedDeliveryMechanismDataToRemove: $approvedDeliveryMechanismDataToRemove
    ) {
      grievanceTicket {
        id
        status
        individualDataUpdateTicketDetails {
          id
          individual {
            ...individualDetailed
          }
          individualData
        }
      }
    }
  }
`;
