// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This is will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

Cypress.Commands.add("search", () => {
  cy.get("[data-test=search_button]").click();
});

Cypress.Commands.add("searchFor", (search_term) => {
  cy.get("[data-test=search_term]")
    .type(search_term)
    .get("[data-test=search_button]")
    .click();
});

Cypress.Commands.add(
  "searchResultsShouldContain",
  (search_term, no_of_results, item_nr) => {
    cy.get("[data-test=search_results]")
      .should("be.visible")
      .children()
      .should("have.length", no_of_results ? no_of_results : 10)
      .eq(item_nr ? item_nr : 0)
      .should("contain", search_term);
  }
);

Cypress.Commands.add(
  "selectedFiltersShouldContain",
  (filter_name, filter_value, no_of_filters, filter_nr) => {
    cy.get("[data-test=selected_filters]")
      .should("be.visible")
      .children()
      .should("have.length", no_of_filters ? no_of_filters + 1 : 2) // children also includes the reset button
      .eq(filter_nr ? filter_nr : 0)
      .should("be.visible")
      .should("contain", filter_name)
      .should("contain", filter_value);
  }
);

Cypress.Commands.add("selectFilter", (filter_category, filter_name) => {
  cy.get(`[data-test='${filter_category}']`)
    .find(".filter-categories__subitems")
    .invoke("attr", "style", "display: block");
  cy.get(
    `[data-category-id='${filter_category}'][data-item-id='${filter_name}']`
  )
    .should("be.visible")
    .click();
});

Cypress.Commands.add("selectPreFilter", (filter_category, filter_name) => {
  cy.get("[data-test='presearch_filters']")
    .should("be.visible")
    .get(`[data-test='filter_${filter_category}']`)
    .click()
    .get(`[data-test='filter_${filter_category}_${filter_name}']`)
    .should("be.visible")
    .click();
});
