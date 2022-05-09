describe("Home page - search - pre-filters", () => {
  beforeEach(function () {
    cy.visit("/");
  });

  it("Should pre-filter on technical type", () => {
    cy.selectPreFilter("technical_type", "document")
      .search()
      .selectedFiltersShouldContain("Bestandstype", "Document", 1, 0);
    cy.selectPreFilter("technical_type", "website")
      .search()
      .selectedFiltersShouldContain("Bestandstype", "Website", 2, 1);
  });

  it("Should pre-filter on theme", () => {
    cy.selectPreFilter(
      "learning_material_themes_normalized",
      "gedrag_maatschappij"
    )
      .search()
      .selectedFiltersShouldContain("Thema", "Gedrag en Maatschappij", 1, 0);
  });

  it("Should pre-filter on educational level", () => {
    cy.selectPreFilter("lom_educational_levels", "HBO")
      .search()
      .selectedFiltersShouldContain("Onderwijsniveau", "HBO", 1, 0);
    cy.selectPreFilter("lom_educational_levels", "WO")
      .search()
      .selectedFiltersShouldContain("Onderwijsniveau", "WO", 2, 1);
  });

  it("Should pre-filter on language", () => {
    cy.selectPreFilter("language.keyword", "nl")
      .search()
      .selectedFiltersShouldContain("Taal", "Nederlands", 1, 0);
    cy.selectPreFilter("language.keyword", "en")
      .search()
      .selectedFiltersShouldContain("Taal", "Engels", 2, 0);
  });
});
