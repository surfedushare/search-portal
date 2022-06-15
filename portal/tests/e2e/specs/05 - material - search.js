describe("Material page - search", { defaultCommandTimeout: 5000 }, () => {
  beforeEach(function () {
    cy.visit("/materialen/f929b625-5ef7-47b8-8fa8-94c969d0c427");
  });

  it("Should find materials by author when clicking the author on the material page", () => {
    cy.get("[data-test=author_link]")
      .click()
      .searchResultsShouldContain("Esther Quaedackers", 6)
      .selectedFiltersShouldContain("Auteur", "Esther Quaedackers");
  });

  it("Should find materials by publisher when clicking the publisher on the material page", () => {
    cy.get("[data-test=publisher_link]")
      .click()
      .selectedFiltersShouldContain("Uitgever", "SURFnet");
  });

  it("Should find materials by consortium when clicking the consortium on the material page", () => {
    cy.get("[data-test=consortium_link]")
      .click()
      .searchResultsShouldContain("03. What are little big histories", 2, 0)
      .selectedFiltersShouldContain("Samenwerkingsverband", "Community Ethics");
  });
});
