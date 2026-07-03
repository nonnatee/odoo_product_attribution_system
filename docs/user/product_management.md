# Product Template Specifications

This guide details operating the **Specifications** tab on Product Templates, using the dynamic input controls (OWL widget), understanding the defaults resolution, searching/filtering products by attributes, and importing template values via CSV.

---

## 1. Specifications Tab & Dynamic OWL Widget

When you open a product template, a custom tab named **Specifications** displays a grid of inherited custom attributes.

### Dynamic Inputs (OWL Widget)
Instead of editing generic text, the grid displays interactive inputs that switch dynamically based on the attribute's `value_type`:

* **Text**: Displays a standard text box.
* **Integer**: Displays a numeric input restricted to whole numbers (e.g. increments/decrements by `1`).
* **Float**: Displays a decimal numeric input supporting arbitrary floating-point values (e.g. `3.14`).
* **Date**: Displays a native browser date-picker calendar.
* **Boolean**: Displays a standard checkbox toggle.
* **Selection**: Displays a dropdown selector containing options fetched directly from the attribute's preset values.

### Readonly Mode
If the product template form is in read-only mode, the dynamic widget displays computed, user-friendly labels (e.g., displaying `Yes`/`No` instead of a checkbox, or rendering the selected dropdown label).

### Dynamic UI Behavior (Configurator Rules)
When the product is in edit mode and values are changed in the Specifications tab:
* **Hiding Rows**: If a conditional hide rule matches, the target attribute row **instantly disappears** from the Specifications grid. If the triggering value is changed back, the row reappears with its previous value intact.
* **Read-only / Disabling**: If a conditional readonly rule matches, the input field for the target attribute is instantly disabled/grayed-out.
* **Forcing Values**: If a conditional set_value rule matches, the target EAV field is instantly updated with the predefined action value in the browser.

---

## 2. Default Values Resolution

When a product category or template set is assigned, missing custom specification rows are created automatically. The system pre-fills these lines using defaults:

1. **Product Template Sets**: Odoo first checks if the attribute belongs to an attribute set directly assigned to the product template. If so, it applies that set's default value.
2. **Category Hierarchy**: If not resolved, Odoo moves up the category hierarchy tree (starting from the template's active category, then its parent, then grandparent, etc.) and searches for assigned sets. The first default value it finds is applied.
3. **Blank Default**: If no set specifies a default, the attribute value remains empty (false/null).

---

## 3. Extended Search & Filters

The system integrates custom attribute values directly into Odoo's standard search bar.

### How to Filter Products:
1. Navigate to **Sales / Inventory > Products > Products**.
2. Type in the Odoo search bar in the top-right:
   * To filter by attribute names: Type a name and select **Search Custom Attribute Name for: [search term]**.
   * To filter by value values: Type a value and select **Search Custom Attribute Value for: [search term]**.
3. The list view will instantly filter to show templates matching the search.

---

## 4. Administrator Import Guide (CSV/Excel)

Importing specification values onto products requires importing into the EAV lines model `product.template.custom.value` associated with the product template.

### 4.1 Step 1: Initialize Products
Before importing custom values, make sure your products have their categories assigned. Changing category in Odoo will trigger the creation of the blank value rows, pre-filled with defaults.

### 4.2 Step 2: Import Custom Values
Import custom values into the `product.template.custom.value` model.

* **Target Model**: `product.template.custom.value`
* **CSV Headers**:
  * `product_tmpl_id/id`: External XML ID of the product template (e.g., `__export__.product_template_42_a`)
  * `attribute_id/id`: External XML ID of the attribute (e.g., `product.product_attribute_1`)
  * **Type-specific value columns** (fill ONLY the column corresponding to the attribute's `value_type`):
    * `value_text`: Your custom multi-line text value.
    * `value_integer`: Your custom integer value.
    * `value_float`: Your custom decimal float value.
    * `value_date`: Your custom Date (`YYYY-MM-DD`).
    * `value_boolean`: Your custom Boolean (`true` / `false`).
    * `value_selection_id/id` (or `/name`): Reference to `product.attribute.value` option.

* **Example CSV**:
  ```csv
  product_tmpl_id/id,attribute_id/id,value_integer,value_boolean,value_text,value_date
  __export__.product_template_42_a,product.product_attribute_warranty,24,,,
  __export__.product_template_42_a,product.product_attribute_waterproof,,true,,
  __export__.product_template_42_b,product.product_attribute_warranty,36,,,
  __export__.product_template_42_b,product.product_attribute_release_date,,,,2026-07-02
  ```
