import { gql } from 'apollo-boost';

export const CashPlan = gql`
  query CashPlan($id: ID!) {
    cashPlan(id: $id) {
      id
      canCreatePaymentVerificationPlan
      name
      startDate
      endDate
      updatedAt
      status
      deliveryType
      fundsCommitment
      downPayment
      dispersionDate
      assistanceThrough
      serviceProvider {
        id
        caId
        fullName
      }
      caId
      caHashId
      dispersionDate
      verificationStatus
      bankReconciliationSuccess
      bankReconciliationError
      totalNumberOfHouseholds
      verifications {
        edges {
          node {
            id
            unicefId
            status
            sampleSize
            receivedCount
            notReceivedCount
            respondedCount
            verificationMethod
            sampling
            receivedCount
            receivedWithProblemsCount
            rapidProFlowId
            confidenceInterval
            marginOfError
            activationDate
            completionDate
            ageFilter {
              min
              max
            }
            excludedAdminAreasFilter
            sexFilter
          }
        }
      }
      program {
        id
        name
        caId
      }
      paymentRecords {
        totalCount
        edgeCount
        edges {
          node {
            targetPopulation {
              id
              name
            }
          }
        }
      }
    }
  }
`;
