# Custom Product Attribution System: 3-Tiers Tutorial

This step-by-step tutorial guides you through configuring the Custom Product Attribution System. We will use a **Home Improvement Supply Store** theme to demonstrate the system's progression from basic attribute creation to automated category inheritance, and finally advanced conditional configurator rules.

---

## 🛠️ Tutorial Prerequisites
Ensure you are logged into Odoo with Administrator permissions and the `odoo_product_attribution_system` module is installed.

---

## 📈 Tier 1: Basic Product Attribution

In this tier, we will create custom attributes of different Value Types and set them manually on a product template.

### Step 1.1: Create Custom Attributes
Let's create three attributes representing tool specifications:
1. Navigate to **Sales > Configuration > Products > Attributes** (or **Inventory > Configuration > Products > Attributes**).
2. Click **New** and configure the first attribute:
   * **Attribute Name**: `Power Source`
   * **Value Type**: `Selection`
   * **Attribute Values** (in the bottom sub-tab): Add three values: `Battery (Cordless)`, `Corded Electric`, and `Manual (Hand Tool)`.
3. Save the record.
4. Click **New** and configure the second attribute:
   * **Attribute Name**: `Voltage (V)`
   * **Value Type**: `Integer`
5. Save the record.
6. Click **New** and configure the third attribute:
   * **Attribute Name**: `Warranty Period (Years)`
   * **Value Type**: `Integer`
7. Save the record.

### Step 1.2: Manually Configure a Product Template
1. Go to **Sales > Products > Products** and click **New**.
2. Name the product: `Standard Circular Saw`.
3. Open the **Specifications** tab. Notice the grid is empty.
4. Manually assign attributes:
   * In Odoo, attributes are inherited from categories or sets. To add attributes manually, let's proceed to **Tier 2** to see how we group them.

---

## 🌿 Tier 2: Category Inheritance & Reusable Defaults

In this tier, we group our attributes into an **Attribute Set**, configure default values, link the set to a **Product Category**, and verify that new products automatically inherit them.

### Step 2.1: Create an Attribute Set
1. Navigate to **Sales > Configuration > Products > Attribute Sets**.
2. Click **New** and configure the set:
   * **Name**: `Hardware Tool Specs`
3. Click **Add a line** in the *Attributes* grid to add our three attributes and set defaults:
   * Line 1: Attribute = `Power Source`, Default Selection Value = `Battery (Cordless)`
   * Line 2: Attribute = `Voltage (V)`, Default Integer Value = `18`
   * Line 3: Attribute = `Warranty Period (Years)`, Default Integer Value = `2`
4. Click **Save**.

### Step 2.2: Assign the Set to a Product Category
1. Navigate to **Sales > Configuration > Products > Product Categories**.
2. Click **New** to create a category:
   * **Category Name**: `Tools & Power Hardware`
   * **Parent Category**: `All` (or your root category)
3. In the **Product Attributes** section of the form:
   * Under **Attribute Sets**, click **Add a line** and select `Hardware Tool Specs`.
4. Click **Save**.

### Step 2.3: Verify Automatic Inheritance on Products
1. Go to **Sales > Products > Products** and click **New**.
2. Name the product: `Professional Cordless Jigsaw`.
3. Set **Product Category** to `Tools & Power Hardware`.
4. Open the **Specifications** tab.
5. **Observe**: The specifications grid is automatically populated with three lines:
   * `Power Source` pre-filled as `Battery (Cordless)`
   * `Voltage (V)` pre-filled as `18`
   * `Warranty Period (Years)` pre-filled as `2`
6. Click **Save**.

---

## ⚡ Tier 3: Advanced Conditional Configurator Rules

In this tier, we will create a dependency rule: **If a tool is manual, it does not require battery voltage or motor warranty details.** We will configure Odoo to dynamically hide these attributes in the UI when `Power Source` is set to `Manual (Hand Tool)`.

### Step 3.1: Configure Dependency Rules in the Set
1. Navigate to **Sales > Configuration > Products > Attribute Sets** and open `Hardware Tool Specs`.
2. Open the **Rules** tab.
3. Click **Add a line** to create the first rule (hiding Voltage):
   * **Trigger Attribute**: `Power Source` (value type will auto-populate as *Selection*)
   * **Trigger Selection Values**: Select `Manual (Hand Tool)`
   * **Action**: `Hide Target Attribute`
   * **Target Attribute**: `Voltage (V)`
4. Click **Add a line** to create the second rule (hiding Warranty):
   * **Trigger Attribute**: `Power Source`
   * **Trigger Selection Values**: Select `Manual (Hand Tool)`
   * **Action**: `Hide Target Attribute`
   * **Target Attribute**: `Warranty Period (Years)`
5. Click **Save**.

### Step 3.2: Verify Dynamic UI Behavior on a Product
1. Go to **Sales > Products > Products** and click **New**.
2. Name the product: `Heavy Duty Hand Hacksaw`.
3. Set **Product Category** to `Tools & Power Hardware`.
4. Open the **Specifications** tab.
   * **Initial State**: Since the default `Power Source` is `Battery (Cordless)`, the rules are *not* met. The grid displays all three attributes (`Power Source`, `Voltage`, and `Warranty`).
5. **Change the Power Source**:
   * Click in the `Power Source` column and change it from `Battery (Cordless)` to `Manual (Hand Tool)`.
6. **Observe the Magic**:
   * The `Voltage (V)` and `Warranty Period (Years)` rows **instantly disappear** from the list view!
7. Change the `Power Source` back to `Battery (Cordless)`.
   * The fields instantly reappear, retaining their configured values!
8. Click **Save**.
