# Custom Product Attribution System: 5-Tiers End-to-End Tutorial

This tutorial provides a hands-on walkthrough to configure custom product attributes, propagate inheritance trees, establish category-based channel synchronization, define dynamic conditional configurator rules, manage PIM lifecycle states, and generate external multi-channel export feeds.

We will use a **Home Improvement Supply & Hardware Store** theme to demonstrate the system's end-to-end capabilities.

---

## 🛠️ Prerequisites
* Ensure the **Custom Product Attribution System** module is installed.
* Ensure you are logged in as an Administrator or have PIM Manager access.

---

## 📂 Tier 1: Basic EAV Attributes & Attribute Sets

In this tier, we will create custom attributes of different Value Types and bundle them into a reusable group with defaults.

### Step 1.1: Create Custom Attributes
Let's create three attributes representing tool specifications:
1. Go to **Sales > Configuration > Products > Attributes** (or **Inventory > Configuration > Products > Attributes**).
2. Click **New** and configure the first attribute:
   * **Attribute Name**: `Power Source`
   * **Value Type**: `Selection`
   * **Attribute Values** (in the bottom sub-tab): Click **Add a line** and create three options: `Battery (Cordless)`, `Corded Electric`, and `Manual (Hand Tool)`.
3. Save the record.
4. Click **New** and configure the second attribute:
   * **Attribute Name**: `Voltage (V)`
   * **Value Type**: `Integer`
5. Save the record.
6. Click **New** and configure the third attribute:
   * **Attribute Name**: `Warranty Period (Years)`
   * **Value Type**: `Integer`
7. Save the record.

### Step 1.2: Build an Attribute Set with Defaults
1. Go to **Sales > Configuration > Products > Attribute Sets**.
2. Click **New** and configure the set:
   * **Name**: `Hardware Tool Specs`
3. Click **Add a line** in the *Attributes* grid to add our three attributes and set defaults:
   * **Power Source**: Default Selection Value = `Battery (Cordless)`
   * **Voltage (V)**: Default Integer Value = `18`
   * **Warranty Period (Years)**: Default Integer Value = `2`, check the **Required** box (making this specification mandatory for completeness checks).
4. Click **Save**.

---

## 🌳 Tier 2: Category Inheritance & Channel Sync

In this tier, we will link our attribute set to a product category, enable recursive propagation down the category tree, and configure auto-sync links to external sales channels.

### Step 2.1: Configure Category Propagation & Channel Synchronization
1. Go to **Sales > Configuration > Products > Product Categories**.
2. Click **New** to create a category:
   * **Category Name**: `Tools & Power Hardware`
   * **Parent Category**: `All`
3. In the **Product Attributes** section of the form:
   * Under **Attribute Sets**, click **Add a line** and select `Hardware Tool Specs`.
4. In the **Category Channel Synchronization** section:
   * Check **Sync to POS** (automatically creates/links a matching Point of Sale category).
   * Check **Sync to eCommerce** (automatically creates/links a matching Website public category).
5. Click **Save**.

### Step 2.2: Assign Product and Verify Synchronization
1. Go to **Sales > Products > Products** and click **New**.
2. Name the product: `Professional Cordless Jigsaw`.
3. Set **Product Category** to `Tools & Power Hardware`.
4. Click **Save**.
5. **Verify sync and inheritance**:
   * Open the **Specifications** tab: notice the grid is automatically populated with the attributes and their default values (`Power Source` = `Battery (Cordless)`, `Voltage (V)` = `18`, `Warranty Period (Years)` = `2`).
   * Inspect the category fields: the mapped Point of Sale Category (`pos_categ_id`) and website Public Categories (`public_categ_ids`) are automatically synchronized to match the `Tools & Power Hardware` category.

---

## ⚡ Tier 3: Advanced Conditional Configurator Rules

In this tier, we will create a dependency rule: **If a tool is manual, it does not require battery voltage or motor warranty details.** We will configure the system to dynamically hide these attributes in the UI when `Power Source` is set to `Manual (Hand Tool)`.

