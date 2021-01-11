import { gql } from 'apollo-boost';

export const PROGRAM_QUERY = gql`
  query Program($id: ID!) {
    program(id: $id) {
      id
      name
      startDate
      endDate
      status
      caId
      description
      budget
      frequencyOfPayments
      cashPlus
      populationGoal
      scope
      sector
      totalNumberOfHouseholds
      administrativeAreasOfImplementation
      individualDataNeeded
      version
    }
  }
`;
