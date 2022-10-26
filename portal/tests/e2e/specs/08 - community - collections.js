describe("Community page - collection", () => {
  beforeEach(() => {
    cy.setLocalStorage("surf_token", "123abc");
    cy.visit("/mijn/community/62f26a9c-d593-49a5-9330-f4a71a1fd370?tab=collections-tab");
  });

  it("Should add a collection", () => {
    cy.get("[data-test=add_collection_button]")
      .click()
      .get("[data-test=collection_name_nl_input]")
      .type("Mijn collectie")
      .get("[data-test=collection_name_en_input]")
      .type("My collection")
      .get("[data-test=collection_create_button]")
      .click()
      .get("[data-test=collection_card]")
      .eq(0)
      .should("contain", "Mijn collectie");
  });

  it("Should remove a collection", () => {
    cy.get("[data-test=delete_select_icon]")
      .eq(0)
      .click()
      .get("[data-test=confirm_delete_collection_button]")
      .click()
      .get("[data-test=collection_card]")
      .eq(0)
      .should("not.contain", "Mijn collectie");
  });
});
