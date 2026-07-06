# Dynamic OWL Component Widget

This document explains the dynamic OWL component (`DynamicAttributeValueField`), which switches its layout on-the-fly and writes data back to EAV fields.

---

## 1. Overview & Registry

The widget `dynamic_attribute_value` targets the `display_value` Char field in list views (inside Odoo backend form views, such as specifications grid list). Rather than standard text editing, it dynamically swaps input controls according to the record's `value_type`.

It is registered in [static/src/components/dynamic_attribute_value_field.js](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/static/src/components/dynamic_attribute_value_field.js#L222-L225):

```javascript
registry.category("fields").add("dynamic_attribute_value", {
    component: DynamicAttributeValueField,
    supportedTypes: ["char"],
});
```

---

## 2. Dynamic Input Controls Switching

The component's XML template uses Odoo's template tags (`t-if`, `t-elif`) to evaluate the active `value_type` on the record.

In [static/src/components/dynamic_attribute_value_field.xml](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/static/src/components/dynamic_attribute_value_field.xml):

| `value_type` | Rendered Input Control | Target Field in ORM |
| :--- | :--- | :--- |
| **`text`** | `<input type="text" class="o_input">` | `value_text` |
| **`integer`** | `<input type="number" step="1" class="o_input">` | `value_integer` |
| **`float`** | `<input type="number" step="any" class="o_input">` | `value_float` |
| **`date`** | `<input type="date" class="o_input">` | `value_date` |
| **`boolean`** | `<input type="checkbox" class="form-check-input">` | `value_boolean` |
| **`selection`** | `<select class="o_input">` | `value_selection_id` |

### Readonly Mode
The widget's `isReadonly` getter decides whether to display inputs or the simple read-only span. It evaluates to `true` if:
1. Odoo's standard view layout sets the field as read-only (`this.props.readonly`).
2. The active record has `is_readonly` computed as `true` by dynamic configurator rules (`this.props.record.data.is_readonly`).

```javascript
    get isReadonly() {
        return this.props.readonly || !!this.props.record.data.is_readonly;
    }
```

When evaluated to `true`, the widget acts as a simple span tag rendering the computed string:
```xml
<t t-if="isReadonly">
    <span t-esc="displayValue"/>
</t>
```

---

## 3. Dropdown Option Loading

When `value_type` evaluates to `selection`, the component fetches the valid list of options from Odoo's `product.attribute.value` model asynchronously.

To fetch these options, it queries standard RPC using Odoo's `orm` service during lifecycle hooks (`onWillStart` and `onWillUpdateProps`):

```javascript
    async _loadSelectionOptions(props) {
        const record = props.record;
        const valueType = record.data.value_type;

        if (valueType !== "selection") {
            this.state.selectionOptions = [];
            return;
        }

        const attributeIdRaw = record.data.attribute_id;
        const attributeId = this._extractId(attributeIdRaw);

        if (!attributeId) {
            this.state.selectionOptions = [];
            return;
        }

        this.state.selectionLoading = true;
        try {
            const options = await this.orm.searchRead(
                "product.attribute.value",
                [["attribute_id", "=", attributeId]],
                ["id", "name"],
                { order: "sequence, id" }
            );
            this.state.selectionOptions = options;
        } catch (err) {
            console.error("DynamicAttributeValueField: failed to load selection options", err);
            this.state.selectionOptions = [];
        } finally {
            this.state.selectionLoading = false;
        }
    }
```

---

## 4. ORM Writeback Event Handlers

Each input control binds to a distinct change event handler (`t-on-change`), which intercepts input entries, converts data to correct primitives, and executes updates on the Odoo web client record cache.

```javascript
    onTextChange(ev) {
        this.props.record.update({ value_text: ev.target.value || false });
    }

    onIntegerChange(ev) {
        const raw = ev.target.value;
        const parsed = parseInt(raw, 10);
        this.props.record.update({
            value_integer: isNaN(parsed) ? false : parsed,
        });
    }

    onFloatChange(ev) {
        const raw = ev.target.value;
        const parsed = parseFloat(raw);
        this.props.record.update({
            value_float: isNaN(parsed) ? false : parsed,
        });
    }

    onDateChange(ev) {
        const raw = ev.target.value;
        this.props.record.update({ value_date: raw || false });
    }

    onBooleanChange(ev) {
        this.props.record.update({ value_boolean: ev.target.checked });
    }

    onSelectionChange(ev) {
        const raw = ev.target.value;
        const id = raw ? parseInt(raw, 10) : false;
        if (id) {
            const option = this.state.selectionOptions.find((o) => o.id === id);
            if (option) {
                this.props.record.update({
                    value_selection_id: [id, option.name],
                });
                return;
            }
        }
        this.props.record.update({ value_selection_id: false });
    }
```
These updates automatically mark the Odoo form as dirty and trigger computes/onchanges, providing a standard, reactive user experience.
