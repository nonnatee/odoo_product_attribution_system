# Custom Product Attribution System (Odoo Module)

A professional and robust Odoo module implementing a dynamic, category-based attribute inheritance system and hybrid EAV (Entity-Attribute-Value) data models. This module is built for Odoo 17+ and extends Odoo's product catalog with customizable specifications, inherited default values, and an interactive dynamic OWL widget.

---

## 🚀 Features

### 1. Recursive Category-Based Attribute Inheritance & Channel Unification
- Assign attributes directly or group them inside **Attribute Sets** for any Product Category.
- Categories recursively inherit attributes from their parent hierarchy (supporting deep nesting of multiple levels).
- Automatically prevents duplicate attribute inheritance and circular dependencies.
- Synchronizes standard categories with **POS Categories** (`pos.category`) and **Website/eCommerce categories** (`product.public.category`) via simple configuration toggles.
- Automatically assigns and updates product POS and website categories when a product's standard category is modified.

### 2. Product Attribute Sets & Default Values
- Define reusable groups of attributes as an **Attribute Set**.
- Configure default values for attributes within a set. Supports type-specific fields:
  - **Text**: Multi-line description.
  - **Integer**: Numeric whole values.
  - **Float**: Numeric decimal values.
  - **Date**: Odoo standard calendar date.
  - **Boolean**: Yes/No flag.
  - **Selection**: Pre-defined options (linked to `product.attribute.value`).

### 3. Hybrid EAV (Entity-Attribute-Value) Model
- Stores values on `product.template` using the `product.template.custom.value` model.
- Merges standard structured database fields with EAV flexibility, keeping data queryable while allowing variable attributes.
- Smart resolution hierarchy for default values:
  1. Template-specific attribute sets.
  2. Nested parent-category attribute sets (traversing from nearest parent to root).

### 4. Dynamic OWL Component (`DynamicAttributeValueField`)
- A single widget (`dynamic_attribute_value`) that adapts dynamically to the attribute's `value_type`.
- Switches input controls on-the-fly (e.g., standard text box, number inputs with steps, calendar picker, custom checkbox, or dropdown menu for selections) inside the backend form view list.

### 5. Automated Value Synchronization
- Auto-populates/syncs missing custom attribute fields in `product.template` when changing categories or template sets.
- Safe data preservation: does not delete values on category change (hidden in UI but preserved in the database to prevent data loss).

### 6. Extended Search Filtering
- Filter products dynamically in the search view by custom attribute name and custom attribute values.

### 7. Product Configurator & Conditional Rules
- Define conditional rules directly inside an Attribute Set (under the *Rules* sub-tab).
- Evaluate dependency triggers using equals comparisons (selection options, boolean states, string text matching).
- Execute dynamic target actions:
  - **Hide**: Dynamically hides the target attribute row from the Specifications grid list view using CSS warning decorations.
  - **Readonly**: Automatically disables editing on target EAV widgets.
  - **Set Value**: Overwrites and forces a predefined target value instantly in the web client record cache.

### 8. Product Data Completeness Score
- Dynamically computes a composite **Completeness Score (%)** on product templates.
- Evaluates core fields (Name, Description, Main Image, Product Category) and custom attributes flagged as **Required**.
- Renders a visually clean completeness indicator inside the product sheet header.

### 9. Product Lifecycle Workflow & Stage Locking
- Introduces lifecycle workflow states: **Draft**, **Enriching**, and **Approved**.
- Restricts editing permissions: when in the **Approved** stage, product information and custom specifications are locked as read-only.
- Safe gates: prevents transitioning a product to **Approved** unless its Completeness Score is exactly 100%.

### 10. Digital Asset Management (DAM)
- Dedicated **Documents & Assets** tab on the product template sheet.
- Supports storing and classifying attachments (User Manuals, Datasheets, High-Res Images, Video Links) with descriptions.

### 11. Multi-Channel Export Profiles
- Create custom **Export Profiles** to generate external channel feeds.
- Supports mapping standard fields and custom EAV specifications to custom CSV or JSON structures.
- Generates and delivers download action files for all templates in the **Approved** stage.

---

## 📖 Documentation

Detailed documentation is organized as follows:

