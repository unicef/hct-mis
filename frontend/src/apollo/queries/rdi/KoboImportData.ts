import { gql } from 'apollo-boost';

export const KOBO_IMPORT_DATA_QUERY = gql`
  query KoboImportData($id: ID!) {
    koboImportData(id: $id) {
      id
      status
      numberOfIndividuals
      numberOfHouseholds
      error
      koboValidationErrors {
        header
        message
      }
    }
  }
`;
