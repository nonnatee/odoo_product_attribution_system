/** @odoo-module **/

import { registry } from "@web/core/registry";

// ==========================================
// Tour 1: End-to-End Product Creation & Attribution Flow
// ==========================================
registry.category("web_tour.tours").add("custom_value_widget_tour", {
    url: "/odoo",
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="stock.menu_stock_root"], .o_app[data-menu-xmlid="sale.sale_menu_root"]',
            content: "Open Inventory or Sales App",
            run: "click",
        },
        {
            trigger: 'a[data-menu-xmlid="stock.menu_product_variant_config_stock"], a[data-menu-xmlid="sale.menu_product_template_action"]',
            content: "Go to Products menu",
            run: "click",
        },
        {
            trigger: 'button.o_list_button_add',
            content: "Click 'New' to create a new product template",
            run: "click",
        },
        {
            trigger: 'input[placeholder="e.g. Cheese Burger"]',
            content: "Enter product name",
            run: "edit Smart Refrigerator Pro",
        },
        {
            trigger: '.o_field_widget[name="categ_id"] input',
            content: "Click category field",
            run: "edit Refrigerators",
        },
        {
            trigger: '.ui-autocomplete a:contains("Refrigerators")',
            content: "Select Refrigerators category",
            run: "click",
        },
        {
            trigger: '.o_field_widget[name="custom_value_ids"] table.o_list_table',
            content: "Verify that custom values table is loaded",
            run: "click",
        },
        {
            trigger: 'tr:has(td:contains("Warranty Details")) td.o_data_cell[name="value"] input',
            content: "Enter Warranty Details text",
            run: "edit 3 Years Parts & Labor",
        },
        {
            trigger: 'tr:has(td:contains("Warranty Period (Months)")) td.o_data_cell[name="value"] input[type="number"]',
            content: "Enter Warranty Period integer",
            run: "edit 36",
        },
        {
            trigger: 'tr:has(td:contains("Power Consumption (kW)")) td.o_data_cell[name="value"] input[type="number"]',
            content: "Enter Power Consumption float",
            run: "edit 1.25",
        },
        {
            trigger: 'tr:has(td:contains("Release Date")) td.o_data_cell[name="value"] input[type="date"]',
            content: "Enter Release Date",
            run: "edit 2026-07-02",
        },
        {
            trigger: 'tr:has(td:contains("Waterproof")) td.o_data_cell[name="value"] input[type="checkbox"]',
            content: "Check Waterproof option",
            run: "click",
        },
        {
            trigger: 'tr:has(td:contains("Efficiency Class")) td.o_data_cell[name="value"] select',
            content: "Select Efficiency Class A",
            run: "select Class A",
        },
        {
            trigger: 'button.o_form_button_save',
            content: "Save the product template",
            run: "click",
        },
        {
            trigger: 'tr:has(td:contains("Warranty Period (Months)")) td.o_data_cell[name="value"]:contains("36")',
            content: "Verify warranty period was saved correctly",
            run: "click",
        },
    ],
});

// ==========================================
// Tour 2: Category Reassignment & Value Retention
// ==========================================
registry.category("web_tour.tours").add("custom_value_widget_retention_tour", {
    url: "/odoo",
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="stock.menu_stock_root"], .o_app[data-menu-xmlid="sale.sale_menu_root"]',
            content: "Open Inventory or Sales App",
            run: "click",
        },
        {
            trigger: 'a[data-menu-xmlid="stock.menu_product_variant_config_stock"], a[data-menu-xmlid="sale.menu_product_template_action"]',
            content: "Go to Products menu",
            run: "click",
        },
        {
            trigger: 'button.o_list_button_add',
            content: "Click 'New'",
            run: "click",
        },
        {
            trigger: 'input[placeholder="e.g. Cheese Burger"]',
            content: "Enter product name",
            run: "edit Retention Test Product",
        },
        {
            trigger: '.o_field_widget[name="categ_id"] input',
            content: "Set category to Refrigerators",
            run: "edit Refrigerators",
        },
        {
            trigger: '.ui-autocomplete a:contains("Refrigerators")',
            content: "Select Refrigerators",
            run: "click",
        },
        {
            trigger: 'tr:has(td:contains("Warranty Details")) td.o_data_cell[name="value"] input',
            content: "Enter text details",
            run: "edit Retention Test",
        },
        {
            trigger: 'tr:has(td:contains("Warranty Period (Months)")) td.o_data_cell[name="value"] input[type="number"]',
            content: "Enter integer details",
            run: "edit 12",
        },
        {
            trigger: 'button.o_form_button_save',
            content: "Save",
            run: "click",
        },
        {
            trigger: '.o_field_widget[name="categ_id"] input',
            content: "Change category to parent Electronics",
            run: "edit Electronics",
        },
        {
            trigger: '.ui-autocomplete a:contains("Electronics")',
            content: "Select Electronics",
            run: "click",
        },
        {
            trigger: 'button.o_form_button_save',
            content: "Save under new category",
            run: "click",
        },
        {
            trigger: 'tr:has(td:contains("Warranty Period (Months)")) td.o_data_cell[name="value"]:contains("12")',
            content: "Verify that parent category attribute retains its value",
            run: "click",
        },
        {
            trigger: '.o_field_widget[name="categ_id"] input',
            content: "Change category back to Refrigerators",
            run: "edit Refrigerators",
        },
        {
            trigger: '.ui-autocomplete a:contains("Refrigerators")',
            content: "Select Refrigerators",
            run: "click",
        },
        {
            trigger: 'button.o_form_button_save',
            content: "Save once more",
            run: "click",
        },
        {
            trigger: 'tr:has(td:contains("Warranty Details")) td.o_data_cell[name="value"]:contains("Retention Test")',
            content: "Verify that custom details were retained",
            run: "click",
        },
    ],
});

