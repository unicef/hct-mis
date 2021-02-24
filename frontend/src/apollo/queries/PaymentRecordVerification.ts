import { gql } from 'apollo-boost';

export const PAYMENT_RECORD_VERIFICATION_QUERY = gql`
  query PaymentRecordVerification($id: ID!) {
    paymentRecordVerification(id: $id) {
      id
      status
      statusDate
      receivedAmount
      paymentRecord {
        id
        status
        statusDate
        caId
        caHashId
        registrationCaId
        household {
          unicefId
          id
          size
          headOfHousehold {
            id
            phoneNo
            phoneNoAlternative
          }
        }
        fullName
        distributionModality
        totalPersonsCovered
        targetPopulation {
          id
          name
        }
        cashPlan {
          id
          caId
          program {
            id
            name
          }
          verifications {
            edges {
              node {
                id
                status
                verificationMethod
              }
            }
          }
        }
        currency
        entitlementQuantity
        deliveredQuantity
        deliveryDate
        deliveryDate
        deliveryType
        entitlementCardIssueDate
        entitlementCardNumber
        serviceProvider {
          id
          fullName
          shortName
        }
      }
    }
  }
`;
