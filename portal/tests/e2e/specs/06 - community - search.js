describe("Community page - search", () => {
  beforeEach(function () {
    cy.visit("/communities/62f26a9c-d593-49a5-9330-f4a71a1fd370");
  });

  it("Should find materials by author when clicking the author on the material page", () => {
    cy.get("[data-test=community_search_link]")
      .click()
      .searchResultsShouldContain("little big histories", 2, 0)
      .searchResultsShouldContain("big history", 2, 1)
      .selectedFiltersShouldContain("Samenwerkingsverband", "Community Ethics");
  });

});
