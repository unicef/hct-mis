import { gql } from 'apollo-boost';

export const individualMinimal = gql`
  fragment individualMinimal on IndividualNode {
    id
    lastRegistrationDate
    createdAt
    updatedAt
    fullName
    sex
    unicefId
    birthDate
    maritalStatus
    phoneNo
    sanctionListPossibleMatch
    deduplicationGoldenRecordStatus
    sanctionListLastCheck
    role
    relationship
    status
    documents {
      edges {
        node {
          id
          documentNumber
          type {
            country
            label
          }
        }
      }
    }

    household {
      id
      unicefId
      status
      adminArea {
        id
        title
        adminAreaType {
          adminLevel
        }
      }
      programs {
        edges {
          node {
            id
            name
          }
        }
      }
    }
  }
`;

export const individualDetailed = gql`
  fragment individualDetailed on IndividualNode {
    ...individualMinimal
    givenName
    familyName
    estimatedBirthDate
    pregnant
    status
    documents {
      edges {
        node {
          id
          type {
            country
            label
          }
          documentNumber
        }
      }
    }
    enrolledInNutritionProgramme
    administrationOfRutf
    identities {
      number
      type
    }
    household {
      status
      id
      address
      countryOrigin
      adminArea {
        id
        title
        level
      }
    }
    role
    relationship
    headingHousehold {
      id
      headOfHousehold {
        id
      }
    }
    flexFields
  }
`;
