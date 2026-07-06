# Test Suite & Coverage Guide

This document describes the testing strategy, test coverage, and execution instructions for the Custom Product Attribution System.

---

## 1. Testing Strategy

The test suite is built on Odoo's testing framework, specifically using `HttpCase` to allow full lifecycle transactions (including UI simulations, EAV writebacks, and OWL assets verification).

Tests are located in [tests/test_product_attribution.py](file:///c:/Users/nonna/Dev/repository/odoo_product_attribution_system/tests/test_product_attribution.py) and execute post-installation (`post_install`) to verify interactions with standard Odoo features.

---

## 2. Test Coverage Details

The test suite consists of **61 specialized tests** divided into distinct tiers:

### Tier 1: Happy Paths & Feature Coverage
These tests verify core functional requirements under normal conditions:
* **Category Attribute Inheritance (Tests 1-5)**: Verifies direct category attributes, parent inheritance, multi-level hierarchy aggregation (5 levels deep), overlapping attribute exclusion, and empty categories.
* **EAV Database Store (Tests 6-11)**: Verifies correct storage, formatting, and retrieval for each data type:
  * Text, Integer, Float, Date, Boolean, Selection.
* **Database & View Synchronizations (Tests 12-16)**: Verifies template value synchronization when categories are assigned, changed, or cleared. Ensures data is preserved in the database (even when hidden in views).
* **View & UI Layer Verification (Tests 17-18)**: Simulates Odoo list grid domains to ensure only active inherited attributes appear to the user.
* **OWL Widget Asset Registration (Test 19)**: Verifies that the widget JavaScript bundle is registered under Odoo's registry (`dynamic_attribute_value`).
* **Widget Field Type Renderings (Tests 20-26)**: Asserts type mappings and widget writeback logic for all six types.
* **Search View Filtering (Tests 27-30)**: Asserts filtering of products using name and value fields under EAV layouts.

### Tier 2: Boundary Value Analysis (BVA) & Negative Testing
These tests verify that the system handles edge cases and invalid states safely:
* **Cyclic Parent Detection (Test 31)**: Asserts that setting a category parent to itself or creating loops throws validation errors.
* **Hierarchy Transitions (Tests 32-34)**: Tests dynamic re-parenting, uncoupling, and active/archived categories.
* **Null & Extreme Values (Tests 35-39)**: Tests null entries, extremely large strings (10,000+ chars), integer boundaries (32-bit limits), leap days, and far-future dates (e.g. `9999-12-31`).
* **Input Out-of-Bounds Validation (Tests 40-41)**: Asserts that selection values from different attributes cannot be linked and that duplicate template values are prevented.
* **Transition States (Tests 42-45)**: Asserts transitions between disjoint categories (no shared attributes) and parent-child switches.
* **Concurrent/Rapid updates (Test 46)**: Simulates rapid category changing to prevent transactional race conditions.
* **Dynamic Modifiers (Tests 47-48)**: Verifies adding or deleting attributes on a category immediately synchronizes active product records.
* **Data Sanitization & Fallbacks (Tests 49-53)**: Verifies writing invalid formats (e.g. string into integer or float EAV fields) throws type errors or is sanitized.
* **Fuzzy & Wildcard Searches (Tests 54-57)**: Verifies special characters, wildcards, and non-existent queries are handled gracefully.
* **Product Configurator Rules (Tests 75-78)**: Verifies the behavior of conditional rules:
  * `test_75` checks that trigger conditions dynamically hide target attributes (`is_visible` evaluations).
  * `test_76` checks that trigger conditions dynamically disable target attributes (`is_readonly` evaluations).
  * `test_77` checks that trigger conditions dynamically set target values (`set_value` actions).
  * `test_78` checks set rule validation constraints (preventing duplicate or invalid attribute assignments in rules).

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
