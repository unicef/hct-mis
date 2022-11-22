import { gql } from 'apollo-boost';

export const REPORT_QUERY = gql`
  query Report($id: ID!) {
    report(id: $id) {
      id
      status
      reportType
      createdAt
      updatedAt
      dateFrom
      dateTo
      fileUrl
      numberOfRecords
      createdBy {
        firstName
        lastName
      }
      adminArea2 {
        edges {
          node {
            name
          }
        }
      }
      adminArea1 {
        name
      }
      program {
        name
      }
    }
  }
`;
