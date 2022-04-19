describe("Material page - search", () => {
  beforeEach(function () {
    cy.visit("/materialen/f929b625-5ef7-47b8-8fa8-94c969d0c427");
  });

  it("Should find materials by author when clicking the author on the material page", () => {
    cy.get("[data-test=author_link]").click();
    cy.searchResultsShouldContain("Esther Quaedackers", 5);
    cy.selectedFiltersShouldContain("Auteur", "Esther Quaedackers");
  });

  it("Should find materials by publisher when clicking the publisher on the material page", () => {
    cy.get("[data-test=publisher_link]").click();
    cy.searchResultsShouldContain("SURFnet", 9);
    cy.selectedFiltersShouldContain("Uitgever", "SURFnet");
  });

  // TODO add test data with consortium
  it.skip("Should find materials by consortium when clicking the consortium on the material page", () => {
    cy.get("[data-test=consortium_link]").click();
    cy.searchResultsShouldContain("Verpleging en verzorging", 10, 1);
    cy.selectedFiltersShouldContain(
      "Samenwerkingsverband",
      "HBO Verpleegkunde"
    );
  });
});
