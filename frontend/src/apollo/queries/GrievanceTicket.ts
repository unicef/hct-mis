import { gql } from 'apollo-boost';

export const GrievanceTicket = gql`
  query GrievanceTicket($id: ID!) {
    grievanceTicket(id: $id) {
      id
      status
      category
      consent
      createdBy {
        id
        firstName
        lastName
        email
      }
      createdAt
      updatedAt
      description
      language
      admin
      area
      assignedTo {
        id
        firstName
        lastName
        email
      }
      individual {
        id
        unicefId
      }
      household {
        id
        unicefId
      }
      paymentRecord {
        id
      }
      linkedTickets {
        edges {
          node {
            id
            status
            household {
              id
              unicefId
            }
          }
        }
      }
      addIndividualTicketDetails{
        id
        individualData
        household{
          id
          unicefId
        }
      }
      issueType
      ticketNotes {
        edges {
          node {
            id
            createdAt
            updatedAt
            description
            createdBy {
              id
              firstName
              lastName
              email
            }
          }
        }
      }
    }
  }
`;
