describe("Community page - detail", () => {
  beforeEach(function () {
    cy.visit("/communities/62f26a9c-d593-49a5-9330-f4a71a1fd370");
  });

  it("Should display community information in the header", () => {
    cy.get("[data-test=header]").contains("4TU.Ethics").should("be.visible");
    cy.get("[data-test=header]").contains("4TU.Ethics is een gemeenschap van onderzoekers")
      .should("be.visible");
    cy.get("[data-test=header]").contains("Bekijk alle 2 materialen").should("be.visible");
    cy.get("[data-test=header]").contains("Collecties (3)")
      .should("be.visible")
      .should("have.class","v-tab--active");
    cy.get("[data-test=header] .community-logo").should("be.visible");
  });

  it("Should display collections and description under tabs", () => {
    cy.get("[data-test=collection_card]").should("have.length", 3)
    cy.get("[data-test=header]").contains("Over deze community").click();
    cy.get("[data-test=content]").get(".community-description").should("be.visible");
    cy.get("[data-test=content]").contains("4TU.Ethics is een gemeenschap van onderzoekers")
      .should("be.visible")
    cy.get("[data-test=collection_card]").should("not.be.visible");
  });

  it("Should display community information in the right sidebar", () => {
    cy.get("[data-test=content]").contains("Bezoek website")
      .should("have.attr", "href", "https://ethicsandtechnology.eu/")
  });
});
