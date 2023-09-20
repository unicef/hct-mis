import { gql } from 'apollo-boost';

export const UPDATE_PROGRAM_CYCLE = gql`
  mutation UpdateProgramCycle($programCycleData: UpdateProgramCycleInput!) {
    updateProgramCycle(programCycleData: $programCycleData) {
      program {
        id
        cycles {
          edges {
            node {
              id
              unicefId
              name
              status
              totalEntitledQuantityUsd
              totalUndeliveredQuantityUsd
              totalUndeliveredQuantityUsd
              startDate
              endDate
            }
          }
        }
      }
    }
  }
`;
