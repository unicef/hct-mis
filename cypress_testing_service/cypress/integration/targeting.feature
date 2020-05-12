@Targeting
Feature: Target Population

  Background:
    # Given I login to AD as country_admin
    Given I login with mocked cookies
    Then I see user profile menu


  # Create New Programme Population
  # As a User
  # I want to create a new Programme Population based on Targeting Criteria
  # So I can create useful Cash Plans

  # Scenario: Target Beneficiaries from the 'HCT MIS DB'
  #   Given the User is viewing the Targeting List screen
  #   When the User starts creating new Target Population
  #     And the User gives new Target Population a name
  #     And the User selects at least one Target Criteria
  #     And the User completes creating new Target Population

  #   Then the User will be directed to the Programme Population details screen
  #     And the Status of the Programme Population will be set to Open

  # Close Programme Population
  # As a User
  # I want to lock in the Beneficiary Data selected from my criteria set
  # So I can use it in CashAssist

  Scenario: Preparing potential list of beneficiaries to be added to a Cash Plan of a particular Program
    Given the User is viewing existing Programme Population in Open state
    When the User closes the Programme Population
    Then the confirmation dialog for closing Programme Population is shown
      And the User is asked to provide associated Program

    When the User selects a Programme to associate with
      And the User confirms to close the Programme Population

    Then the Programme population becomes Closed
      And the User can no longer edit the Programme Population
      And the Programme Population details are locked

# Send Target Population to CashAssist
# As a User
# I want to send the final Target Populationt to CashAssist
# So that it can be used for Programme Cash Plans

# Scenario: Finalizing list of Targeted Beneficiaries to send to CashAssist
#   Given the User is viewing existing Target Population in Closed state
#   When the User sends the Target Population to Cash Assist
#   Then the confirmation dialog for Send to Cash Assist is shown

#   When the User confirms sending to Cash Assist
#   Then the details for the Target Population are sent to Cash Assist

# @Targeting
# Feature: Duplicate Programme Population

#     As a User I want to Duplicate the Target Criteria of a particular Programme Population

#     Scenario: Refresh Eligible Beneficiaries with Current Population in the 'HCT MIS DB'
#         Given The User is viewing the details of a 'Open' 'Closed' or 'Sent' Programme Population
#         When The User clicks the duplicate symbol located at the top-right of body
#         Then A Confirmation Modal screen will display

#         Given The Confirmation Modal is present
#         When The User completes all the required form fields
#         And The User clicks the 'Save' Button
#         Then The Confirmation Modal dissapears
#         And A new Create New Programme Population is started with the Title prefilled
#         And The User is directed to the new Create New Programme Population screen