### 👤 User & Configuration Guides
* **[User Guide Index](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/docs/user_guide.md)**: Main entry point for administrators and operators.
* **[Attributes & Sets Setup](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/docs/user/attributes_and_sets.md)**: Managing attributes, value types, sets, and CSV imports.
* **[Category Configuration](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/docs/user/category_configuration.md)**: Linking attributes to categories, inheritance, channel unification sync, and imports.
* **[Product Template Management](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/docs/user/product_management.md)**: Editing product specs tab, widget usages, lifecycle workflow locking, and search filterings.
* **[4-Tiers Hands-On Tutorial](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/docs/tutorial.md)**: Configuration guide walk-through covering custom attributes, categories, channel sync, PIM validation, and multi-channel feeds.

### 💻 Developer & Technical Documentation
* **[Technical Documentation Index](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/TECHNICAL_DOCUMENTATION.md)**: System design and high-level architecture diagram.
* **[Architecture & Traversal Logic](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/docs/architecture.md)**: Traversal code flows, cache handling, and cyclic prevention.
* **[Data Models & EAV Schema](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/docs/models.md)**: Database schema relationships and default resolution logic.
* **[OWL Widget Component](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/docs/owl_widget.md)**: Dynamic widget structure, templates, events, and writebacks.
* **[Testing & Coverage Guide](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/docs/testing.md)**: Test coverage tiers, Happy/Edge cases, and execution commands.

---

## 📁 Repository Structure

```text
odoo_product_attribution_system/
├── __init__.py
├── __manifest__.py                 # Module manifest and dependencies (depends on product & sale)
├── TECHNICAL_DOCUMENTATION.md     # Main developer overview and high-level system diagram
├── data/
│   └── demo_data.xml               # Home Improvement wholesaler demo records
├── docs/                           # Specialized guides for traversal, EAV schema, OWL, and tests
├── models/
│   ├── __init__.py
│   ├── product_attribute.py        # Adds value_type selection to attributes
│   ├── product_attribute_set.py    # Sets and default value schemas
│   ├── product_category.py         # Category inheritance logic & template synchronization
│   ├── product_template.py         # Template integration & default value resolvers
│   └── product_template_custom_value.py # EAV model for storing custom attributes per product
├── security/
│   └── ir.model.access.csv         # Access control lists (ACL)
├── static/
│   └── src/
│       └── components/
│           ├── dynamic_attribute_value_field.js   # OWL component code
│           └── dynamic_attribute_value_field.xml  # OWL template code
├── tests/
│   ├── __init__.py
│   └── test_product_attribution.py # Integration test suite (HAPPY and EDGE cases)
└── views/
    ├── product_attribute_set_views.xml
    ├── product_attribute_views.xml
    ├── product_category_views.xml
    └── product_template_views.xml
```

---

## 🛠️ Installation & Setup

1. Copy the `odoo_product_attribution_system` folder into your Odoo custom addons path.
2. Restart the Odoo server.
3. Activate the Developer Mode in Odoo.
4. Go to **Apps**, click **Update Apps List**, search for `Custom Product Attribution System` (`odoo_product_attribution_system`), and click **Activate**.

---

## 📖 How to Use

### Step 1: Define Custom Attributes
1. Go to **Inventory / Sales > Configuration > Attributes**.
2. Create or edit an Attribute and set the **Value Type** (e.g., Integer, Date, Selection, etc.).

### Step 2: Create Attribute Sets
1. Go to **Inventory / Sales > Configuration > Attribute Sets**.
2. Define a new Attribute Set (e.g., *Technical Specifications*).
3. Add lines with attributes and specify the **Default Values** to inherit.

### Step 3: Link to Product Categories
1. Go to **Inventory / Sales > Configuration > Product Categories**.
2. Select a category. Under the **Product Attributes** group, add individual attributes or attribute sets.
3. Subcategories will inherit these attributes recursively.

### Step 4: Manage Attributes on Product Templates
1. Navigate to **Sales / Inventory > Products**.
2. Open a product template. Assign it to a category.
3. Open the **Specifications** tab. You'll see all inherited attributes automatically sync.
4. Set or override attribute values directly in the editable grid. The dynamic OWL widget handles rendering the correct inputs.

---

## 🧪 Testing

The module comes with a comprehensive suite of integration tests (located in `tests/test_product_attribution.py`) covering happy paths and edge cases.

To execute the test suite:
```bash
python3 odoo-bin -c <path_to_odoo_conf> -d <database_name> -i odoo_product_attribution_system --test-enable --stop-after-init
```
