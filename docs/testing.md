# Test Suite & Coverage Guide

This document describes the testing strategy, test coverage, and execution instructions for the Custom Product Attribution System.

---

## 1. Testing Strategy

The test suite is built on Odoo's testing framework, specifically using `HttpCase` to allow full lifecycle transactions (including UI simulations, EAV writebacks, and OWL assets verification).

Tests are located in [tests/test_product_attribution.py](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/tests/test_product_attribution.py) and execute post-installation (`post_install`) to verify interactions with standard Odoo features.

---

## 2. Test Coverage Details

<<<<<<< Updated upstream
The test suite consists of **57 specialized tests** divided into distinct tiers:
=======
The test suite consists of **81 specialized tests** divided into distinct tiers:
>>>>>>> Stashed changes

### Tier 1: Happy Paths & Feature Coverage (Tests 1-30)
These tests verify core functional requirements under normal conditions:
* **Category Attribute Inheritance (Tests 1-5)**: Verifies direct category attributes, parent inheritance, multi-level hierarchy aggregation (5 levels deep), overlapping attribute exclusion, and empty categories.
* **EAV Database Store (Tests 6-11)**: Verifies correct storage, formatting, and retrieval for each data type: Text, Integer, Float, Date, Boolean, and Selection.
* **Database & View Synchronizations (Tests 12-16)**: Verifies template value synchronization when categories are assigned, changed, or cleared. Ensures data is preserved in the database (even when hidden in views) and checks default value initialization.
* **View & UI Layer Verification (Tests 17-18)**: Simulates Odoo list grid domains to ensure only active inherited attributes appear to the user.
* **OWL Widget Asset Registration (Test 19)**: Verifies that the widget JavaScript bundle is registered under Odoo's registry (`dynamic_attribute_value`).
* **Widget Field Type Renderings (Tests 20-26)**: Asserts type mappings, dropdown option loaders, and widget writeback logic for all six types.
* **Search View Filtering (Tests 27-30)**: Asserts filtering of products using name and value fields under EAV layouts.

### Tier 2: Boundary Value Analysis (BVA) & Negative Testing (Tests 31-60)
These tests verify that the system handles edge cases and invalid states safely:
* **Cyclic Parent Detection (Test 31)**: Asserts that setting a category parent to itself or creating loops throws validation errors.
* **Hierarchy Transitions (Tests 32-34)**: Tests dynamic re-parenting, uncoupling, and active/archived categories.
* **Null & Extreme Values (Tests 35-39)**: Tests null entries, extremely large strings (10,000+ chars), integer boundaries (32-bit limits), leap days, and far-future dates (e.g. `9999-12-31`).
* **Input Out-of-Bounds Validation (Tests 40-41)**: Asserts that selection values from different attributes cannot be linked and that duplicate template values are prevented.
* **Transition States (Tests 42-45)**: Asserts transitions between disjoint categories (no shared attributes) and parent-child switches.
* **Concurrent/Rapid updates (Test 46)**: Simulates rapid category changing to prevent transactional race conditions.
* **Dynamic Modifiers (Tests 47-48)**: Verifies adding or deleting attributes on a category immediately synchronizes active product records.
* **Data Sanitization & Fallbacks (Tests 49-53)**: Verifies writing invalid formats (e.g. string into integer or float EAV fields) throws type errors or is sanitized.
<<<<<<< Updated upstream
* **Fuzzy & Wildcard Searches (Tests 54-57)**: Verifies special characters, wildcards, and non-existent queries are handled gracefully.
=======
* **Fuzzy & Wildcard Searches (Tests 54-59)**: Verifies special characters, wildcards, case-insensitivity, and mismatched field filters.
* **Security & Access Control (Test 60)**: Asserts that non-managers are restricted from altering category attributes/sets, but are authorized to edit specifications on product templates.

### Tier 3: Cross-Feature Combinations (Tests 61-66)
These tests verify interactions between different features:
* **Value Preservation (Tests 61-62)**: Reverting category changes restores hidden value states, while category attribute deletion hides EAV values from views but keeps them in the database.
* **Advanced Searches & Batch Sync (Tests 63-66)**: Multi-level hierarchy searching, widget validation triggers, multi-company data segregation, and bulk template category reassignment.

### Tier 4: Real-World Workload Scenarios & UI Tours (Tests 67-71)
These tests simulate operational workloads and frontend actions:
* **Vertical Store Mock Scenarios (Tests 67-69)**: Clothing store apparel sizing, electronics hardware spec configs, and bookstore media catalogs.
* **Frontend Web Tours (Test 70)**: Executes Odoo frontend web tours validating widget flow, value retention, search grids, and validation popups.
* **Bulk Performance Benchmark (Test 71)**: Batch creates and updates 100 products to ensure performance remains within transaction limits.

### Tier 5: Attribute Sets & Default Values (Tests 72-74)
These tests check defaults propagation and precedence logic:
* **Propagation & priority (Tests 72-73)**: Propagating default values on creation and verifying set override priority (product set > category sub-set > parent category set).
* **Sets Union Inheritance (Test 74)**: Merging product-level sets with inherited category sets.

### Tier 6: Product Configurator & Dependency Rules (Tests 75-78)
These tests verify conditional dependency configurator behaviors:
* **Dynamic UI Hiding (Test 75)**: Asserts trigger condition hides target attributes.
* **Dynamic Disable/Readonly (Test 76)**: Asserts trigger condition makes target field readonly.
* **Forced Value Writeback (Test 77)**: Asserts trigger condition forces a preset target value.
* **Rule Constraints Validation (Test 78)**: Asserts rules validation constraints prevent invalid rule configurations (e.g., trigger/target not in set, trigger = target).

### Tier 7: Category Channel Unification (Tests 79-81)
These tests verify synchronization between standard categories, POS, and eCommerce channels:
* **POS Category Sync (Test 79)**: Asserts creating, updating, parent linking, and deleting standard categories replicates matching hierarchies in POS categories.
* **eCommerce Category Sync (Test 80)**: Asserts replicating and nesting standard categories to Website/eCommerce public categories.
* **Product Category Association Sync (Test 81)**: Asserts assigning standard categories automatically synchronizes POS and Website category links on the product record.
>>>>>>> Stashed changes

---

## 3. Test Execution Guide

To execute the entire test suite, run the Odoo command-line bin specifying the test flags.

### Prerequisites
1. Ensure the Odoo server is stopped.
2. Verify that Odoo config path and database name are correct.

### Command Execution
Run the following command in your terminal:

```bash
python3 odoo-bin -c <path_to_odoo_conf> -d <database_name> -i odoo_product_attribution_system --test-enable --stop-after-init
```

### Explaining the Flags:
* `-i odoo_product_attribution_system`: Forces installation/upgrade of the module before running.
* `--test-enable`: Directs Odoo to execute the test suite post-install.
* `--stop-after-init`: Shuts down the Odoo server immediately after tests complete (ideal for CI/CD runs).
