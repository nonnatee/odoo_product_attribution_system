# Traversal Logic & System Architecture

This document explains the core traversal logic, recursive category-based inheritance, cyclic inheritance prevention, and performance considerations for the Custom Product Attribution System.

---

## 1. Category-Based Attribute Inheritance

In Odoo, product templates are organized in a parent-child category tree (`product.category`). To enable dynamic specifications on products, categories are mapped to attributes and attribute sets.

### Traversal Algorithm

The attributes active on a category are a union of:
1. Attributes directly defined on the category (`attribute_ids`).
2. Attributes from sets directly assigned to the category (`attribute_set_ids`).
3. Inherited attributes from parent categories recursively up to the root parent.

This is implemented dynamically in [models/product_category.py](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/models/product_category.py#L32-L47):

```python
    @api.depends('attribute_ids', 'attribute_set_ids.attribute_line_ids.attribute_id', 'parent_id.all_inherited_attribute_ids')
    def _compute_all_inherited_attribute_ids(self):
        for category in self:
            visited = {category.id}
            attrs = category.attribute_ids
            if category.attribute_set_ids:
                attrs |= category.attribute_set_ids.mapped('attribute_line_ids.attribute_id')
            parent = category.parent_id
            while parent and parent.id not in visited:
                visited.add(parent.id)
                attrs |= parent.attribute_ids
                if parent.attribute_set_ids:
                    attrs |= parent.attribute_set_ids.mapped('attribute_line_ids.attribute_id')
                parent = parent.parent_id
            category.all_inherited_attribute_ids = attrs
```

---

## 2. Cyclic Inheritance Prevention

To prevent infinite loops when traversing parent categories, the system enforces constraints:

* **Odoo Built-in Cyclic Check**: The parent category assignment uses Odoo's native hierarchy validation.
* **Traversal Visited Set**: The `while` loop maintains a `visited` set containing category IDs. If a circular path is encountered (e.g., in corrupted DB records), the traversal halts immediately via `parent.id not in visited`.
* **SQL/Model Level Constraints**: In [models/product_category.py](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/models/product_category.py#L49-L52), a python constraint validates hierarchy sanity:

```python
    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError('Error! You cannot create recursive categories.')
```

---

## 3. Performance Considerations

Recursive computation can become expensive for deep hierarchies or huge catalogs. The system addresses performance through several mechanisms:

### Caching and Recomputation
* The field `all_inherited_attribute_ids` is computed dynamically (`store=False`).
* Traversal executes in memory on pre-cached records. Odoo's ORM caches `parent_id` pre-fetches, making the `while` loop traverse fast without triggering sequential SQL `SELECT` queries for every parent step.
* Direct attributes (`attribute_ids`) are indexed in the relational mapping table (`product_category_product_attribute_rel`), ensuring rapid fetches.

### Smart Cascaded Synchronizations
When category attributes, sets, or hierarchy are modified, existing products need their attribute value rows updated. Rather than scanning all templates in the database, the system triggers a targeted update on category write:
1. Performs a tree search for descendant subcategories (`child_of`).
2. Performs a search for product templates referencing those subcategory IDs.
3. Invokes the template EAV synchronization method `_sync_custom_values()`.

This targeted cascade is defined in [models/product_category.py](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/models/product_category.py#L54-L63):

```python
    def write(self, vals):
        res = super().write(vals)
        if any(f in vals for f in ('attribute_ids', 'attribute_set_ids', 'parent_id')):
            descendants = self.search([('id', 'child_of', self.ids)])
            templates = self.env['product.template'].search([
                ('categ_id', 'in', descendants.ids),
            ])
            templates._sync_custom_values()
        return res

---

## 4. Conditional Attribute Rules Engine & Dynamic Hiding

The product configurator layer evaluates dependency rules on-the-fly.

### Dynamic Visibility & Readonly Compute
When values are changed in the Specifications grid, the Odoo client triggers recomputation of `is_visible` and `is_readonly` fields on-the-fly.

### Hiding Rows with Zero JS Overrides
To physically collapse/hide records marked as invisible without complex custom list view renderers, the system uses a combination of Odoo dynamic decorations and a clean CSS display rule:
1. The `<list>` view in `views/product_template_views.xml` defines `decoration-warning="not is_visible"`.
2. When `is_visible` evaluates to `False`, Odoo automatically appends the class `text-warning` to the row's `<tr>` element.
3. The custom CSS stylesheet in [static/src/css/product_attribution.css](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/static/src/css/product_attribution.css) defines:
   ```css
   .o_field_one2many[name="custom_value_ids"] tr.text-warning {
       display: none !important;
   }
   ```
4. This instantly collapses the row from the DOM while preserving record cache integrity (hidden data is never deleted, preventing data loss).
```
