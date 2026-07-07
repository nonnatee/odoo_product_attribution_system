# Category Configuration & Inheritance

This guide explains how to link attributes and attribute sets directly to Product Categories, how the inheritance tree propagates, and how Odoo updates products dynamically when category configurations change.

---

## 1. Assigning Attributes & Sets to Product Categories

Categories are the backbone of the attribution system. By linking attributes or sets directly to a category, you ensure that all products belonging to that category (and any subcategories) will inherit those attributes automatically.

### How to Configure a Category:
1. Navigate to **Sales / Inventory > Configuration > Products > Product Categories**.
2. Create a new category or select an existing one (e.g., *Refrigerators*).
3. Look at the **Product Attributes** section:
   * **Attributes (Many2many)**: Add individual custom attributes.
   * **Attribute Sets (Many2many)**: Add attribute sets (e.g., *Kitchen Appliance Specs*).
4. Save the category.

---

## 2. Category Tree Recursive Inheritance

The module aggregates attributes recursively up the category tree structure:

```text
[Parent Category: Electronics] (Attributes: Screen Size)
         ▲
         │ (propagates downward)
[Sub-Category: Computers] (Attributes: Operating System)
         ▲
         │ (propagates downward)
[Grandchild Category: Laptops] (Attributes: Weight)
```

In the example above, a product assigned to the **Laptops** category will automatically inherit three attributes:
1. `Weight` (direct)
2. `Operating System` (inherited from Computers)
3. `Screen Size` (inherited from Electronics)

### Core Inheritance Rules:
* **Unique Aggregation**: If the same attribute is added to both a parent and a child category (or inside multiple sets assigned to the hierarchy), the system unique-aggregates them. No duplicates will show up in the product template.
* **Hierarchy Sane Constraints**: You cannot save a category that loops on itself (e.g., setting a category as its own parent). The system will raise a validation error.

---

## 3. Dynamic Product Template Synchronization

When a category's attributes or sets are updated, the changes cascade down to products:

* **Automatic Sync**: Adding a new attribute to a category immediately creates empty/default custom value records on all active product templates belonging to that category and its subcategories.
* **Safe Transition (No Data Loss)**: If an attribute is *removed* from a category, Odoo hides the attribute in the specifications view of the product template. However, **it does not delete the saved values from the database**. If you temporarily change category configurations or move a product, your entered value rows are safely preserved and will reappear if the attribute is re-linked.

---

## 4. Category Channel Unification (POS & eCommerce)

To maintain a unified catalog across different sales channels, the system supports synchronizing standard product categories (`product.category`) with Point of Sale categories (`pos.category`) and Website public categories (`product.public.category`).

### Configuration Options
In any product category form view, the **Category Channel Synchronization** section contains two toggles:
* **Sync to POS**: When enabled, creates a matching `pos.category` record.
* **Sync to eCommerce**: When enabled, creates a matching `product.public.category` record.

### Key Synchronization Rules:
* **Hierarchy Replication**: The system automatically replicates the parent-child relationships. If a child standard category is synced and its parent standard category is also synced, the child POS/eCommerce category parent link will point directly to the parent POS/eCommerce category.
* **Dynamic Updates**: Modifying a category name or changing its parent hierarchy instantly updates the mapped POS and Website records.
* **Safe Cleanup**: Unchecking the sync options or deleting the standard category record automatically unlinks and deletes the corresponding POS and eCommerce categories to keep catalog channels clean.
* **Product Association Auto-Sync**: When you assign a product template to a synchronized standard category, Odoo automatically maps the product to the matching POS category and adds it to the eCommerce website public categories.

---

## 5. Administrator Import Guide (CSV/Excel)

To import category configurations linked to attributes and sets:

* **Target Model**: `product.category`
* **CSV Headers**:
  * `name`: Category Name
  * `parent_id/id` (or `/name`): Parent Category relation
  * `attribute_ids/id` (or `/name`): Comma-separated list of individual attribute XML IDs or Names
  * `attribute_set_ids/id` (or `/name`): Comma-separated list of Attribute Set XML IDs or Names

* **Example CSV**:
  ```csv
  name,parent_id/name,attribute_ids/name,attribute_set_ids/name
  Electronics,,,
  Computers,Electronics,Screen Size,
  Laptops,Computers,Weight,Electronics Specs
  ```
