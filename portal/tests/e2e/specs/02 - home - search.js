describe("Home page - search", () => {
  beforeEach(function () {
    cy.visit("/");
  });

  it("Should find materials by search term", () => {
    cy.searchFor("How");
    cy.searchResultsShouldContain("how", 7);
  });

  it("Should give search term suggestions and use the search suggestion as search term when clicked", () => {
    cy.get("[data-test=search_term]")
      .type("lea")
      .get("[role=listbox]")
      .should("be.visible")
      .children()
      .should("have.length", 2)
      .eq(1)
      .should("contain", "learn")
      .click(50, 25, { force: true })
      .searchResultsShouldContain("Learn", 2, 0);
  });

  it("Should find materials by author", () => {
    cy.searchFor("esther");
    cy.searchResultsShouldContain("Esther Quaedackers", 5, 1);
  });

  it("Should show search suggestion when a search suggestion is available", () => {
    cy.searchFor("thee");
    cy.get("[data-test=search_suggestion]")
      .should("be.visible")
      .should(
        "contain",
        "Bedoelde je these ? Want er zijn geen resultaten voor 'thee'"
      );
  });

  it("Should search with search suggestion when the search suggestion is clicked", () => {
    cy.searchFor("thee");
    cy.get("[data-test=search_suggestion_link]").should("be.visible").click();
    cy.searchResultsShouldContain("these", 3, 1);
  });

  it("Should show 'no search result' message when no search suggestion is available", () => {
    cy.searchFor("xyzyz");
    cy.get("[data-test=no_search_results]")
      .should("be.visible")
      .should("contain", "Er zijn geen resultaten voor 'xyzyz'");
  });
});
