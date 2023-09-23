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
      caHashId
      description
      budget
      frequencyOfPayments
      cashPlus
      populationGoal
      scope
      sector
      totalNumberOfHouseholds
      totalNumberOfHouseholdsWithTpInProgram
      administrativeAreasOfImplementation
      individualDataNeeded
      version
      dataCollectingType {
        code
        description
        active
        individualFiltersAvailable
      }
    }
  }
`;
