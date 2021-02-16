
      export interface IntrospectionResultData {
        __schema: {
          types: {
            kind: string;
            name: string;
            possibleTypes: {
              name: string;
            }[];
          }[];
        };
      }
      const result: IntrospectionResultData = {
  "__schema": {
    "types": [
      {
        "kind": "INTERFACE",
        "name": "Node",
        "possibleTypes": [
          {
            "name": "LogEntryNode"
          },
          {
            "name": "UserNode"
          },
          {
            "name": "UserBusinessAreaNode"
          },
          {
            "name": "AdminAreaTypeNode"
          },
          {
            "name": "AdminAreaNode"
          },
          {
            "name": "HouseholdNode"
          },
          {
            "name": "IndividualNode"
          },
          {
            "name": "RegistrationDataImportNode"
          },
          {
            "name": "PaymentRecordNode"
          },
          {
            "name": "CashPlanNode"
          },
          {
            "name": "ProgramNode"
          },
          {
            "name": "TargetPopulationNode"
          },
          {
            "name": "SteficonRuleNode"
          },
          {
            "name": "ReportNode"
          },
          {
            "name": "CashPlanPaymentVerificationNode"
          },
          {
            "name": "PaymentVerificationNode"
          },
          {
            "name": "TicketPaymentVerificationDetailsNode"
          },
          {
            "name": "ServiceProviderNode"
          },
          {
            "name": "TicketComplaintDetailsNode"
          },
          {
            "name": "TicketSensitiveDetailsNode"
          },
          {
            "name": "TicketIndividualDataUpdateDetailsNode"
          },
          {
            "name": "TicketDeleteIndividualDetailsNode"
          },
          {
            "name": "TicketSystemFlaggingDetailsNode"
          },
          {
            "name": "SanctionListIndividualNode"
          },
          {
            "name": "SanctionListIndividualDocumentNode"
          },
          {
            "name": "SanctionListIndividualNationalitiesNode"
          },
          {
            "name": "SanctionListIndividualCountriesNode"
          },
          {
            "name": "SanctionListIndividualAliasNameNode"
          },
          {
            "name": "SanctionListIndividualDateOfBirthNode"
          },
          {
            "name": "DocumentNode"
          },
          {
            "name": "TicketHouseholdDataUpdateDetailsNode"
          },
          {
            "name": "TicketAddIndividualDetailsNode"
          },
          {
            "name": "GrievanceTicketNode"
          },
          {
            "name": "TicketNoteNode"
          },
          {
            "name": "TicketNeedsAdjudicationDetailsNode"
          },
          {
            "name": "BusinessAreaNode"
          },
          {
            "name": "ImportedHouseholdNode"
          },
          {
            "name": "ImportedIndividualNode"
          },
          {
            "name": "RegistrationDataImportDatahubNode"
          },
          {
            "name": "ImportDataNode"
          },
          {
            "name": "ImportedDocumentNode"
          }
        ]
      }
    ]
  }
};
      export default result;
    