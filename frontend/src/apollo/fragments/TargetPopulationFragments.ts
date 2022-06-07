import { gql } from 'apollo-boost';

export const targetPopulationMinimal = gql`
  fragment targetPopulationMinimal on TargetPopulationNode {
    id
    name
    status
    createdAt
    updatedAt
    candidateListTotalHouseholds
    finalListTotalHouseholds
    program {
      id
      name
    }
    createdBy {
      id
      firstName
      lastName
    }
  }
`;
export const targetPopulationDetailed = gql`
  fragment targetPopulationDetailed on TargetPopulationNode {
    id
    name
    status
    candidateListTotalHouseholds
    candidateListTotalIndividuals
    finalListTotalHouseholds
    finalListTotalIndividuals
    caHashId
    excludedIds
    exclusionReason
    steficonRule {
      id
      rule {
        id
        name
      }
    }
    vulnerabilityScoreMin
    vulnerabilityScoreMax
    changeDate
    finalizedAt
    finalizedBy {
      id
      firstName
      lastName
    }
    program {
      id
      name
      status
    }
    createdBy {
      id
      firstName
      lastName
    }
    candidateListTargetingCriteria {
      targetPopulationCandidate {
        createdBy {
          id
          firstName
          lastName
        }
      }
      rules {
        id
        individualsFiltersBlocks {
          individualBlockFilters {
            fieldName
            isFlexField
            arguments
            comparisionMethod
            fieldAttribute {
              name
              labelEn
              type
              choices {
                value
                labelEn
              }
            }
          }
        }
        filters {
          fieldName
          isFlexField
          arguments
          comparisionMethod
          fieldAttribute {
            name
            labelEn
            type
            choices {
              value
              labelEn
            }
          }
        }
      }
    }
    finalListTargetingCriteria {
      targetPopulationFinal {
        createdBy {
          id
          firstName
          lastName
        }
      }
      rules {
        id
        filters {
          fieldName
          isFlexField
          arguments
          comparisionMethod
          fieldAttribute {
            name
            labelEn
            type
            choices {
              value
              labelEn
            }
          }
        }
      }
    }
    candidateStats {
      childMale
      childFemale
      adultMale
      adultFemale
      allHouseholds
      allIndividuals
    }
    finalStats {
      childMale
      childFemale
      adultMale
      adultFemale
    }
  }
`;
