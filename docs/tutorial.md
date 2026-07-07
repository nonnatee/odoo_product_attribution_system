# 3-Tiers (Evolved to 4-Tiers) Configuration Tutorial

This tutorial provides a hands-on walkthrough to configure custom product attributes, propagate inheritance trees, manage data completeness quality, attach digital assets, and generate multi-channel export feeds.

---

## 🛠️ Prerequisites
* Ensure the **Custom Product Attribution System** module is installed.
* Ensure you are logged in as an Administrator or have PIM Manager access.

---

## 📂 Tier 1: Basic EAV Attributes & Attribute Sets

In this tier, you will define custom specifications and bundle them into a reusable group with defaults and validation constraints.

### Step 1: Create Custom Attributes
1. Go to **Sales > Configuration > Products > Attributes** (or Inventory > Configuration > Products > Attributes).
2. Click **New**.
3. Create the first attribute:
   * **Attribute Name**: `Warranty Period`
   * **Value Type**: `Integer`
   * Click **Save**.
4. Click **New** again to create the second attribute:
   * **Attribute Name**: `Eco Certification`
   * **Value Type**: `Selection`
   * In the **Attribute Values** tab, click **Add a line** and create three options: `RoHS`, `CE`, and `FCC`.
   * Click **Save**.

### Step 2: Build an Attribute Set with Defaults & Rules
1. Go to **Sales > Configuration > Products > Attribute Sets**.
2. Click **New**.
3. Set **Name** to `Device Specifications`.
4. In the **Attributes** list grid, add lines:
   * **Warranty Period**:
     * Set **Default Integer Value** to `12` (representing 12 months).
     * Leave **Required** unchecked.
   * **Eco Certification**:
     * Toggle the **Required** checkbox on (making this field mandatory for data completeness).
5. Click **Save**.

---

## 🌳 Tier 2: Category Inheritance & Channel Sync

In this tier, you will link your specification set to the product category tree and enable auto-sync links to external sales channels.

### Step 1: Configure Category Propagation & Channel Synchronization
1. Go to **Sales > Configuration > Products > Product Categories**.
2. Click **New**.
3. Configure the category:
   * **Category Name**: `Smart Electronics`
   * **Parent Category**: `All` (or standard parent)
   * **Attribute Sets**: Add `Device Specifications`.
4. In the **Category Channel Synchronization** section:
   * Check **Sync to POS** (automatically creates/links a matching Point of Sale category).
   * Check **Sync to eCommerce** (automatically creates/links a matching Website public category).
5. Click **Save**.

### Step 2: Assign Product and Verify Synchronization
1. Go to **Sales > Products > Products** and click **New**.
2. Set **Product Name** to `Smartwatch V1`.
3. Set **Product Category** to `Smart Electronics`.
4. Click **Save**.
5. **Verify sync**:
   * Inspect the fields: the mapped Point of Sale Category (`pos_categ_id`) and website Public Categories (`public_categ_ids`) are automatically mapped to match the synchronization.

---

## 📈 Tier 3: PIM Lifecycle, Completeness, & DAM

In this tier, you will enrich the product data, observe completeness score constraints, upload manuals, and lock the catalog record.

### Step 1: Track the Completeness Score
1. Open the form for `Smartwatch V1`.
2. Notice the **Completeness Score** indicator in the top-right header reads `40%`. This is because:
   * Core fields Name and Category are filled.
   * Core fields Sales Description and Main Image are empty.
   * The required EAV specification `Eco Certification` is empty.
3. Edit the product:
   * Add a **Sales Description** (e.g., "Feature-rich smartwatch with health monitoring").
   * Upload a **Product Image**.
4. Navigate to the **Specifications** tab:
   * Observe `Warranty Period` is pre-filled with the default value `12`.
   * Set `Eco Certification` to `RoHS`.
5. Click **Save**.
6. The **Completeness Score** now updates to **100%**.

### Step 2: Manage Digital Attachments (DAM)
1. Go to the **Documents & Assets** tab on `Smartwatch V1`.
2. Click **Add a line**:
   * **Asset Title**: `Smartwatch V1 User Guide`
   * **Asset Type**: Select `User Manual`.
   * **File Attachment**: Upload a PDF guide file.
3. Click **Save**.

### Step 3: Lifecycle Transition & Approval Locking
1. In the product form header, click **Start Enriching** (transitions stage to `Enriching`).
2. Click **Approve Product** (transitions stage to `Approved`).
3. Observe:
   * The **Approved** success ribbon displays on the template.
   * Try to edit the product name or specifications—Odoo raises a **Validation Error** stating the record is locked.
4. To modify again, click **Reset to Draft** or **Start Enriching** in the header.

### Step 4: Test Lock Bypass and User Roles
1. Go to **Sales/Inventory > Configuration > Products > PIM Settings**.
2. Check the **Allow Lock Bypass** parameter and click **Save**.
3. Now, if your user has the **PIM Manager** role, you can edit the product `Smartwatch V1` directly while it is in the `Approved` state.
4. Try assigning a user with the **Operator** role (they are blocked from approving or bypassing locks in all configurations).

---

## 📡 Tier 4: Channel Feeds & Mapping Export

In this tier, you will configure a feed profile to export approved product specifications to external marketplaces.

### Step 1: Create an Export Profile
1. Go to **Sales > Configuration > Products > PIM Export Profiles**.
2. Click **New**.
3. Set **Profile Name** to `Shopify Apparel Feed`.
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
     * **Column/Header Name**: `Certification`
     * **Source Type**: `Custom Attribute EAV`
     * **Custom Attribute**: `Eco Certification`
6. Click **Save**.

### Step 2: Run the Export Feed
1. Click the **Generate Feed & Download** button in the header.
2. The PIM system scans for all templates in the **Approved** stage, extracts their standard fields and custom EAV specifications, generates a CSV payload, and triggers an immediate web client download action.
