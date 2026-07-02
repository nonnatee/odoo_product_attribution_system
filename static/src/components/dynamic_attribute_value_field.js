/** @odoo-module **/

import { Component, onWillStart, onWillUpdateProps, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";

/**
 * DynamicAttributeValueField
 *
 * A field widget for the `value` Char field on `product.template.custom.value`.
 * Instead of editing the generic `value` char, it inspects `value_type` from the
 * current record and renders the appropriate typed input, writing directly to the
 * corresponding EAV typed field (value_text, value_integer, value_float, etc.).
 */
class DynamicAttributeValueField extends Component {
    static template = "odoo_product_attribution_system.DynamicAttributeValueField";
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");

        this.state = useState({
            selectionOptions: [],
            selectionLoading: false,
        });

        onWillStart(async () => {
            await this._loadSelectionOptions(this.props);
        });

        onWillUpdateProps(async (nextProps) => {
            await this._loadSelectionOptions(nextProps);
        });
    }

    // -------------------------------------------------------------------------
    // Selection options loading
    // -------------------------------------------------------------------------

    /**
     * Fetch product.attribute.value records for the current attribute_id
     * when the value_type is 'selection'.
     */
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

    // -------------------------------------------------------------------------
    // Getters for template
    // -------------------------------------------------------------------------

    get valueType() {
        return this.props.record.data.value_type || "text";
    }

    get isReadonly() {
        return this.props.readonly;
    }

    get textValue() {
        return this.props.record.data.value_text || "";
    }

    get integerValue() {
        const v = this.props.record.data.value_integer;
        return v !== false && v !== null && v !== undefined ? v : "";
    }

    get floatValue() {
        const v = this.props.record.data.value_float;
        return v !== false && v !== null && v !== undefined ? v : "";
    }

    get dateValue() {
        const v = this.props.record.data.value_date;
        if (!v) {
            return "";
        }
        // Odoo may return a luxon DateTime or a string
        if (typeof v === "string") {
            return v;
        }
        if (v.toFormat) {
            return v.toFormat("yyyy-MM-dd");
        }
        if (v.toISOString) {
            return v.toISOString().slice(0, 10);
        }
        return String(v);
    }

    get booleanValue() {
        return !!this.props.record.data.value_boolean;
    }

    get selectionValue() {
        const raw = this.props.record.data.value_selection_id;
        return this._extractId(raw) || false;
    }

    /**
     * Readonly display text: delegates to the computed `value` char field.
     */
    get displayValue() {
        const vt = this.valueType;
        if (vt === "boolean") {
            return this.booleanValue ? "Yes" : "No";
        }
        return this.props.record.data.display_value || "";
    }

    get selectionOptions() {
        return this.state.selectionOptions;
    }

    // -------------------------------------------------------------------------
    // Event handlers
    // -------------------------------------------------------------------------

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

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    /**
     * Extract a numeric ID from various Odoo relational field formats:
     *  - [id, "display_name"]  (Many2one tuple)
     *  - { id: ..., display_name: ... }  (record-like)
     *  - a plain number
     */
    _extractId(raw) {
        if (!raw) {
            return false;
        }
        if (Array.isArray(raw)) {
            return raw[0] || false;
        }
        if (typeof raw === "object" && raw.id) {
            return raw.id;
        }
        if (typeof raw === "number") {
            return raw;
        }
        return false;
    }
}

registry.category("fields").add("dynamic_attribute_value", {
    component: DynamicAttributeValueField,
    supportedTypes: ["char"],
});