// ==========================================
// Tour 3: Advanced Search and Filter Journey
// ==========================================
registry.category("web_tour.tours").add("custom_value_widget_search_tour", {
    url: "/odoo",
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="stock.menu_stock_root"], .o_app[data-menu-xmlid="sale.sale_menu_root"]',
            content: "Open main application",
            run: "click",
        },
        {
            trigger: 'a[data-menu-xmlid="stock.menu_product_variant_config_stock"], a[data-menu-xmlid="sale.menu_product_template_action"]',
            content: "Navigate to Products",
            run: "click",
        },
        {
            trigger: '.o_searchview_input',
            content: "Click search view input",
            run: "edit Warranty Period (Months)",
        },
        {
            trigger: '.o_searchview_autocomplete li:first-child',
            content: "Select first autocomplete option",
            run: "click",
        },
        {
            trigger: '.o_searchview_input',
            content: "Input search value",
            run: "edit 36",
        },
        {
            trigger: '.o_searchview_autocomplete li:first-child',
            content: "Filter by value",
            run: "click",
        },
        {
            trigger: '.o_kanban_view, .o_list_view',
            content: "Confirm view renders filtered results",
            run: "click",
        },
    ],
});

// ==========================================
// Tour 4: OWL Widget Input Validation
// ==========================================
registry.category("web_tour.tours").add("custom_value_widget_validation_tour", {
    url: "/odoo",
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="stock.menu_stock_root"], .o_app[data-menu-xmlid="sale.sale_menu_root"]',
            content: "Open App",
            run: "click",
        },
        {
            trigger: 'a[data-menu-xmlid="stock.menu_product_variant_config_stock"], a[data-menu-xmlid="sale.menu_product_template_action"]',
            content: "Go to Products",
            run: "click",
        },
        {
            trigger: 'button.o_list_button_add',
            content: "New Product",
            run: "click",
        },
        {
            trigger: 'input[placeholder="e.g. Cheese Burger"]',
            content: "Name product",
            run: "edit Validation Test Product",
        },
        {
            trigger: '.o_field_widget[name="categ_id"] input',
            content: "Set category",
            run: "edit Refrigerators",
        },
        {
            trigger: '.ui-autocomplete a:contains("Refrigerators")',
            content: "Select category",
            run: "click",
        },
        {
            trigger: 'tr:has(td:contains("Warranty Period (Months)")) td.o_data_cell[name="value"] input[type="number"]',
            content: "Enter invalid non-integer characters or click it",
            run: "edit abc",
        },
        {
            trigger: 'button.o_form_button_save',
            content: "Click save to check if validation runs",
            run: "click",
        },
        {
            trigger: 'tr:has(td:contains("Warranty Period (Months)")) td.o_data_cell[name="value"] input[type="number"]',
            content: "Fix to a valid number",
            run: "edit 24",
        },
        {
            trigger: 'button.o_form_button_save',
            content: "Save successfully",
            run: "click",
        },
    ],
});

// ==========================================
// Tour 5: Hot-Adding Attributes to Active Products
// ==========================================
registry.category("web_tour.tours").add("custom_value_widget_admin_tour", {
    url: "/odoo",
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="stock.menu_stock_root"], .o_app[data-menu-xmlid="sale.sale_menu_root"]',
            content: "Open App",
            run: "click",
        },
        {
            trigger: 'a[data-menu-xmlid="stock.menu_product_category_config_stock"], a[data-menu-xmlid="sale.menu_product_category_action"]',
            content: "Go to Product Categories",
            run: "click",
        },
        {
            trigger: 'tr:has(td:contains("Refrigerators")) a, td[name="display_name"]:contains("Refrigerators")',
            content: "Open Refrigerators Category",
            run: "click",
        },
        {
            trigger: '.o_field_widget[name="attribute_ids"] .o_field_x2many_list_row_add a',
            content: "Add an attribute to category",
            run: "click",
        },
        {
            trigger: '.o_field_widget[name="attribute_ids"] input',
            content: "Type Brand Name attribute",
            run: "edit Brand Name",
        },
        {
            trigger: 'button.o_form_button_save',
            content: "Save Category",
            run: "click",
        },
        {
            trigger: 'a[data-menu-xmlid="stock.menu_product_variant_config_stock"], a[data-menu-xmlid="sale.menu_product_template_action"]',
            content: "Navigate back to Products list",
            run: "click",
        },
        {
            trigger: 'tr:has(td:contains("Smart Refrigerator Pro")) a, td[name="name"]:contains("Smart Refrigerator Pro")',
            content: "Open Smart Refrigerator Pro Product",
            run: "click",
        },
        {
            trigger: 'tr:has(td:contains("Brand Name")) td.o_data_cell[name="value"] input',
            content: "Input Brand Name",
            run: "edit BrandX",
        },
        {
            trigger: 'button.o_form_button_save',
            content: "Save product",
            run: "click",
        },
    ],
});
