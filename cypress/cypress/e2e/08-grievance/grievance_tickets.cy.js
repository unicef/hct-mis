import Grievance from "../../page-objects/pages/grievance/grievance_tickets.po";
import GrievanceDetailsPage from "../../page-objects/pages/grievance/details_grievance_page.po";
import NewTicket from "../../page-objects/pages/grievance/new_ticket.po";

let grievancePage = new Grievance();
let grievanceDetailsPage = new GrievanceDetailsPage();
let newTicketPage = new NewTicket();

describe("Grievance", () => {
  before(function () {
    cy.fixture("grievance_new_ticket").as("newTicket");
  });
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
    grievancePage.clickMenuButtonGrievance();
  });

  describe("Smoke tests Grievance", () => {
    it("Check Grievance page", () => {
      cy.scenario([
        "Go to Grievance page",
        "Elements of Grievance menu are visible",
        "Check if all elements on page exist",
      ]);
      grievancePage.checkGrievanceMenu();
      grievancePage.checkElementsOnUserGeneratedPage();
      grievancePage.checkElementsOnSystemGeneratedPage();
    });
    it("Check Grievance Details page", () => {
      cy.scenario([
        "Go to Grievance page",
        "Press tab: System-Generated",
        "Choose first row from Grievance Tickets List",
        "Check if all elements on details page exist",
      ]);
      grievancePage.getTabSystemGenerated().click();
      cy.url().should("include", "/system-generated");
      // ToDo: After fix bug: 164824
      grievancePage
        .getTicketListRow()
        .eq(0)
        .find("a")
        .contains("GRV-0000003")
        .click();
      grievanceDetailsPage.checkGrievanceMenu();
      grievanceDetailsPage.getButtonAssignToMe().should("be.visible");
      grievanceDetailsPage.checkElementsOnPage();
      grievanceDetailsPage
        .getCreateLinkedTicket()
        .scrollIntoView()
        .should("be.visible");
      grievanceDetailsPage
        .getMarkDuplicate()
        .scrollIntoView()
        .should("be.visible");
      grievanceDetailsPage.checkElementsCells();
    });
    it("Check Grievance New Ticket page", () => {
      cy.scenario([
        "Go to Grievance page",
        "Press New Ticket button",
        "Check if all elements on details page exist",
      ]);
      grievancePage.getButtonNewTicket().click();
      newTicketPage.checkElementsOnPage();
    });
  });

  describe("Component tests Grievance", () => {
    context("Export", () => {
      it.skip("Export", () => {});
    });
    context("Grievance Filters", () => {
      [
        ["USER-GENERATED", "GRV-0000001", 1, "Ticket ID: GRV-0000001"],
        ["SYSTEM-GENERATED", "GRV-0000003", 1, "Ticket ID: GRV-0000003"],
      ].forEach((testData) => {
        it("Grievance Search filter " + testData[0], () => {
          cy.scenario([
            "Go to Grievance page",
            "Choose tab: " + testData[0],
            'Type in Search filter "Not Exist"',
            "Press button Apply",
            "Check if Tickets List is empty",
            "Press button Clear",
            "Type in Search filter " + testData[1],
            "Press button Apply",
            `Check if Tickets List has ${testData[2]} rows`,
            "Press first row from Ticket List and check data",
            "Come back to Grievance Page",
          ]);
          grievancePage.chooseTab(testData[0]);
          grievancePage.useSearchFilter("Not Exist");
          grievancePage.expectedNumberOfRows(0);
          grievancePage.getButtonClear().click();
          grievancePage.useSearchFilter(testData[1]);
          grievancePage.expectedNumberOfRows(testData[2]);
          grievancePage.chooseTicketListRow(0, testData[1]).click();
          grievanceDetailsPage.getTitle().contains(testData[3]);
        });
      });
      [
        [
          "USER-GENERATED",
          "HH-20-0000.0001",
          1,
          "Kowalska",
          1,
          "Ticket ID: GRV-0000005",
          "GRV-0000005",
        ],
        [
          "SYSTEM-GENERATED",
          "HH-20-0000.0002",
          1,
          "Romaniak",
          1,
          "Ticket ID: GRV-0000003",
          "GRV-0000003",
        ],
      ].forEach((testData) => {
        it("Grievance Search Type filter " + testData[0], () => {
          cy.scenario([
            "Go to Grievance page",
            "Choose tab: " + testData[0],
            "Change ticket type filter to Household ID",
            "Change ticket type filter to Ticket ID",
            "Change ticket type filter to Last Name",
            "Change ticket type filter to Household ID",
            'Type in Search filter "Not Exist"',
            "Press button Apply",
            "Check if Tickets List is empty",
            "Press button Clear",
            "Change ticket type filter to Household ID",
            "Type in Search filter " + testData[1],
            "Press button Apply",
            `Check if Tickets List has ${testData[2]} rows`,
            "Press first row from Ticket List and check data",
            "Come back to Grievance Page",
            "Change ticket type filter to Last Name",
            'Type in Search filter "Not Exist"',
            "Press button Apply",
            "Check if Tickets List is empty",
            "Press button Clear",
            "Change ticket type filter to Household ID",
            "Type in Search filter " + testData[3],
            "Press button Apply",
            `Check if Tickets List has ${testData[4]} rows`,
            "Press first row from Ticket List and check data",
            "Come back to Grievance Page",
          ]);
          grievancePage.chooseTab(testData[0]);
          grievancePage.checkTicketTypeFilterText("Ticket ID");
          grievancePage.chooseTicketTypeHouseholdID();
          grievancePage.checkTicketTypeFilterText("Household ID");
          grievancePage.chooseTicketTypeTicketID();
          grievancePage.checkTicketTypeFilterText("Ticket ID");
          grievancePage.chooseTicketTypeLastName();
          grievancePage.checkTicketTypeFilterText("Last Name");
          grievancePage.chooseTicketTypeHouseholdID();
          grievancePage.useSearchFilter("Not Exist");
          grievancePage.expectedNumberOfRows(0);
          grievancePage.getButtonClear().click();
          grievancePage.chooseTicketTypeHouseholdID();
          grievancePage.useSearchFilter(testData[1]);
          grievancePage.expectedNumberOfRows(testData[2]);
          grievancePage.chooseTicketListRow(0, testData[6]).click();
          grievanceDetailsPage.getTitle().contains(testData[5]);
          grievanceDetailsPage.pressBackButton();

          grievancePage.getButtonClear().click();
          grievancePage.chooseTicketTypeLastName();
          grievancePage.useSearchFilter("Not Exist");
          grievancePage.expectedNumberOfRows(0);
          grievancePage.getButtonClear().click();
          grievancePage.chooseTicketTypeLastName();
          grievancePage.useSearchFilter(testData[3]);
          grievancePage.expectedNumberOfRows(testData[4]);
        });
      });
      [
        ["Assigned", 1, "GRV-0000005"],
        ["For Approval", 1, "GRV-0000001"],
        ["In Progress", 1, "GRV-0000004"],
        ["On Hold", 1, "GRV-0000002"],
      ].forEach((testData) => {
        it(`Grievance Status filter ${testData[0]}`, () => {
          grievancePage.chooseStatusFilter(testData[0]);
          grievancePage.expectedNumberOfRows(testData[1]);
          grievancePage.chooseTicketListRow(0, testData[2]);
        });
      });
      it("Grievance FSP filter", () => {
        // ToDo After fix bug: 165198
      });
      [
        ["USER-GENERATED", 1],
        ["SYSTEM-GENERATED", 0],
      ].forEach((testData) => {
        it(`Grievance Creation Date From filter of ${testData[0]} tab`, () => {
          grievancePage.chooseTab(testData[0]);
          grievancePage.changeCreationDateFrom("2024-01-01");
          grievancePage.checkDateFilterFrom("2024-01-01");
          grievancePage.openCreationDateFromFilter();
          grievancePage.checkDateTitleFilter("Mon, Jan 1");
          grievancePage.openCreationDateFromFilter();
          grievancePage.chooseDayFilterPopup(20);
          grievancePage.checkDateFilterFrom("2024-01-20");
          grievancePage.getButtonApply().click();
          grievancePage.expectedNumberOfRows(testData[1]);
        });
      });
      [
        ["USER-GENERATED", 3],
        ["SYSTEM-GENERATED", 1],
      ].forEach((testData) => {
        it(`Grievance Creation Date To filter of ${testData[0]} tab`, () => {
          grievancePage.chooseTab(testData[0]);
          grievancePage.changeCreationDateTo("2024-01-01");
          grievancePage.checkDateFilterTo("2024-01-01");
          grievancePage.openCreationDateToFilter();
          grievancePage.checkDateTitleFilter("Mon, Jan 1");
          grievancePage.openCreationDateToFilter();
          grievancePage.chooseDayFilterPopup(20);
          grievancePage.checkDateFilterTo("2024-01-20");
          grievancePage.getButtonApply().click();
          grievancePage.expectedNumberOfRows(testData[1]);
        });
      });

      [
        ["Data Change", "GRV-0000005"],
        // ["Sensitive Grievance", "GRV-0000004"], ToDo: 166077
        ["Referral", "GRV-0000001"],
        // ["Grievance Complaint", "GRV-0000001"], ToDo: 166077
      ].forEach((testData) => {
        it(`Grievance Category filter - ${testData[0]}`, () => {
          grievancePage.chooseCategoryFilter(testData[0]);
          grievancePage.chooseTicketListRow(0, testData[1]);
        });
      });
      it(`Grievance Admin Level 2 filter - USER-GENERATED`, () => {
        grievancePage.chooseAdminFilter("Andarab");
        grievancePage.chooseTicketListRow(1, "GRV-0000002");
      });
      it(`Grievance Admin Level 2 filter - SYSTEM-GENERATED`, () => {
        grievancePage.chooseTab("SYSTEM-GENERATED");
        grievancePage.chooseAdminFilter("Andarab");
        grievancePage.expectedNumberOfRows(0);
      });
      [
        ["USER-GENERATED", 2],
        ["SYSTEM-GENERATED", 0],
      ].forEach((testData) => {
        it(`Grievance Assignee filter - ${testData[0]}`, () => {
          grievancePage.chooseTab(testData[0]);
          grievancePage.chooseAssigneeFilter("root@root.com");
          grievancePage.expectedNumberOfRows(testData[1]);
        });
      });
      it("Grievance Similarity Score filter", () => {
        grievancePage.chooseTab("SYSTEM-GENERATED");
        grievancePage.getSimilarityScoreFromFilter().type(5);
        grievancePage.getButtonApply().click();
        grievancePage.expectedNumberOfRows(1);
        grievancePage.getSimilarityScoreFromFilter().clear().type(10);
        grievancePage.getButtonApply().click();
        grievancePage.expectedNumberOfRows(0);
        grievancePage.getButtonClear().click();
        grievancePage.expectedNumberOfRows(1);
        grievancePage.getSimilarityScoreFromFilter().type(5);
        grievancePage.getSimilarityScoreToFilter().type(10);
        grievancePage.getButtonApply().click();
        grievancePage.expectedNumberOfRows(1);
        grievancePage.getSimilarityScoreFromFilter().clear().type(4);
        grievancePage.getSimilarityScoreToFilter().clear().type(5);
        grievancePage.getButtonApply().click();
        grievancePage.expectedNumberOfRows(0);
      });
      [
        ["USER-GENERATED", "GRV-0000001"],
        ["SYSTEM-GENERATED", "GRV-0000003"],
      ].forEach((testData) => {
        it("Grievance Registration Date Import filter", () => {
          grievancePage.chooseTab(testData[0]);
          grievancePage.chooseRDIFilter("Test");
          grievancePage.expectedNumberOfRows(1);
          grievancePage.chooseTicketListRow(0, testData[1]);
        });
      });
      it.skip("Grievance Preferred language filter", () => {
        // ToDo: Language filter does not work.
      });
      [
        ["USER-GENERATED", "High", 1, "GRV-0000005"],
        ["USER-GENERATED", "Low", 1, "GRV-0000002"],
        ["USER-GENERATED", "Medium", 2, "GRV-0000001"],
        ["SYSTEM-GENERATED", "Not set", 1, "GRV-0000003"],
      ].forEach((testData) => {
        it(`Grievance Priority filter - ${testData[1]}`, () => {
          grievancePage.chooseTab(testData[0]);
          grievancePage.choosePriorityFilter(testData[1]);
          grievancePage.expectedNumberOfRows(testData[2]);
          grievancePage.chooseTicketListRow(0, testData[3]);
        });
      });
      [
        ["USER-GENERATED", "Very urgent", 1, "GRV-0000005"],
        ["USER-GENERATED", "Urgent", 2, "GRV-0000001"],
        ["USER-GENERATED", "Not urgent", 1, "GRV-0000002"],
        ["SYSTEM-GENERATED", "Not set", 1, "GRV-0000003"],
      ].forEach((testData) => {
        it(`Grievance Urgency filter - ${testData[1]}`, () => {
          grievancePage.chooseTab(testData[0]);
          grievancePage.chooseUrgencyFilter(testData[1]);
          grievancePage.expectedNumberOfRows(testData[2]);
          grievancePage.chooseTicketListRow(0, testData[3]);
        });
      });
      it("Grievance Active Tickets filter", () => {});
    });
    context("Create New Ticket", () => {
      beforeEach(() => {
        grievancePage.getButtonNewTicket().click();
        newTicketPage.checkElementsOnPage();
      });
      // ToDo: I don't think it is necessary to test each issue type for Sensitive Grievance category. Issue types are the only things that differ.
      // It makes sense to test all different issue types for Data Change tickets as they have different fields.
      ["DataChangeAddIndividual"].forEach((testData) => {
        it("Create New Ticket - Data Change - Add Individual", function () {
          let newTicket = this.newTicket[testData];
          newTicketPage.chooseCategory(newTicket.category);
          newTicketPage.chooseIssueType(newTicket.issueType);
          newTicketPage
            .getLabelCategoryDescription()
            .contains(
              newTicketPage.textCategoryDescription[newTicket.category]
            );
          newTicketPage
            .getLabelIssueTypeDescription()
            .contains(
              newTicketPage.textIssueTypeDescription[newTicket.issueType]
            );
          newTicketPage.getButtonNext().click();
          newTicketPage.getHouseholdTab().should("be.visible");
          newTicketPage.getHouseholdTableRows(0).click();
          newTicketPage.getButtonNext().click();
          newTicketPage.getReceivedConsent().click();
          newTicketPage.getButtonNext().click();
          newTicketPage.getDescription().type(newTicket.description);
          newTicketPage.getComments().type(newTicket.comment);
          newTicketPage.getAdminAreaAutocomplete().click();
          newTicketPage.getOption().contains(newTicket.adminArea).click();
          newTicketPage.getInputArea().type(newTicket.inputArea);
          newTicketPage.getInputLanguage().type(newTicket.inputLanguage);
          newTicketPage.getSelectPriority().click();
          newTicketPage.getOption().contains(newTicket.priority).click();
          newTicketPage.getSelectUrgency().click();
          newTicketPage.getOption().contains(newTicket.urgency).click();
          newTicketPage.getLookUpButton().click();
          newTicketPage.getCheckbox().eq(0).contains(newTicket.lookUp);
          newTicketPage.getCheckbox().eq(0).click();
          newTicketPage.getButtonNext().eq(1).click();
          newTicketPage.getIndividualID().contains(newTicket.individualID);
          newTicketPage.getHouseholdID().contains(newTicket.householdID);
          newTicketPage.getIssueTypeLabel().contains(newTicket.issueType);
          newTicketPage.getCategory().contains(newTicket.category);
          newTicketPage.getWhoAnswersPhone().type(newTicket.whoAnswersPhone);
          newTicketPage
            .getWhoAnswersAltPhone()
            .type(newTicket.whoAnswersAltPhone);
          newTicketPage.getRole().click();
          newTicketPage
            .getOptionUndefined()
            .eq(2)
            .contains(newTicket.role)
            .click();
          newTicketPage.getRelationship().click();
          newTicketPage
            .getOptionUndefined()
            .eq(5)
            .contains(newTicket.relationship)
            .click();
          newTicketPage.getPhoneNo().type(newTicket.phoneNo);
          newTicketPage.getMiddleName().type(newTicket.middleName);
          newTicketPage.getMaritalStatus().click();
          newTicketPage
            .getOptionUndefined()
            .eq(0)
            .contains(newTicket.maritalStatus)
            .click();
          newTicketPage.getPregnant().click();
          newTicketPage.getOptionZero().contains(newTicket.pregnant).click();
          newTicketPage.getDisability().click();
          newTicketPage
            .getOptionUndefined()
            .eq(1)
            .contains(newTicket.disability)
            .click();
          // ToDo: Uncomment after resolve bug: 167376
          // newTicketPage.getEmail().type(newTicket.email);
          newTicketPage.getPhysicalDisability().click();
          newTicketPage
            .getOptionUndefined()
            .eq(1)
            .contains(newTicket.physicalDisability)
            .click();
          newTicketPage.getsSeeingDisability().click();
          newTicketPage
            .getOptionUndefined()
            .eq(3)
            .contains(newTicket.seeingDisability)
            .click();
          newTicketPage.getMemoryDisability().click();
          newTicketPage
            .getOptionUndefined()
            .eq(0)
            .contains(newTicket.memoryDisability)
            .click();
          newTicketPage.getHearingDisability().click();
          newTicketPage
            .getOptionUndefined()
            .eq(3)
            .contains(newTicket.hearingDisability)
            .click();
          newTicketPage.getCommsDisability().click();
          newTicketPage
            .getOptionUndefined()
            .eq(3)
            .contains(newTicket.commsDisability)
            .click();
          newTicketPage.getGivenName().type(newTicket.givenName);
          newTicketPage.getGender().click();
          newTicketPage.getOptionUndefined().contains(newTicket.gender).click();
          newTicketPage.getFullName().type(newTicket.fullName);
          newTicketPage.getFamilyName().type(newTicket.familyName);
          newTicketPage.getEstimatedBirthDate().click();
          newTicketPage
            .getOptionOne()
            .contains(newTicket.estimatedBirthDate)
            .click();
          newTicketPage.getWorkStatus().click();
          newTicketPage
            .getOptionUndefined()
            .contains(newTicket.workStatus)
            .click();
          newTicketPage.getObservedDisability().click();
          newTicketPage.getOptionUndefined().eq(0).click();
          newTicketPage.getOptionUndefined().eq(1).click();
          newTicketPage.getOptionUndefined().eq(2).click().type("{esc}");
          newTicketPage.getSelfcareDisability().click();
          newTicketPage
            .getOptionUndefined()
            .contains(newTicket.selfcareDisability)
            .click();
          newTicketPage.getBirthDate().type(newTicket.birthDate);
          newTicketPage
            .getPhoneNoAlternative()
            .type(newTicket.phoneNoAlternative);
          newTicketPage.getButtonNext().contains("Save").click();

          grievanceDetailsPage.checkElementsOnPage(
            grievanceDetailsPage.textStatusAssigned,
            newTicket.priority,
            newTicket.urgency,
            grievanceDetailsPage.textNotAssigment,
            newTicket.category
          );
          grievanceDetailsPage
            .getAdministrativeLevel()
            .contains(newTicket.adminArea);
          grievanceDetailsPage
            .getLanguagesSpoken()
            .contains(newTicket.inputLanguage);
          grievanceDetailsPage.getAreaVillage().contains(newTicket.inputArea);
          grievanceDetailsPage
            .getLabelIssueType()
            .contains(newTicket.issueType);
          grievanceDetailsPage.getLabelTickets().contains(newTicket.lookUp);
          grievanceDetailsPage.getLabelGENDER().contains(newTicket.gender);
          grievanceDetailsPage.getLabelRole().contains(newTicket.role);
          grievanceDetailsPage.getLabelPhoneNo().contains(newTicket.phoneNo);
          grievanceDetailsPage.getLabelPregnant().contains(newTicket.pregnant);
          grievanceDetailsPage.getLabelFullName().contains(newTicket.fullName);
          grievanceDetailsPage
            .getLabelBirthDate()
            .contains(newTicket.birthDate);
          // Todo: Fix after resolve bug: 167436
          // grievanceDetailsPage.getLabelDisability().contains("not disabled");
          grievanceDetailsPage
            .getLabelGivenName()
            .contains(newTicket.givenName);
          grievanceDetailsPage
            .getLabelFamilyName()
            .contains(newTicket.familyName);
          grievanceDetailsPage
            .getLabelMiddleName()
            .contains(newTicket.middleName);
          grievanceDetailsPage
            .getLabelWorkStatus()
            .contains(newTicket.workStatus);
          grievanceDetailsPage
            .getLabelRelationship()
            .contains(newTicket.relationship);
          grievanceDetailsPage
            .getLabelMaritalStatus()
            .contains(newTicket.maritalStatus);
          grievanceDetailsPage
            .getLabelCommsDisability()
            .contains(newTicket.commsDisability);
          // Todo: Fix after resolve bug: 167426 - MEMORY DISABILITY
          // grievanceDetailsPage.getLabelMEMORYDISABILITY().contains("");
          grievanceDetailsPage
            .getLabelSeeingDisability()
            .contains(newTicket.seeingDisability);
          grievanceDetailsPage
            .getLabelWhoAnswersPhone()
            .contains(newTicket.whoAnswersPhone);
          grievanceDetailsPage
            .getLabelHearingDisability()
            .contains(newTicket.hearingDisability);
          // Todo: Fix after resolve bug: 167436 - OBSERVED DISABILITY
          // grievanceDetailsPage.getLabelObservedDisability().contains("");
          grievanceDetailsPage
            .getLabelPhysicalDisability()
            .contains(newTicket.physicalDisability);
          grievanceDetailsPage
            .getLabelSelfcareDisability()
            .contains(newTicket.selfcareDisability);
          grievanceDetailsPage
            .getLabelEstimatedBirthDate()
            .contains(newTicket.estimatedBirthDate);
          grievanceDetailsPage
            .getLabelPhoneNoAlternative()
            .contains(newTicket.phoneNoAlternative);
          grievanceDetailsPage
            .getLabelWhoAnswersAltPhone()
            .contains(newTicket.whoAnswersAltPhone);
        });
      });
      ["Household Data Update - 1", "Household Data Update - 2"].forEach(
        (testData) => {
          it(`Create New Ticket - Data Change - ${testData}`, function () {
            let newTicket = this.newTicket[testData];
            newTicketPage.chooseCategory(newTicket.category);
            newTicketPage.chooseIssueType(newTicket.issueType);
            newTicketPage
              .getLabelCategoryDescription()
              .contains(
                newTicketPage.textCategoryDescription[newTicket.category]
              );
            newTicketPage
              .getLabelIssueTypeDescription()
              .contains(
                newTicketPage.textIssueTypeDescription[newTicket.issueType]
              );
            newTicketPage.getButtonNext().click();
            newTicketPage.getHouseholdTab().should("be.visible");
            newTicketPage.getHouseholdTableRows(0).click();
            // ToDo: Delete after fixed: 167943
            // newTicketPage.getIndividualTab().parent().should("not.be.disabled")
            newTicketPage.getButtonNext().click();
            newTicketPage.getReceivedConsent().click();
            newTicketPage.getButtonNext().click();
            newTicketPage.getDescription().type(newTicket.description);
            newTicketPage.getComments().type(newTicket.comment);
            newTicketPage.getAdminAreaAutocomplete().click();
            newTicketPage.getOption().contains(newTicket.adminArea).click();
            newTicketPage.getInputArea().type(newTicket.inputArea);
            newTicketPage.getInputLanguage().type(newTicket.inputLanguage);
            newTicketPage.getSelectPriority().click();
            newTicketPage.getOption().contains(newTicket.priority).click();
            newTicketPage.getSelectUrgency().click();
            newTicketPage.getOption().contains(newTicket.urgency).click();
            newTicketPage.getLookUpButton().click();
            newTicketPage.getCheckbox().eq(0).contains(newTicket.lookUp);
            newTicketPage.getCheckbox().eq(0).click();
            newTicketPage.getButtonNext().eq(1).click();
            newTicketPage.getSelectFieldName().click();
            newTicketPage.selectOption(newTicket.householdDataField).click();
            newTicketPage.getInputValue().type("1");
            newTicketPage.getButtonNext().contains("Save").click();

            grievanceDetailsPage.checkElementsOnPage(
              grievanceDetailsPage.textStatusAssigned,
              newTicket.priority,
              newTicket.urgency,
              grievanceDetailsPage.textNotAssigment,
              newTicket.category
            );
            grievanceDetailsPage
              .getTicketIndividualID()
              .contains(newTicket.individualID);
            grievanceDetailsPage
              .getAdministrativeLevel()
              .contains(newTicket.adminArea);
            grievanceDetailsPage
              .getLanguagesSpoken()
              .contains(newTicket.inputLanguage);
            grievanceDetailsPage.getAreaVillage().contains(newTicket.inputArea);
            grievanceDetailsPage
              .getLabelIssueType()
              .contains(newTicket.issueType);
            grievanceDetailsPage.getLabelTickets().contains(newTicket.lookUp);
            grievanceDetailsPage
              .getTicketCategoryBy()
              .contains(newTicket.createdBy);
            grievanceDetailsPage
              .getCheckbox()
              .contains(
                newTicket.householdDataField.split("s")[0].toLowerCase()
              );
          });
        }
      );
      ["Individual Data Update"].forEach((testData) => {
        it(`Create New Ticket - Data Change - ${testData}`, function () {
          let newTicket = this.newTicket[testData];
          newTicketPage.chooseCategory(newTicket.category);
          newTicketPage.chooseIssueType(newTicket.issueType);
          newTicketPage
            .getLabelCategoryDescription()
            .contains(
              newTicketPage.textCategoryDescription[newTicket.category]
            );
          newTicketPage
            .getLabelIssueTypeDescription()
            .contains(
              newTicketPage.textIssueTypeDescription[newTicket.issueType]
            );
          newTicketPage.getButtonNext().click();
          newTicketPage.getHouseholdTab().should("be.visible");
          newTicketPage.getHouseholdTableRows(0).click();
          newTicketPage.getIndividualTab().click();
          newTicketPage.getIndividualTableRows(0).click();
          newTicketPage.getButtonNext().click();
          newTicketPage.getReceivedConsent().click();
          newTicketPage.getButtonNext().click();
          newTicketPage.getDescription().type(newTicket.description);
          newTicketPage.getComments().type(newTicket.comment);
          newTicketPage.getAdminAreaAutocomplete().click();
          newTicketPage.getOption().contains(newTicket.adminArea).click();
          newTicketPage.getInputArea().type(newTicket.inputArea);
          newTicketPage.getInputLanguage().type(newTicket.inputLanguage);
          newTicketPage.getSelectPriority().click();
          newTicketPage.getOption().contains(newTicket.priority).click();
          newTicketPage.getSelectUrgency().click();
          newTicketPage.getOption().contains(newTicket.urgency).click();
          newTicketPage.getLookUpButton().click();
          newTicketPage.getCheckbox().eq(0).contains(newTicket.lookUp);
          newTicketPage.getCheckbox().eq(0).click();
          newTicketPage.getButtonNext().eq(1).click();
          newTicketPage.getIndividualFieldName().click();
          newTicketPage.selectOption(newTicket.individualDataField).click();
          newTicketPage
            .getInputIndividualData(newTicket.individualDataField)
            .type(newTicket.newData);
          newTicketPage.getButtonNext().contains("Save").click();

          grievanceDetailsPage.checkElementsOnPage(
            grievanceDetailsPage.textStatusAssigned,
            newTicket.priority,
            newTicket.urgency,
            grievanceDetailsPage.textNotAssigment,
            newTicket.category
          );
          grievanceDetailsPage
            .getTicketIndividualID()
            .contains(newTicket.individualID);
          grievanceDetailsPage
            .getAdministrativeLevel()
            .contains(newTicket.adminArea);
          grievanceDetailsPage
            .getLanguagesSpoken()
            .contains(newTicket.inputLanguage);
          grievanceDetailsPage.getAreaVillage().contains(newTicket.inputArea);
          grievanceDetailsPage
            .getLabelIssueType()
            .contains(newTicket.issueType);
          grievanceDetailsPage.getLabelTickets().contains(newTicket.lookUp);
          grievanceDetailsPage
            .getTicketCategoryBy()
            .contains(newTicket.createdBy);
          grievanceDetailsPage
            .getCheckbox()
            .contains(newTicket.individualDataField.toLowerCase());
          grievanceDetailsPage.getCheckbox().contains(newTicket.currentData);
          grievanceDetailsPage.getCheckbox().contains(newTicket.newData);
        });
      });
      ["Withdraw Individual"].forEach((testData) => {
        it(`Create New Ticket - Data Change - ${testData}`, function () {
          let newTicket = this.newTicket[testData];
          newTicketPage.chooseCategory(newTicket.category);
          newTicketPage.chooseIssueType(newTicket.issueType);
          newTicketPage
            .getLabelCategoryDescription()
            .contains(
              newTicketPage.textCategoryDescription[newTicket.category]
            );
          newTicketPage
            .getLabelIssueTypeDescription()
            .contains(
              newTicketPage.textIssueTypeDescription[newTicket.issueType]
            );
          newTicketPage.getButtonNext().click();
          newTicketPage.getHouseholdTab().should("be.visible");
          newTicketPage.getHouseholdTableRows(0).click();
          newTicketPage.getIndividualTab().click();
          newTicketPage.getIndividualTableRows(0).click();
          newTicketPage.getButtonNext().click();
          newTicketPage.getReceivedConsent().click();
          newTicketPage.getButtonNext().click();
          newTicketPage.getDescription().type(newTicket.description);
          newTicketPage.getComments().type(newTicket.comment);
          newTicketPage.getAdminAreaAutocomplete().click();
          newTicketPage.getOption().contains(newTicket.adminArea).click();
          newTicketPage.getInputArea().type(newTicket.inputArea);
          newTicketPage.getInputLanguage().type(newTicket.inputLanguage);
          newTicketPage.getSelectPriority().click();
          newTicketPage.getOption().contains(newTicket.priority).click();
          newTicketPage.getSelectUrgency().click();
          newTicketPage.getOption().contains(newTicket.urgency).click();
          newTicketPage.getLookUpButton().click();
          newTicketPage.getCheckbox().eq(0).contains(newTicket.lookUp);
          newTicketPage.getCheckbox().eq(0).click();
          newTicketPage.getButtonNext().eq(1).click();
          newTicketPage.getButtonNext().contains("Save").click();

          grievanceDetailsPage.checkElementsOnPage(
            grievanceDetailsPage.textStatusAssigned,
            newTicket.priority,
            newTicket.urgency,
            grievanceDetailsPage.textNotAssigment,
            newTicket.category
          );
          grievanceDetailsPage
            .getTicketIndividualID()
            .contains(newTicket.individualID);
          grievanceDetailsPage
            .getAdministrativeLevel()
            .contains(newTicket.adminArea);
          grievanceDetailsPage
            .getLanguagesSpoken()
            .contains(newTicket.inputLanguage);
          grievanceDetailsPage.getAreaVillage().contains(newTicket.inputArea);
          grievanceDetailsPage
            .getLabelIssueType()
            .contains(newTicket.issueType);
          grievanceDetailsPage.getLabelTickets().contains(newTicket.lookUp);
          grievanceDetailsPage
            .getTicketCategoryBy()
            .contains(newTicket.createdBy);
          grievanceDetailsPage
            .getLabelFullName()
            .contains(newTicket.familyName);
        });
      });

      ["Withdraw Household"].forEach((testData) => {
        it(`Create New Ticket - Data Change - ${testData}`, function () {
          let newTicket = this.newTicket[testData];
          newTicketPage.chooseCategory(newTicket.category);
          newTicketPage.chooseIssueType(newTicket.issueType);
          newTicketPage
            .getLabelCategoryDescription()
            .contains(
              newTicketPage.textCategoryDescription[newTicket.category]
            );
          newTicketPage
            .getLabelIssueTypeDescription()
            .contains(
              newTicketPage.textIssueTypeDescription[newTicket.issueType]
            );
          newTicketPage.getButtonNext().click();
          newTicketPage.getHouseholdTab().should("be.visible");
          newTicketPage.getHouseholdTableRows(0).click();
          newTicketPage.getIndividualTab().parent().should("be.disabled");
          newTicketPage.getButtonNext().click();
          newTicketPage.getReceivedConsent().click();
          newTicketPage.getButtonNext().click();
          newTicketPage.getDescription().type(newTicket.description);
          if (newTicket.comment)
            newTicketPage.getComments().type(newTicket.comment);
          newTicketPage.getAdminAreaAutocomplete().click();
          newTicketPage.getOption().contains(newTicket.adminArea).click();
          newTicketPage.getInputArea().type(newTicket.inputArea);
          newTicketPage.getInputLanguage().type(newTicket.inputLanguage);
          newTicketPage.getSelectPriority().click();
          newTicketPage.getOption().contains(newTicket.priority).click();
          newTicketPage.getSelectUrgency().click();
          newTicketPage.getOption().contains(newTicket.urgency).click();
          newTicketPage.getLookUpButton().click();
          newTicketPage.getCheckbox().eq(0).contains(newTicket.lookUp);
          newTicketPage.getCheckbox().eq(0).click();
          newTicketPage.getButtonNext().eq(1).click();
          newTicketPage.getButtonNext().contains("Save").click();

          grievanceDetailsPage.checkElementsOnPage(
            grievanceDetailsPage.textStatusAssigned,
            newTicket.priority,
            newTicket.urgency,
            grievanceDetailsPage.textNotAssigment,
            newTicket.category
          );
          grievanceDetailsPage
            .getTicketIndividualID()
            .contains(newTicket.individualID);
          grievanceDetailsPage
            .getAdministrativeLevel()
            .contains(newTicket.adminArea);
          grievanceDetailsPage
            .getLanguagesSpoken()
            .contains(newTicket.inputLanguage);
          grievanceDetailsPage.getAreaVillage().contains(newTicket.inputArea);
          grievanceDetailsPage
            .getLabelIssueType()
            .contains(newTicket.issueType);
          grievanceDetailsPage.getLabelTickets().contains(newTicket.lookUp);
          grievanceDetailsPage
            .getTicketCategoryBy()
            .contains(newTicket.createdBy);
        });
      });
      [
        "Payment Related Complaint",
        "FSP Related Complaint",
        "Registration Related Complaint",
        "Other Complaint",
        "Partner Related Complaint",
      ].forEach((testData) => {
        it.only(`Create New Ticket - Grievance Complaint - ${testData}`, function () {
          let newTicket = this.newTicket[testData];
          newTicketPage.chooseCategory(newTicket.category);
          newTicketPage.chooseIssueType(newTicket.issueType);
          newTicketPage
            .getLabelCategoryDescription()
            .contains(
              newTicketPage.textCategoryDescription[newTicket.category]
            );
          newTicketPage
            .getLabelIssueTypeDescription()
            .contains(
              newTicketPage.textIssueTypeDescription[newTicket.issueType]
            );
          newTicketPage.getButtonNext().click();
          newTicketPage.getHouseholdTab().should("be.visible");

          if (newTicket.householdID !== "-")
            newTicketPage.getHouseholdTableRows(1).click();
          if (newTicket.individualID !== "-") {
            newTicketPage.getIndividualTab().click();
            newTicketPage.getIndividualTableRows(2).click();
          }
          newTicketPage.getButtonNext().click();
          newTicketPage.getReceivedConsent().click();
          newTicketPage.getButtonNext().click();

          newTicketPage.getDescription().type(newTicket.description);
          if (newTicket.comment)
            newTicketPage.getComments().type(newTicket.comment);
          newTicketPage.getAdminAreaAutocomplete().click();
          newTicketPage.getOption().contains(newTicket.adminArea).click();
          newTicketPage.getInputArea().type(newTicket.inputArea);
          newTicketPage.getInputLanguage().type(newTicket.inputLanguage);
          newTicketPage.getSelectPriority().click();
          newTicketPage.getOption().contains(newTicket.priority).click();
          newTicketPage.getSelectUrgency().click();
          newTicketPage.getOption().contains(newTicket.urgency).click();
          newTicketPage
            .getLookUpButton()
            .contains("Look up Payment Record")
            .click();
          newTicketPage.getCheckbox().eq(0).contains(newTicket.lookUp);
          newTicketPage.getCheckbox().eq(0).click();
          newTicketPage.getButtonNext().eq(1).click();
        });
      });
      it.skip("Create New Ticket - Negative Feedback", () => {});
      it.skip("Create New Ticket - Positive Feedback", () => {});
      it.skip("Create New Ticket - Referral", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Bribery, corruption or kickback", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Data breach", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Conflict of interest", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Fraud and forgery", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Fraud involving misuse of programme funds by third party", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Gross mismanagement", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Harassment and abuse of authority", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Inappropriate staff conduct", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Miscellaneous", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Personal disputes", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Sexual harassment and sexual exploitation", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Unauthorized use, misuse or waste of UNICEF property or funds", () => {});

      it.skip("Create New Ticket - Cancel", () => {});
    });

    context("Edit Ticket", () => {
      it.skip("Edit Ticket", () => {});
    });

    context("Assign Ticket", () => {
      it.skip("Assign to me", () => {});
      it.skip("Set to in progress", () => {});
      it.skip("Send for approval", () => {});
      it.skip("Send back", () => {});
      it.skip("Close ticket", () => {});
      it.skip("Add new note", () => {});
      it.skip("Create Linked Ticket from details page", () => {});
      it.skip("Mark duplicate from details page", () => {});
    });
  });
  describe.skip("E2E tests Grievance", () => {});

  describe("Regression tests Grievance", () => {
    // ToDo: Enable
    xit('164824 GM: Cannot select a row except texts from "Ticket ID" column.', () => {
      grievancePage.chooseTicketListRow(0).click();
      cy.url().should("include", "/system-generated");
    });
  });
});
