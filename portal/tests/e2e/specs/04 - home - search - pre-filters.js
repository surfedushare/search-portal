describe("Home page - search - pre-filters", () => {
  beforeEach(function () {
    cy.visit("/");
  });

  it("Should pre-filter on technical type", () => {
    cy.selectPreFilter("technical_type", "document")
      .search()
      .selectedFiltersShouldContain("Bestandstype", "Document", 1, 0);
    cy.selectFilter("technical_type", "website").search().selectedFiltersShouldContain("Bestandstype", "Website", 2, 1);
  });

  it("Should pre-filter on discipline", () => {
    cy.selectPreFilter("learning_material_disciplines_normalized", "gedrag_maatschappij")
      .search()
      .selectedFiltersShouldContain("Vakgebied", "Gedrag en Maatschappij", 1, 0);
  });

  it("Should pre-filter on educational level", () => {
    cy.selectPreFilter("lom_educational_levels", "HBO")
      .search()
      .selectedFiltersShouldContain("Onderwijsniveau", "HBO", 1, 0);
    cy.selectFilter("lom_educational_levels", "WO")
      .search()
      .selectedFiltersShouldContain("Onderwijsniveau", "WO", 2, 1);
  });

  it("Should clear all filters when resetting filters", () => {
    cy.selectPreFilter("technical_type", "website")
      .search()
      .selectedFiltersShouldContain("Bestandstype", "Website", 0, 0);
    cy.get("[data-test=reset_filters").click().get("[data-test=selected_filters]").should("not.be.visible");
  });

  it("Should clear all filters when navigating away", () => {
    cy.selectPreFilter("technical_type", "website")
      .search()
      .selectedFiltersShouldContain("Bestandstype", "Website", 0, 0);
    cy.visit("/").search().get("[data-test=selected_filters]").should("not.be.visible");
  });

  it("Should pre-filter on language", () => {
    cy.selectPreFilter("language.keyword", "nl").search().selectedFiltersShouldContain("Taal", "Nederlands", 1, 0);
  });

});
