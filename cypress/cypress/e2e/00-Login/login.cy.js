import Login from "../../page-objects/pages/login/login.po";

let l = new Login();
describe(
  "Login",
  {
    retries: {
      runMode: 3,
      openMode: 1,
    },
  },
  () => {
    after(() => {
      cy.adminLogin();
    });
    it("login with valid username and valid password", () => {
      cy.adminLogin();
      cy.navigateToHomePage();
      cy.get("h5").should("contain", "Dashboard");
    });
    it("Check the login with valid username and Invalid password", () => {
      Cypress.session.clearCurrentSessionData();
      cy.navigateToHomePage();
      l.navigateToLoginPage();
      cy.get('input[name="username"]').type(Cypress.env("username"));
      cy.get('input[name="password"]').type("wrong-password");
      cy.get("input").contains("Log in").click();
      cy.get(".errornote").should(
        "contain",
        "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
      );
    });
    it("Check the login with Invalid username and valid password", () => {
      Cypress.session.clearCurrentSessionData();
      l.navigateToLoginPage();
      cy.get('input[name="username"]').type("wrong-username");
      cy.get('input[name="password"]').type(Cypress.env("password"));
      cy.get("input").contains("Log in").click();
      cy.get(".errornote").should(
        "contain",
        "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
      );
    });
    it("Check the login with Invalid username and Invalid password", () => {
      Cypress.session.clearCurrentSessionData();
      l.navigateToLoginPage();
      cy.get('input[name="username"]').type("wrong-username");
      cy.get('input[name="password"]').type("wrong-password");
      cy.get("input").contains("Log in").click();
      cy.get(".errornote").should(
        "contain",
        "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
      );
    });
  }
);
