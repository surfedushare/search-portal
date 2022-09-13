describe("Community page - collection", () => {
  beforeEach(() => {
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
      .click()
      .get("[data-test=add_select_icon]")
      .eq(1)
      .click()
      .get("[data-test=popup_add_materials_button]")
      .should("contain", "2")
      .click();
  });

  it("Should remove materials from a collection", () => {
    cy.get("[data-test=delete_select_icon]")
      .eq(0)
      .click()
      .get("[data-test=delete_select_icon]")
      .eq(1)
      .click()
      .get("[data-test=delete_select_icon]")
      .should("not.exist");
  });
});
