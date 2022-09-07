describe("Community page - collection", () => {

  beforeEach(function () {
    cy.visit("/mijn/collectie/b1d912ec-8c29-4051-9b3a-4b6563ab3e0a");
    cy.setLocalStorage("surf_token", "123abc");
  });

  it("Should add materials to a collection", () => {
    cy.get("[data-test=add_materials_button]")
      .click()
      .searchFor("esther")
      .searchResultsShouldContain("How can we", 6, 0)
      .get("[data-test=add_select_icon]")
      .eq(0)
      .click({ force: true })
      .get("[data-test=add_select_icon]")
      .eq(1)
      .click({ force: true })
      .get("[data-test=popup_add_materials_button]")
      .should("contain", "2")
      .click();

    // TODO first fix https://www.pivotaltracker.com/story/show/183180947
    // then click the button to send POST request using correct session credentials
  });

  it.skip("Should remove materials from a collection", () => {
    cy.get("[data-test=delete_select_icon]")
      .eq(0)
      .click({ force: true })
      .get("[data-test=delete_select_icon]")
      .should("have.length", 1);
    // TODO first fix https://www.pivotaltracker.com/story/show/183180947
    // then click the button to send POST request using correct session credentials
  });
});
