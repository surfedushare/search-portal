describe("Material page - search", () => {
  beforeEach(function () {
    cy.visit("/materialen/edurep_delen:36824284-b208-4712-b309-644d628f18eb");
  });

  it("Should find materials by author when clicking the author on the material page", () => {
    cy.get("[data-test=author_link]").click();
    cy.searchResultsShouldContain("A. Borst", 9);
    cy.selectedFiltersShouldContain("Auteur", "A. Borst");
  });

  it("Should find materials by publisher when clicking the publisher on the material page", () => {
    cy.get("[data-test=publisher_link]").click();
    cy.searchResultsShouldContain("Edurep Delen", 10);
    cy.selectedFiltersShouldContain("Uitgever", "Edurep Delen");
  });

  it("Should find materials by consortium when clicking the consortium on the material page", () => {
    cy.get("[data-test=consortium_link]").click();
    cy.searchResultsShouldContain("Verpleging en verzorging", 10, 1);
    cy.selectedFiltersShouldContain(
      "Samenwerkingsverband",
      "HBO Verpleegkunde"
    );
  });
});
