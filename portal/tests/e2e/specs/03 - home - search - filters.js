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
    cy.selectFilter("aggregation_level", "1").selectedFiltersShouldContain(
      "Bruikbaar als",
      "Fragment",
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
    cy.selectFilter("material_types", "opdracht").selectedFiltersShouldContain(
      "Soort materiaal",
      "opdracht",
      1,
      0
    );
    cy.selectFilter(
      "material_types",
      "informatiebron"
    ).selectedFiltersShouldContain("Soort materiaal", "informatiebron", 2, 1);
  });

  it("Should filter on publisher", () => {
    cy.selectFilter(
      "publishers.keyword",
      "Edurep Delen"
    ).selectedFiltersShouldContain("Uitgever", "Edurep Delen", 1, 0);
    cy.selectFilter(
      "publishers.keyword",
      "SURFnet"
    ).selectedFiltersShouldContain("Uitgever", "SURFnet", 2, 1);
  });

  it("Should filter on consortium", () => {
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

  it("Should filter on disciplines", () => {
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
      "OpenStax"
    ).selectedFiltersShouldContain("Auteur", "OpenStax", 1, 0);
    cy.selectFilter(
      "authors.name.keyword",
      "Ron Slagter"
    ).selectedFiltersShouldContain("Auteur", "Ron Slagter", 2, 1);
  });

  it("Should filter on theme", () => {
    cy.selectFilter(
      "learning_material_themes_normalized",
      "gezondheid"
    ).selectedFiltersShouldContain("Thema", "Gezondheid", 1, 0);
    cy.selectFilter(
      "learning_material_themes_normalized",
      "aarde_milieu"
    ).selectedFiltersShouldContain("Thema", "Aarde en Milieu", 2, 1);
  });
});
