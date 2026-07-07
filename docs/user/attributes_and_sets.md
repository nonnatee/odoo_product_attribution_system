# Creating Attributes & Attribute Sets

This guide walks you through configuring custom attributes, choosing data types, grouping attributes into sets, and setting up default values. It also includes guidelines for importing/exporting configurations via Odoo's CSV/Excel tool.

---

## 1. Custom Attributes & Value Types

To define new specifications for your product catalog, you first create **Product Attributes** and assign them a specific data type (Value Type).

### How to Create an Attribute:
1. Navigate to **Sales / Inventory > Configuration > Products > Attributes**.
2. Click **New**.
3. Enter the **Attribute Name** (e.g. *Waterproof* or *Release Date*).
4. Set the **Value Type**:
   * **Text**: For multi-line strings, descriptions, or notes.
   * **Integer**: For whole numbers (e.g. counts, duration in months).
   * **Float**: For decimal numbers (e.g. power consumption, weight).
   * **Date**: For dates (e.g. warranty start, release calendar).
   * **Boolean**: A Yes/No flag (displays as a checkbox).
   * **Selection**: A closed dropdown list. Values must be predefined in the *Attribute Values* sub-tab at the bottom.
5. Set the **Required Globally** checkbox:
   * If enabled, this attribute must be populated on *any* product template that inherits it (across all categories and sets), contributing to the PIM Completeness Score.
6. Click **Save**.

---

## 2. Defining Attribute Sets & Default Values

**Attribute Sets** let you group related attributes together (e.g., *Electronics Specifications* containing attributes: *Warranty Period*, *Waterproof*, *Power Consumption*) and define default values for them.

### How to Create an Attribute Set:
1. Navigate to **Sales / Inventory > Configuration > Products > Attribute Sets**.
2. Click **New**.
3. Enter the **Name** of the set (e.g., *Kitchen Appliance Specs*).
4. Click **Add a line** in the *Attributes* table.
5. Select the **Attribute**. The system will automatically display its **Value Type**.
6. Set the **Default Value** in the appropriate type-specific column.
7. Toggle the **Required** checkbox on the set line:
   * If enabled, this attribute will be required *only* for products that inherit this specific set (rather than globally).
8. Save the record.

---

## 3. Configuring Attribute Set Rules (Configurator)

Attribute Sets support **Rules** which dynamically change the behavior of specifications depending on trigger conditions.

### Trigger Conditions
You can choose any attribute in the set to act as a trigger, matching when its value:
* Matches selected options (for **Selection** types).
* Matches checked/unchecked state (for **Boolean** types).
* Matches specific input characters (for **Text**, **Integer**, **Float**, or **Date** types).

### Action Types
When a rule's condition is met, Odoo will execute one of three actions:
1. **Hide Target Attribute**: Removes the row from the Specifications grid completely.
2. **Disable Target Attribute (Readonly)**: Prevents users from editing the value field in the grid.
3. **Force Target Attribute Value**: Automatically sets a specific value in the target EAV field.

### How to Create a Rule:
1. Navigate to **Sales / Inventory > Configuration > Products > Attribute Sets** and open your set.
2. Open the **Rules** sub-tab.
3. Click **Add a line**:
   * **Trigger Attribute**: Select the attribute that starts the rule.
   * **Trigger values** (fill only the trigger column corresponding to the attribute's type):
     * *Trigger Selection Values*: Predefined dropdown options.
     * *Trigger Boolean Value*: Checked/Unchecked.
     * *Trigger String Value*: Text match.
   * **Action**: Select `Hide Target Attribute`, `Disable Target Attribute (Readonly)`, or `Force Target Attribute Value`.
   * **Target Attribute**: Select the attribute to affect (must belong to the set).
   * **Action values** (required *only* if the action is `Force Target Attribute Value`): Set the value in the column matching the target's type.
4. Save the set.

---

## 4. Administrator Import & Export Guide (CSV/Excel)

For large catalogs, you can import attributes, values, and sets using Odoo's built-in data import utility.

### 3.1 Importing Product Attributes (`product.attribute`)
To bulk-create attributes, import into the `product.attribute` model.

* **Target Model**: `product.attribute`
* **CSV Headers**:
  * `name`: Attribute Name (text)
  * `value_type`: Data type. Must match key values: `text`, `integer`, `float`, `date`, `boolean`, `selection`
  * `create_variant`: How to treat variants (e.g. `no_variant`, `always`, `dynamic`)

* **Example CSV**:
  ```csv
  name,value_type,create_variant
  Screen Size,float,no_variant
  Operating System,selection,no_variant
  Smart features,boolean,no_variant
  ```

### 3.2 Importing Attribute Sets (`product.attribute.set`)
To import sets and set lines, import into the `product.attribute.set` model.

* **Target Model**: `product.attribute.set`
* **CSV Headers**:
  * `name`: Set Name (Char)
  * `attribute_line_ids/attribute_id/id`: External XML ID of the attribute (e.g., `product.product_attribute_1` or custom XML ID) OR `attribute_line_ids/attribute_id/name` (Attribute Name)
  * **Type-specific default columns** (fill ONLY the column corresponding to the attribute's `value_type`):
    * `attribute_line_ids/value_text`: Multi-line text default.
    * `attribute_line_ids/value_integer`: Integer default number.
    * `attribute_line_ids/value_float`: Decimal float default number.
    * `attribute_line_ids/value_date`: Date default (`YYYY-MM-DD`).
    * `attribute_line_ids/value_boolean`: Boolean (`true` / `false` or `1` / `0`).
    * `attribute_line_ids/value_selection_id/id` (or `/name`): Reference to `product.attribute.value` (Selection default).

* **Example CSV**:
  ```csv
  name,attribute_line_ids/attribute_id/name,attribute_line_ids/value_integer,attribute_line_ids/value_boolean,attribute_line_ids/value_text
  Electronics Specs,Warranty Period (Months),12,,
  Electronics Specs,Waterproof,,true,
  Electronics Specs,Special Notes,,,Standard domestic usage
  ```
