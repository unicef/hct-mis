import { gql } from 'apollo-boost';

export const CreateProgrm = gql`
    mutation CreateProgram($programData: CreateProgramInput!) {
      createProgram(programData: $programData) {
        program {
          id
          name
          status
          startDate
          endDate
          programCaId
          budget
          description
          frequencyOfPayments
          sector
          scope
          cashPlus
          populationGoal
        }
      }
    }
`