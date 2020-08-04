import { gql } from 'apollo-boost';

export const individualMinimal = gql`
  fragment individualMinimal on IndividualNode {
    id
    createdAt
    updatedAt
    fullName
    sex
    birthDate
    maritalStatus
    phoneNo
    role
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
      status
      adminArea{
        id
        title
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
    status
    enrolledInNutritionProgramme
    administrationOfRutf
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
    headingHousehold {
      id
      headOfHousehold {
        id
      }
    }
    flexFields
  }
`;
