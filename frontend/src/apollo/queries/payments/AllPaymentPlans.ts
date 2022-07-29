import { gql } from 'apollo-boost';

export const PAYMENT_PLAN_LIST_QUERY = gql`
  query AllPaymentPlans (
    $businessArea: String!
    $search: String
    $status: [String]
    $totalEntitledQuantity: String
    $dispersionStartDate: Date
    $dispersionEndDate: Date
  ) {
    allPaymentPlans (
      businessArea: $businessArea
      search: $search
      status: $status
      totalEntitledQuantity: $totalEntitledQuantity
      dispersionStartDate: $dispersionStartDate
      dispersionEndDate: $dispersionEndDate
    ) {
      isRemoved
      id
      createdAt
      businessArea {
        id
        slug
        code
        name
        longName
      }
      statusDate
      startDate
      endDate
      program {
        isRemoved
        id
        createdAt
        updatedAt
        version
        name
        status
        startDate
        endDate
        description
        caId
        caHashId
        budget
      }
      exchangeRate
      totalEntitledQuantity
      totalEntitledQuantityUsd
      totalEntitledQuantityRevised
      totalEntitledQuantityRevisedUsd
      totalDeliveredQuantity
      totalDeliveredQuantityUsd
      createdBy {
        id
        username
        firstName
        lastName
      }
      status
      unicefId
      targetPopulation {
        name
        id
      }
      currency
      dispersionStartDate
      dispersionEndDate
      femaleChildrenCount
      maleChildrenCount
      femaleAdultsCount
      maleAdultsCount
      totalHouseholdsCount
      totalIndividualsCount
    }
  }
`;
