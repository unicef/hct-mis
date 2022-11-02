Feature: Create Payment Plan
        Checks the whole payment plan flow

        Background:
                Given I am authenticated
                Given I initialize the data
                Given Business area is payment plan applicable

        Scenario: Create Payment Plan
                When I visit the main dashboard
                Then I should see the side panel with Payment Module option
                When I click on Payment Module option
                Then I should see the Payment Module page

                When I click the New Payment Plan button
                Then I should see the New Payment Plan page
                When I fill out the form fields and save
                Then I should see the Payment Plan details page

                When I lock the Payment Plan
                Then I see the entitlements input
                And I see that all individuals have proper payment channels

                When I choose the steficon rule
                And I apply the steficon rule
                Then I see the entitlements calculated

                When I download the xlsx template
                Then I fill the xlsx template
                When I upload the xlsx template
                Then I see the entitlements calculated

                When I click Set up FSP button
                Then I should see the Set up FSP page
                When I select the delivery mechanisms
                Then I should be able to assign FSPs
                When I select the FSPs and save
                Then I should see volumes by delivery mechanisms
                When I lock the FSPs
                Then I should see that the status is FSP Locked

                When I send the Payment Plan for approval
                Then I see the acceptance process stepper
                When I approve the Payment Plan
                Then I see the Payment Plan as in authorization
                When I authorize the Payment Plan
                Then I see the Payment Plan as in review
                When I finalize the Payment Plan
                Then I see the Payment Plan as accepted

                And I export xlsx to zip file
                When I unarchive the zip file
                Then I see the 1 xlsx files
                When I fill the reconciliation info
                And I upload the reconciliation info
                Then I see the delivered quantities for each payment
