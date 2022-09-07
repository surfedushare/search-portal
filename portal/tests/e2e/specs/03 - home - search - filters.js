describe("Home page - search - filters", () => {
  beforeEach(function () {
    cy.visit("/").search();
  });

  it("Should filter on technical type", () => {
    cy.selectFilter("technical_type", "document").selectedFiltersShouldContain("Bestandstype", "Document", 1, 0);
  });

  it("Should filter on aggregation level", () => {
    cy.selectFilter("aggregation_level", "3").selectedFiltersShouldContain("Bruikbaar als", "Les", 1, 0);
    cy.selectFilter("aggregation_level", "2").selectedFiltersShouldContain("Bruikbaar als", "Leerobject", 2, 1);
  });

  it("Should filter on material type", () => {
    cy.selectFilter("material_types", "unknown").selectedFiltersShouldContain("Soort materiaal", "onbekend", 1, 0);
    cy.selectFilter("material_types", "kennisoverdracht").selectedFiltersShouldContain(
      "Soort materiaal",
      "kennisoverdracht",
      2,
      1
    );
  });

  it("Should filter on publisher", () => {
    cy.selectFilter("publishers.keyword", "SURFnet").selectedFiltersShouldContain("Uitgever", "SURFnet", 1, 0);
    cy.selectFilter("publishers.keyword", "Stimuleringsregeling Open en Online Onderwijs").selectedFiltersShouldContain(
      "Uitgever",
      "Stimuleringsregeling Open en Online Onderwijs",
      2,
      1
    );
  });

  it("Should filter on consortium", () => {
    cy.selectFilter("consortium", "Community Ethics").selectedFiltersShouldContain(
      "Samenwerkingsverband",
      "Community Ethics",
      1,
      0
    );
  });

  it("Should filter on educational level", () => {
    cy.selectFilter("lom_educational_levels", "HBO").selectedFiltersShouldContain("Onderwijsniveau", "HBO", 1, 0);
    cy.selectFilter("lom_educational_levels", "WO").selectedFiltersShouldContain("Onderwijsniveau", "WO", 2, 1);
  });

  it("Should filter on copyright", () => {
    cy.selectFilter("copyright.keyword", "cc-by-sa").selectedFiltersShouldContain(
      "Gebruiksrechten",
      "Naamsvermelding-GelijkDelen",
      1,
      0
    );
    cy.selectFilter("copyright.keyword", "cc-by").selectedFiltersShouldContain(
      "Gebruiksrechten",
      "Naamsvermelding",
      2,
      1
    );
  });

  it("Should filter on language", () => {
    cy.selectFilter("language.keyword", "nl").selectedFiltersShouldContain("Taal", "Nederlands", 1, 0);
  });

  it("Should filter on disciplines", () => {
    cy.selectFilter("disciplines", "0861c43d-1874-4788-b522-df8be575677f").selectedFiltersShouldContain(
      "Vakgebied",
      "Onderwijskunde",
      1,
      0
    );
  });

  it("Should filter on author", () => {
    cy.selectFilter("authors.name.keyword", "Esther Quaedackers").selectedFiltersShouldContain(
      "Auteur",
      "Esther Quaedackers",
      1,
      0
    );
    cy.selectFilter("authors.name.keyword", "Fred Spier").selectedFiltersShouldContain("Auteur", "Fred Spier", 2, 1);
  });

  it("Should filter on disciplines", () => {
    cy.selectFilter("learning_material_disciplines_normalized", "gedrag_maatschappij").selectedFiltersShouldContain(
      "Vakgebied",
      "Gedrag en Maatschappij",
      1,
      0
    );
  });

  it("Should filter on multiple filter categories", () => {
    cy.selectFilter("learning_material_disciplines_normalized", "gedrag_maatschappij")
      .selectFilter("authors.name.keyword", "Ning Ding")
      .selectFilter("lom_educational_levels", "HBO")
      .selectedFiltersShouldContain("Vakgebied", "Gedrag en Maatschappij", 3, 0)
      .selectedFiltersShouldContain("Auteur", "Ning Ding", 3, 1)
      .selectedFiltersShouldContain("Onderwijsniveau", "HBO", 3, 2);
  });

  it("Should retain filters when searching again", () => {
    cy.selectFilter("technical_type", "document").selectedFiltersShouldContain("Bestandstype", "Document", 1, 0);
    cy.searchFor("big").selectedFiltersShouldContain("Bestandstype", "Document", 1, 0);
  });
});
