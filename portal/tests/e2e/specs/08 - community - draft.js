describe("Community page - draft", () => {

  it("Should display community information in the header and description in the content for user", () => {

    cy.setLocalStorage("surf_token", "123abc");
    cy.visit("/communities/e7cdbb19-89fa-4a80-af69-101c8b9cf3df");

    cy.get("[data-test=header]").contains("Leven lang ontwikkelen").should("be.visible");
    cy.get("[data-test=header]").contains("in ontwikkeling")
      .should("be.visible");
    cy.get("[data-test=header]").contains("Over deze community")
      .should("be.visible")
      .should("have.class","v-tab--active");
    cy.get("[data-test=header] .community-logo").should("be.visible");
    cy.get("[data-test=header] .v-tab").should("have.length", 1);
    cy.get("[data-test=content]").get(".community-description").should("be.visible");
    cy.get("[data-test=content] .community-info").should("not.have.descendants")

  });

  it("Should display not found page for anonymous user", () => {
    cy.visit("/communities/e7cdbb19-89fa-4a80-af69-101c8b9cf3df");
    cy.contains("Community niet gevonden").should("be.visible");
  });

});
