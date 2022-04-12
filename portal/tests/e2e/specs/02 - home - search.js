describe("Home page - search", () => {
  beforeEach(function () {
    cy.visit("/");
  });

  it("Should find materials by search term", () => {
    cy.searchFor("Wiskunde");
    cy.searchResultsShouldContain("wiskunde");
  });

  it("Should give search term suggestions and use the search suggestion as search term when clicked", () => {
    cy.get("[data-test=search_term]")
      .type("muscul")
      .get("[role=listbox]")
      .should("be.visible")
      .children()
      .should("have.length", 6)
      .eq(2)
      .should("contain", "muscularis")
      .click(50, 25, { force: true })
      .searchResultsShouldContain("muscularis", 10, 1);
  });

  it("Should find materials by author", () => {
    cy.searchFor("A Borst");
    cy.searchResultsShouldContain("A. Borst");
  });

  it("Should show search suggestion when a search suggestion is available", () => {
    cy.searchFor("soocial");
    cy.get("[data-test=search_suggestion]")
      .should("be.visible")
      .should(
        "contain",
        "Bedoelde je social ? Want er zijn geen resultaten voor 'soocial'"
      );
  });

  it("Should search with search suggestion when the search suggestion is clicked", () => {
    cy.searchFor("soocial");
    cy.get("[data-test=search_suggestion_link]").should("be.visible").click();
    cy.searchResultsShouldContain("Social");
  });

  it("Should show 'no search result' message when no search suggestion is available", () => {
    cy.searchFor("xyzyz");
    cy.get("[data-test=no_search_results]")
      .should("be.visible")
      .should("contain", "Er zijn geen resultaten voor 'xyzyz'");
  });
});
