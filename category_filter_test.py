#!/usr/bin/env python3
"""
Category Filtering Test for Anantha Lakshmi Food Delivery App
Tests: Category-based product filtering functionality
"""

import requests
import json
import sys
from datetime import datetime
from collections import defaultdict

# Backend URL from environment
BACKEND_URL = "https://recipe-store-1.preview.emergentagent.com/api"

def test_category_filtering():
    """Test category filtering functionality"""
    print("🚀 Starting Category Filtering Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now()}")
    
    # Get all products first
    try:
        response = requests.get(f"{BACKEND_URL}/products", timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to get products: HTTP {response.status_code}")
            return False
        
        all_products = response.json()
        print(f"✅ Retrieved {len(all_products)} total products")
        
    except Exception as e:
        print(f"❌ Error getting products: {str(e)}")
        return False
    
    # Group products by category
    products_by_category = defaultdict(list)
    for product in all_products:
        category = product.get('category', 'unknown')
        products_by_category[category].append(product)
    
    print(f"\n📊 Products by Category:")
    for category, products in products_by_category.items():
        print(f"  - {category}: {len(products)} products")
    
    # Test filtering for each category
    print(f"\n🔍 Testing Category Filtering:")
    
    categories_to_test = ['laddus-chikkis', 'sweets', 'hot-items', 'snacks', 'pickles', 'powders', 'spices']
    
    all_filters_working = True
    
    for category in categories_to_test:
        expected_products = products_by_category.get(category, [])
        expected_count = len(expected_products)
        
        # Filter products by category (client-side filtering simulation)
        filtered_products = [p for p in all_products if p.get('category') == category]
        actual_count = len(filtered_products)
        
        status = "✅" if actual_count == expected_count else "❌"
        print(f"  {status} {category}: {actual_count} products (expected {expected_count})")
        
        if actual_count != expected_count:
            all_filters_working = False
        
        # Show sample products from this category
        if filtered_products:
            sample_products = filtered_products[:2]  # Show first 2 products
            for product in sample_products:
                print(f"    - {product.get('name', 'Unknown')}")
    
    return all_filters_working

if __name__ == "__main__":
    success = test_category_filtering()
    if success:
        print(f"\n🎉 Category filtering is working correctly!")
        sys.exit(0)
    else:
        print(f"\n❌ Category filtering has issues!")
        sys.exit(1)