### Step 3.1: Configure Dependency Rules in the Set
1. Go to **Sales > Configuration > Products > Attribute Sets** and open `Hardware Tool Specs`.
2. Open the **Rules** tab.
3. Click **Add a line** to create the first rule (hiding Voltage):
   * **Trigger Attribute**: `Power Source`
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
6. **Observe the Dynamic Hiding**:
   * The `Voltage (V)` and `Warranty Period (Years)` rows **instantly disappear** from the specifications list view!
7. Change the `Power Source` back to `Battery (Cordless)`.
   * The fields instantly reappear, retaining their configured values.
8. Click **Save**.

---

## 📈 Tier 4: PIM Lifecycle, Completeness, & DAM

In this tier, we will enrich product data, observe completeness score constraints, upload manuals, and lock the catalog record to prevent unauthorized edits.

### Step 4.1: Track the Completeness Score
1. Open the form for `Professional Cordless Jigsaw`.
2. Notice the **Completeness Score** indicator in the top-right header reads `40%`. This is because:
   * Core fields Name and Category are filled.
   * Core fields Sales Description and Main Image are empty.
   * The required EAV specification `Warranty Period (Years)` is pre-filled, but does not satisfy 100% until core details are fully enriched.
3. Edit the product:
   * Add a **Sales Description** (e.g., "Heavy-duty 18V cordless jigsaw with variable speed trigger").
   * Upload a **Product Image**.
4. Navigate to the **Specifications** tab and ensure all fields are filled.
5. Click **Save**.
6. The **Completeness Score** now updates to **100%**.

### Step 4.2: Manage Digital Attachments (DAM)
1. Go to the **Documents & Assets** tab on `Professional Cordless Jigsaw`.
2. Click **Add a line**:
   * **Asset Title**: `Professional Cordless Jigsaw User Manual`
   * **Asset Type**: Select `User Manual`.
   * **File Attachment**: Upload a PDF guide file.
3. Click **Save**.

### Step 4.3: Lifecycle Transition & Approval Locking
1. In the product form header, click **Start Enriching** (transitions stage to `Enriching`).
2. Click **Approve Product** (transitions stage to `Approved`).
3. Observe:
   * The **Approved** success ribbon displays on the template.
   * Try to edit the product name or specifications—Odoo raises a **Validation Error** stating the record is locked.
4. To modify again, click **Reset to Draft** or **Start Enriching** in the header.

### Step 4.4: Test Lock Bypass and User Roles
1. Go to **Sales/Inventory > Configuration > Products > PIM Settings**.
2. Check the **Allow Lock Bypass** parameter and click **Save**.
3. Now, if your user has the **PIM Manager** role, you can edit the product directly while it is in the `Approved` state.
4. Try assigning a user with the **Operator** role (they are blocked from approving or bypassing locks in all configurations).

---

## 📡 Tier 5: Channel Feeds & Mapping Export

In this tier, we will configure a feed profile to export approved product specifications to external marketplaces.

### Step 5.1: Create an Export Profile
1. Go to **Sales > Configuration > Products > PIM Export Profiles**.
2. Click **New**.
3. Set **Profile Name** to `Shopify Tools Feed`.
4. Set **Export Format** to `CSV Format`.
5. In the **Field Mappings** tab, add lines:
   * **Line 1**:
     * **Column/Header Name**: `Title`
     * **Source Type**: `Standard Product Field`
     * **Standard Field Technical Name**: `name`
   * **Line 2**:
     * **Column/Header Name**: `Description`
     * **Source Type**: `Standard Product Field`
     * **Standard Field Technical Name**: `description_sale`
   * **Line 3**:
     * **Column/Header Name**: `Power Source`
     * **Source Type**: `Custom Attribute EAV`
     * **Custom Attribute**: `Power Source`
6. Click **Save**.

### Step 5.2: Run the Export Feed
1. Click the **Generate Feed & Download** button in the header.
2. The PIM system scans for all templates in the **Approved** stage, extracts their standard fields and custom EAV specifications, generates a CSV payload, and triggers an immediate web client download action.
