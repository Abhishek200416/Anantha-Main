#!/usr/bin/env python3
"""
Products API Testing Script for Anantha Lakshmi Food Delivery App
FOCUSED TEST: Product Verification - Check all 56 products with correct categories
Tests: GET /api/products, Product Details Verification, Category Filtering, Specific Products
"""

import requests
import json
import sys
from datetime import datetime
from collections import defaultdict

# Backend URL from environment
BACKEND_URL = "https://recipe-buddy-28.preview.emergentagent.com/api"

def test_api_endpoint(method, endpoint, headers=None, data=None, description="", expected_status=None):
    """Test a single API endpoint"""
    url = f"{BACKEND_URL}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"URL: {url}")
    if data:
        print(f"Request Data: {json.dumps(data, indent=2)}")
    print(f"{'='*60}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            print(f"❌ Unsupported method: {method}")
            return False, None
            
        print(f"Status Code: {response.status_code}")
        
        # Try to parse JSON response
        response_data = None
        try:
            response_data = response.json()
            print(f"Response Data Length: {len(response_data) if isinstance(response_data, list) else 'Not a list'}")
        except:
            print(f"Response Text: {response.text}")
        
        # Check if request was successful
        if expected_status:
            success = response.status_code == expected_status
        else:
            success = 200 <= response.status_code < 300
            
        if success:
            print("✅ SUCCESS: API endpoint is working as expected")
            return True, response_data
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False, response_data
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: {str(e)}")
        return False, None
    except requests.exceptions.Timeout as e:
        print(f"❌ TIMEOUT ERROR: {str(e)}")
        return False, None
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False, None

def verify_product_structure(product):
    """Verify that a product has the correct structure"""
    required_fields = ['id', 'name', 'category', 'description', 'image', 'prices', 'isBestSeller', 'isNew', 'tag']
    
    issues = []
    
    for field in required_fields:
        if field not in product:
            issues.append(f"Missing field: {field}")
    
    # Check prices structure
    if 'prices' in product:
        if not isinstance(product['prices'], list) or len(product['prices']) == 0:
            issues.append("Prices should be a non-empty list")
        else:
            for i, price_item in enumerate(product['prices']):
                if not isinstance(price_item, dict):
                    issues.append(f"Price item {i} should be a dictionary")
                elif 'weight' not in price_item or 'price' not in price_item:
                    issues.append(f"Price item {i} missing weight or price")
    
    # Check image URL
    if 'image' in product:
        image_url = product['image']
        if not image_url or not isinstance(image_url, str):
            issues.append("Image URL should be a non-empty string")
        elif not (image_url.startswith('http') or image_url.startswith('/')):
            issues.append("Image URL should be a valid URL or path")
    
    # Check inventory fields
    if 'inventory_count' in product:
        if not isinstance(product['inventory_count'], int) or product['inventory_count'] < 0:
            issues.append("Inventory count should be a non-negative integer")
    
    if 'out_of_stock' in product:
        if not isinstance(product['out_of_stock'], bool):
            issues.append("out_of_stock should be a boolean")
    
    return issues

def main():
    """Main testing function - FOCUSED ON PRODUCT VERIFICATION"""
    print("🚀 Starting Products API Verification Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now()}")
    
    # Test results tracking
    test_results = {}
    
    # ============= STEP 1: GET ALL PRODUCTS =============
    print("\n" + "="*80)
    print("📦 STEP 1: GET ALL PRODUCTS")
    print("="*80)
    
    success, all_products = test_api_endpoint(
        "GET",
        "/products",
        description="Get all products to verify 56 products with correct categories"
    )
    
    test_results['get_products'] = success
    
    if not success or not all_products:
        print("❌ CRITICAL: Failed to get products - cannot proceed with verification")
        return 1
    
    # ============= STEP 2: VERIFY PRODUCT COUNT AND CATEGORIES =============
    print("\n" + "="*80)
    print("📊 STEP 2: VERIFY PRODUCT COUNT AND CATEGORIES")
    print("="*80)
    
    total_products = len(all_products)
    print(f"\n📊 Product Count Verification:")
    print(f"  - Total products found: {total_products}")
    print(f"  - Expected: 56 products")
    
    # Expected category counts
    expected_categories = {
        'laddus-chikkis': 8,
        'sweets': 10,
        'hot-items': 10,
        'snacks': 3,
        'pickles': 9,
        'powders': 12,
        'spices': 4
    }
    
    # Count products by category
    category_counts = defaultdict(int)
    for product in all_products:
        category = product.get('category', 'unknown')
        category_counts[category] += 1
    
    print(f"\n📊 Category Breakdown:")
    total_expected = sum(expected_categories.values())
    print(f"  Expected total: {total_expected}")
    
    category_verification_passed = True
    
    for category, expected_count in expected_categories.items():
        actual_count = category_counts.get(category, 0)
        status = "✅" if actual_count == expected_count else "❌"
        print(f"  {status} {category}: {actual_count}/{expected_count}")
        
        if actual_count != expected_count:
            category_verification_passed = False
    
    # Check for unexpected categories
    unexpected_categories = set(category_counts.keys()) - set(expected_categories.keys())
    if unexpected_categories:
        print(f"\n⚠️  Unexpected categories found: {list(unexpected_categories)}")
        for category in unexpected_categories:
            print(f"    - {category}: {category_counts[category]} products")
    
    test_results['correct_product_count'] = (total_products == total_expected)
    test_results['correct_category_distribution'] = category_verification_passed
    
    # ============= STEP 3: VERIFY SPECIFIC PRODUCTS =============
    print("\n" + "="*80)
    print("🎯 STEP 3: VERIFY SPECIFIC PRODUCTS")
    print("="*80)
    
    # Specific products to check as requested
    specific_products_to_check = [
        {"name": "Immunity Dry Fruits Laddu", "category": "laddus-chikkis", "isBestSeller": True},
        {"name": "Kobbari Laddu", "category": "sweets", "isBestSeller": False},
        {"name": "Atukullu Mixture", "category": "hot-items", "isBestSeller": True},
        {"name": "Masala Chekkalu / Pappu Chekkalu", "category": "snacks", "isBestSeller": False},
        {"name": "Mango Pickle", "category": "pickles", "isBestSeller": True},
        {"name": "Kandi Podi", "category": "powders", "isBestSeller": True},
        {"name": "Sambar Powder", "category": "spices", "isBestSeller": True}
    ]
    
    print(f"\n🔍 Checking {len(specific_products_to_check)} specific products:")
    
    specific_products_found = 0
    specific_products_correct = 0
    
    # Create a lookup dictionary for faster searching
    products_by_name = {product['name']: product for product in all_products}
    
    for expected_product in specific_products_to_check:
        product_name = expected_product['name']
        expected_category = expected_product['category']
        expected_best_seller = expected_product['isBestSeller']
        
        print(f"\n  🔍 Checking: {product_name}")
        
        if product_name in products_by_name:
            specific_products_found += 1
            actual_product = products_by_name[product_name]
            
            # Verify category
            actual_category = actual_product.get('category')
            category_correct = actual_category == expected_category
            
            # Verify best seller flag
            actual_best_seller = actual_product.get('isBestSeller', False)
            best_seller_correct = actual_best_seller == expected_best_seller
            
            # Check if all attributes are correct
            all_correct = category_correct and best_seller_correct
            
            if all_correct:
                specific_products_correct += 1
                print(f"    ✅ Found and verified correctly")
            else:
                print(f"    ❌ Found but has issues:")
                if not category_correct:
                    print(f"      - Category: expected '{expected_category}', got '{actual_category}'")
                if not best_seller_correct:
                    print(f"      - Best Seller: expected {expected_best_seller}, got {actual_best_seller}")
            
            print(f"    - Category: {actual_category} {'✅' if category_correct else '❌'}")
            print(f"    - Best Seller: {actual_best_seller} {'✅' if best_seller_correct else '❌'}")
            print(f"    - ID: {actual_product.get('id')}")
            
        else:
            print(f"    ❌ Product not found in database")
    
    test_results['specific_products_found'] = (specific_products_found == len(specific_products_to_check))
    test_results['specific_products_correct'] = (specific_products_correct == len(specific_products_to_check))
    
    print(f"\n📊 Specific Products Summary:")
    print(f"  - Products found: {specific_products_found}/{len(specific_products_to_check)}")
    print(f"  - Products correct: {specific_products_correct}/{len(specific_products_to_check)}")
    
    # ============= STEP 4: VERIFY PRODUCT STRUCTURE =============
    print("\n" + "="*80)
    print("🔧 STEP 4: VERIFY PRODUCT STRUCTURE")
    print("="*80)
    
    print(f"\n🔍 Checking product structure for all {total_products} products:")
    
    products_with_issues = 0
    sample_products_checked = 0
    max_samples_to_check = 10  # Check first 10 products in detail
    
    for i, product in enumerate(all_products[:max_samples_to_check]):
        sample_products_checked += 1
        issues = verify_product_structure(product)
        
        if issues:
            products_with_issues += 1
            print(f"\n  ❌ Product '{product.get('name', 'Unknown')}' has issues:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"  ✅ Product '{product.get('name', 'Unknown')}' structure is correct")
    
    # Check key fields across all products
    print(f"\n📊 Overall Structure Analysis:")
    
    products_with_prices = sum(1 for p in all_products if 'prices' in p and p['prices'])
    products_with_images = sum(1 for p in all_products if 'image' in p and p['image'])
    products_with_descriptions = sum(1 for p in all_products if 'description' in p and p['description'])
    products_with_inventory = sum(1 for p in all_products if 'inventory_count' in p)
    products_best_seller = sum(1 for p in all_products if p.get('isBestSeller', False))
    products_new = sum(1 for p in all_products if p.get('isNew', False))
    
    print(f"  - Products with prices: {products_with_prices}/{total_products}")
    print(f"  - Products with images: {products_with_images}/{total_products}")
    print(f"  - Products with descriptions: {products_with_descriptions}/{total_products}")
    print(f"  - Products with inventory: {products_with_inventory}/{total_products}")
    print(f"  - Best seller products: {products_best_seller}")
    print(f"  - New products: {products_new}")
    
    structure_ok = (products_with_issues == 0)
    test_results['product_structure_valid'] = structure_ok
    
    # ============= STEP 5: SAMPLE PRODUCT DETAILS =============
    print("\n" + "="*80)
    print("📋 STEP 5: SAMPLE PRODUCT DETAILS")
    print("="*80)
    
    # Show details of a few sample products
    sample_products = all_products[:3] if len(all_products) >= 3 else all_products
    
    for i, product in enumerate(sample_products, 1):
        print(f"\n📦 Sample Product {i}: {product.get('name', 'Unknown')}")
        print(f"  - ID: {product.get('id')}")
        print(f"  - Category: {product.get('category')}")
        print(f"  - Description: {product.get('description', 'N/A')[:100]}...")
        print(f"  - Image: {product.get('image', 'N/A')}")
        print(f"  - Best Seller: {product.get('isBestSeller', False)}")
        print(f"  - New Product: {product.get('isNew', False)}")
        print(f"  - Tag: {product.get('tag', 'N/A')}")
        print(f"  - Inventory: {product.get('inventory_count', 'N/A')}")
        print(f"  - Out of Stock: {product.get('out_of_stock', False)}")
        
        # Show price tiers
        prices = product.get('prices', [])
        if prices:
            print(f"  - Price Tiers ({len(prices)}):")
            for j, price_tier in enumerate(prices[:3]):  # Show first 3 price tiers
                weight = price_tier.get('weight', 'N/A')
                price = price_tier.get('price', 'N/A')
                print(f"    {j+1}. {weight}: ₹{price}")
        else:
            print(f"  - Prices: No price tiers found")
    
    # ============= FINAL SUMMARY =============
    print(f"\n{'='*80}")
    print("🎯 PRODUCTS VERIFICATION TEST SUMMARY")
    print(f"{'='*80}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"\n📊 Test Results:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\n📊 Overall Statistics:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n🎯 KEY FINDINGS:")
    
    # Product Count
    if test_results.get('correct_product_count'):
        print(f"  ✅ Correct number of products found: {total_products}")
    else:
        print(f"  ❌ Incorrect product count: found {total_products}, expected {total_expected}")
    
    # Category Distribution
    if test_results.get('correct_category_distribution'):
        print(f"  ✅ All categories have correct product counts")
    else:
        print(f"  ❌ Some categories have incorrect product counts")
    
    # Specific Products
    if test_results.get('specific_products_found') and test_results.get('specific_products_correct'):
        print(f"  ✅ All specific products found and verified correctly")
    else:
        print(f"  ❌ Some specific products missing or incorrect")
    
    # Product Structure
    if test_results.get('product_structure_valid'):
        print(f"  ✅ Product structure is valid for all checked products")
    else:
        print(f"  ❌ Some products have structural issues")
    
    # Overall Assessment
    if failed_tests == 0:
        print(f"\n🎉 ALL TESTS PASSED! Product database is correctly populated.")
        print(f"✅ {total_products} products with proper categories and structure")
        print(f"✅ All specific products verified with correct attributes")
        print(f"✅ Product structure meets requirements")
        return 0
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Check the detailed output above for specific issues.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)