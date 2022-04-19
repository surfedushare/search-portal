describe("Home page - search - filters", () => {
  beforeEach(function () {
    cy.visit("/").search();
  });

  it("Should filter on technical type", () => {
    cy.selectFilter("technical_type", "document").selectedFiltersShouldContain(
      "Bestandstype",
      "Document",
      1,
      0
    );
  });

  it("Should filter on aggregation level", () => {
    cy.selectFilter("aggregation_level", "3").selectedFiltersShouldContain(
      "Bruikbaar als",
      "Les",
      1,
      0
    );
    cy.selectFilter("aggregation_level", "2").selectedFiltersShouldContain(
      "Bruikbaar als",
      "Leerobject",
      2,
      1
    );
  });

  it("Should filter on material type", () => {
    cy.selectFilter("material_types", "unknown").selectedFiltersShouldContain(
      "Soort materiaal",
      "onbekend",
      1,
      0
    );
    cy.selectFilter(
      "material_types",
      "kennisoverdracht"
    ).selectedFiltersShouldContain("Soort materiaal", "kennisoverdracht", 2, 1);
  });

  it("Should filter on publisher", () => {
    cy.selectFilter(
      "publishers.keyword",
      "SURFnet"
    ).selectedFiltersShouldContain("Uitgever", "SURFnet", 1, 0);
    cy.selectFilter(
      "publishers.keyword",
      "Stimuleringsregeling Open en Online Onderwijs"
    ).selectedFiltersShouldContain(
      "Uitgever",
      "Stimuleringsregeling Open en Online Onderwijs",
      2,
      1
    );
  });

  // TODO add test data
  it.skip("Should filter on consortium", () => {
    cy.selectFilter(
      "consortium",
      "HBO Verpleegkunde"
    ).selectedFiltersShouldContain(
      "Samenwerkingsverband",
      "HBO Verpleegkunde",
      1,
      0
    );
    cy.selectFilter(
      "consortium",
      "Community Ethics"
    ).selectedFiltersShouldContain(
      "Samenwerkingsverband",
      "Community Ethics",
      2,
      1
    );
  });

  it("Should filter on educational level", () => {
    cy.selectFilter(
      "lom_educational_levels",
      "HBO"
    ).selectedFiltersShouldContain("Onderwijsniveau", "HBO", 1, 0);
    cy.selectFilter(
      "lom_educational_levels",
      "WO"
    ).selectedFiltersShouldContain("Onderwijsniveau", "WO", 2, 1);
  });

  it("Should filter on copyright", () => {
    cy.selectFilter(
      "copyright.keyword",
      "cc-by-sa"
    ).selectedFiltersShouldContain(
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
    cy.selectFilter("language.keyword", "nl").selectedFiltersShouldContain(
      "Taal",
      "Nederlands",
      1,
      0
    );
    cy.selectFilter("language.keyword", "en").selectedFiltersShouldContain(
      "Taal",
      "Engels",
      2,
      1
    );
  });

  // TODO add test data with dicipline
  it.skip("Should filter on disciplines", () => {
    cy.selectFilter(
      "disciplines",
      "b333369b-e647-4bbf-b04c-d11a9235a113"
    ).selectedFiltersShouldContain(
      "Vakgebied",
      "Verpleging en verzorging",
      1,
      0
    );
    cy.selectFilter(
      "disciplines",
      "743e38e7-d3bc-40e5-9f5d-5d7941af659e"
    ).selectedFiltersShouldContain("Vakgebied", "Zorgverlener", 2, 1);
  });

  it("Should filter on author", () => {
    cy.selectFilter(
      "authors.name.keyword",
      "Esther Quaedackers"
    ).selectedFiltersShouldContain("Auteur", "Esther Quaedackers", 1, 0);
    cy.selectFilter(
      "authors.name.keyword",
      "Fred Spier"
    ).selectedFiltersShouldContain("Auteur", "Fred Spier", 2, 1);
  });

  // TODO add test data with theme
  it.skip("Should filter on theme", () => {
    cy.selectFilter(
      "learning_material_themes_normalized",
      "gezondheid"
    ).selectedFiltersShouldContain("Thema", "Gezondheid", 1, 0);
    cy.selectFilter(
      "learning_material_themes_normalized",
      "aarde_milieu"
    ).selectedFiltersShouldContain("Thema", "Aarde en Milieu", 2, 1);
  });

  // TODO add test data with theme
  it.skip("Should filter on multiple filter categories", () => {
    cy.selectFilter("learning_material_themes_normalized", "aarde_milieu")
      .selectFilter("authors.name.keyword", "Fred Spier")
      .selectFilter("lom_educational_levels", "WO")
      .selectedFiltersShouldContain("Thema", "Aarde en Milieu", 3, 0)
      .selectedFiltersShouldContain("Auteur", "Fred Spier", 3, 1)
      .selectedFiltersShouldContain("Onderwijsniveau", "WO", 3, 2);
  });
});
