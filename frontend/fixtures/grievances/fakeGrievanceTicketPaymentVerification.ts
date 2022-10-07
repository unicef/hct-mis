import { GrievanceTicketNode } from '../../src/__generated__/graphql';

export const fakeGrievanceTicketPaymentVerification = {
  id:
    'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ZTY1N2JiZC1hNzM4LTQ0MTktYjlmOS04YTIyOWI2MGUwNzU=',
  unicefId: 'GRV-000004',
  status: 5,
  category: 1,
  consent: true,
  createdBy: null,
  createdAt: '2022-04-08T09:22:18.806856',
  updatedAt: '2022-04-11T09:14:45.395754',
  description: '',
  language: '',
  admin: null,
  admin2: null,
  area: '',
  assignedTo: null,
  individual: null,
  household: null,
  paymentRecord: null,
  relatedTickets: [],
  addIndividualTicketDetails: null,
  individualDataUpdateTicketDetails: null,
  householdDataUpdateTicketDetails: null,
  deleteIndividualTicketDetails: null,
  deleteHouseholdTicketDetails: null,
  systemFlaggingTicketDetails: null,
  paymentVerificationTicketDetails: {
    id:
      'VGlja2V0UGF5bWVudFZlcmlmaWNhdGlvbkRldGFpbHNOb2RlOmQ5NWFlNzA2LWRmNTQtNDYyMi1hODVmLTRiOGExZTg2Y2VhMQ==',
    newStatus: null,
    newReceivedAmount: 45,
    approveStatus: false,
    paymentVerificationStatus: 'NOT_RECEIVED',
    hasMultiplePaymentVerifications: false,
    paymentVerification: {
      id:
        'UGF5bWVudFZlcmlmaWNhdGlvbk5vZGU6NDhmZjMwODEtNTVhMy00Zjg4LWJjNTgtNTE0YWM0MGI0MzQ2',
      receivedAmount: 0,
      paymentObjectId: null,
      paymentContentType: null,
      // paymentRecord: {
  //       id:
  //         'UGF5bWVudFJlY29yZE5vZGU6MDZlODg0ZjQtYzAxNS00Mzk2LWI3YmItMDc4NDZkODBkNGQx',
  //       deliveredQuantity: 3355,
  //       __typename: 'PaymentRecordNode',
  //     },
  //     __typename: 'PaymentVerificationNode',
  //   },
    // paymentVerifications: {
    //   edges: [],
    //   __typename: 'PaymentVerificationNodeConnection',
    // }
    },
    __typename: 'TicketPaymentVerificationDetailsNode',
  },
  needsAdjudicationTicketDetails: null,
  issueType: null,
  ticketNotes: { edges: [], __typename: 'TicketNoteNodeConnection' },
  __typename: 'GrievanceTicketNode',
} as GrievanceTicketNode;
