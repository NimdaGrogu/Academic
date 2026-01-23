import logging

from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# In-memory inventory database
inventory = {
    "LAPTOP001": {
        "name": "Dell Latitude 7420",
        "category": "Electronics",
        "quantity": 15,
        "min_threshold": 5,
        "price": 1200.00,
        "supplier": "Dell Technologies",
        "last_updated": "2025-01-15",
        "transactions": [
            {"date": "2025-01-10", "type": "purchase", "quantity": 20, "unit_cost": 1150.00},
            {"date": "2025-01-12", "type": "sale", "quantity": 5, "unit_price": 1200.00}
        ]
    },
    "CHAIR042": {
        "name": "Ergonomic Office Chair",
        "category": "Furniture",
        "quantity": 8,
        "min_threshold": 3,
        "price": 350.00,
        "supplier": "Office Depot",
        "last_updated": "2025-01-14",
        "transactions": [
            {"date": "2025-01-05", "type": "purchase", "quantity": 12, "unit_cost": 320.00},
            {"date": "2025-01-08", "type": "sale", "quantity": 4, "unit_price": 350.00}
        ]
    },
    "PAPER001": {
        "name": "A4 Copy Paper (500 sheets)",
        "category": "Office Supplies",
        "quantity": 2,
        "min_threshold": 10,
        "price": 8.99,
        "supplier": "Staples",
        "last_updated": "2025-01-13",
        "transactions": [
            {"date": "2025-01-01", "type": "purchase", "quantity": 50, "unit_cost": 7.50},
            {"date": "2025-01-10", "type": "sale", "quantity": 48, "unit_price": 8.99}
        ]
    },
    "MONITOR055": {
        "name": "Samsung 27\" 4K Monitor",
        "category": "Electronics",
        "quantity": 12,
        "min_threshold": 4,
        "price": 450.00,
        "supplier": "Samsung",
        "last_updated": "2025-01-16",
        "transactions": [
            {"date": "2025-01-15", "type": "purchase", "quantity": 15, "unit_cost": 400.00},
            {"date": "2025-01-16", "type": "sale", "quantity": 3, "unit_price": 450.00}
        ]
    }
}

# Create MCP server
mcp = FastMCP("InventoryManager")

# Tool: Check stock levels
@mcp.tool()
def check_stock(item_code: str) -> str:
    """Check current stock level and details for a specific item"""
    item = inventory.get(item_code)
    if not item:
        return f"Item code '{item_code}' not found in inventory."

    status_icon = "🔴" if item['quantity'] <= item['min_threshold'] else "🟡" if item['quantity'] <= item['min_threshold'] * 2 else "🟢"
    stock_status = "CRITICAL" if item['quantity'] <= item['min_threshold'] else "LOW" if item['quantity'] <= item['min_threshold'] * 2 else "GOOD"

    total_value = item['quantity'] * item['price']

    return f"""
{status_icon} Stock Report: {item['name']} ({item_code})
─────────────────────────────────────────────
Current Stock: {item['quantity']} units
Minimum Threshold: {item['min_threshold']} units
Status: {stock_status}
Unit Price: ${item['price']:.2f}
Total Value: ${total_value:.2f}
Supplier: {item['supplier']}
Last Updated: {item['last_updated']}
"""

# Tool: Add stock (purchase/restock)
@mcp.tool()
def add_stock(item_code: str, quantity: int, unit_cost: Optional[float] = None) -> str:
    """Add stock to inventory (purchase/restock operation)"""
    if item_code not in inventory:
        return f"Item code '{item_code}' not found. Use create_item() first."

    if quantity <= 0:
        return "Quantity must be greater than 0."

    item = inventory[item_code]
    old_quantity = item['quantity']
    item['quantity'] += quantity
    item['last_updated'] = datetime.now().strftime("%Y-%m-%d")

    # Record transaction
    cost = unit_cost or item['price'] * 0.85  # Default to 85% of selling price
    transaction = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": "purchase",
        "quantity": quantity,
        "unit_cost": cost
    }
    item['transactions'].append(transaction)

    return f"""
Stock Added Successfully!
─────────────────────────
Item: {item['name']} ({item_code})
Added: {quantity} units
Stock Level: {old_quantity} → {item['quantity']} units
Unit Cost: ${cost:.2f}
Total Cost: ${cost * quantity:.2f}
"""

# Tool: Remove stock (sale/usage)
@mcp.tool()
def remove_stock(item_code: str, quantity: int, unit_price: Optional[float] = None) -> str:
    """Remove stock from inventory (sale/usage operation)"""
    if item_code not in inventory:
        return f"Item code '{item_code}' not found."

    if quantity <= 0:
        return "Quantity must be greater than 0."

    item = inventory[item_code]
    if item['quantity'] < quantity:
        return f"Insufficient stock! Available: {item['quantity']}, Requested: {quantity}"

    old_quantity = item['quantity']
    item['quantity'] -= quantity
    item['last_updated'] = datetime.now().strftime("%Y-%m-%d")

    # Record transaction
    price = unit_price or item['price']
    transaction = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": "sale",
        "quantity": quantity,
        "unit_price": price
    }
    item['transactions'].append(transaction)

    # Check if stock is below threshold
    warning = ""
    if item['quantity'] <= item['min_threshold']:
        warning = f"\n WARNING: Stock below minimum threshold ({item['min_threshold']} units)!"

    return f"""
Stock Removed Successfully!
─────────────────────────
Item: {item['name']} ({item_code})
Removed: {quantity} units
Stock Level: {old_quantity} → {item['quantity']} units
Unit Price: ${price:.2f}
Total Revenue: ${price * quantity:.2f}{warning}
"""

# Tool: Get low stock alerts
@mcp.tool()
def get_low_stock_alerts() -> str:
    """Get list of items that are low on stock or below minimum threshold"""
    low_stock_items = []
    critical_items = []

    for code, item in inventory.items():
        if item['quantity'] <= item['min_threshold']:
            critical_items.append((code, item))
        elif item['quantity'] <= item['min_threshold'] * 2:
            low_stock_items.append((code, item))

    if not low_stock_items and not critical_items:
        return "All items are well-stocked!"

    alert_msg = "Stock Alerts\n" + "="*50 + "\n"

    if critical_items:
        alert_msg += "\nCRITICAL - Reorder Immediately:\n"
        for code, item in critical_items:
            alert_msg += f"  • {item['name']} ({code}): {item['quantity']} units (Min: {item['min_threshold']})\n"

    if low_stock_items:
        alert_msg += "\n🟡 LOW STOCK - Consider Reordering:\n"
        for code, item in low_stock_items:
            alert_msg += f"  • {item['name']} ({code}): {item['quantity']} units (Min: {item['min_threshold']})\n"

    return alert_msg

# Tool: Get inventory summary by category
@mcp.tool()
def get_inventory_summary(category: Optional[str] = None) -> str:
    """Get inventory summary, optionally filtered by category"""
    filtered_items = inventory.items()

    if category:
        filtered_items = [(code, item) for code, item in inventory.items()
                         if item['category'].lower() == category.lower()]
        if not filtered_items:
            return f"❌ No items found in category '{category}'"

    total_value = 0
    total_items = 0
    categories = {}

    summary = f"Inventory Summary"
    if category:
        summary += f" - {category.title()}"
    summary += "\n" + "="*60 + "\n"

    for code, item in filtered_items:
        item_value = item['quantity'] * item['price']
        total_value += item_value
        total_items += item['quantity']

        cat = item['category']
        if cat not in categories:
            categories[cat] = {'items': 0, 'value': 0, 'quantity': 0}
        categories[cat]['items'] += 1
        categories[cat]['value'] += item_value
        categories[cat]['quantity'] += item['quantity']

    # Category breakdown
    for cat, stats in categories.items():
        summary += f"\n{cat}:\n"
        summary += f"   Items: {stats['items']} types\n"
        summary += f"   Total Units: {stats['quantity']}\n"
        summary += f"   Total Value: ${stats['value']:,.2f}\n"

    summary += f"\n Grand Total: ${total_value:,.2f}"
    summary += f"\n Total Units: {total_items:,}"
    summary += f"\n Unique Items: {len(filtered_items)}"

    return summary

# Tool: Get transaction history
@mcp.tool()
def get_transaction_history(item_code: str, limit: int = 10) -> str:
    """Get recent transaction history for an item"""
    if item_code not in inventory:
        return f" Item code '{item_code}' not found."

    item = inventory[item_code]
    transactions = item['transactions']

    if not transactions:
        return f"No transaction history found for {item['name']} ({item_code})."

    # Sort by date (most recent first)
    sorted_transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
    limited_transactions = sorted_transactions[:limit]

    history = f"Transaction History: {item['name']} ({item_code})\n"
    history += "="*60 + "\n"

    for i, trans in enumerate(limited_transactions, 1):
        if trans['type'] == 'purchase':
            amount = f"${trans['unit_cost']:.2f} each"
            total = f"${trans['unit_cost'] * trans['quantity']:.2f}"
        else:
            amount = f"${trans['unit_price']:.2f} each"
            total = f"${trans['unit_price'] * trans['quantity']:.2f}"

        history += f"{i:2}. {trans['date']} | {trans['type'].title()} | "
        history += f"{trans['quantity']} units @ {amount} = {total}\n"

    if len(transactions) > limit:
        history += f"\n... and {len(transactions) - limit} more transactions"

    return history

# Tool: Create new item
@mcp.tool()
def create_item(item_code: str, name: str, category: str, initial_quantity: int,
                price: float, min_threshold: int, supplier: str) -> str:
    """Create a new item in the inventory"""
    if item_code in inventory:
        return f"Item code '{item_code}' already exists."

    if initial_quantity < 0 or price <= 0 or min_threshold < 0:
        return "Invalid values. Quantity and threshold must be non-negative, price must be positive."

    inventory[item_code] = {
        "name": name,
        "category": category,
        "quantity": initial_quantity,
        "min_threshold": min_threshold,
        "price": price,
        "supplier": supplier,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "transactions": []
    }

    # Add initial stock transaction if quantity > 0
    if initial_quantity > 0:
        inventory[item_code]['transactions'].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "purchase",
            "quantity": initial_quantity,
            "unit_cost": price * 0.8  # Assume 80% cost ratio
        })

    return f"""
New Item Created Successfully!
─────────────────────────────────
Item Code: {item_code}
Name: {name}
Category: {category}
Initial Stock: {initial_quantity} units
Price: ${price:.2f}
Min Threshold: {min_threshold} units
Supplier: {supplier}
"""

# Resource: Inventory dashboard
@mcp.resource("dashboard://inventory-overview")
def get_inventory_dashboard() -> str:
    """Get a comprehensive inventory dashboard"""
    total_items = len(inventory)
    total_value = sum(item['quantity'] * item['price'] for item in inventory.values())
    low_stock_count = sum(1 for item in inventory.values() if item['quantity'] <= item['min_threshold'])

    categories = {}
    for item in inventory.values():
        cat = item['category']
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1

    dashboard = f"""
INVENTORY DASHBOARD
{'='*50}

Quick Stats:
  └─ Total Items: {total_items} types
  └─ Total Value: ${total_value:,.2f}
  └─ Low Stock Alerts: {low_stock_count} items

Categories:
"""

    for cat, count in categories.items():
        dashboard += f"  └─ {cat}: {count} items\n"

    dashboard += f"""
Action Required:
  └─ Items needing reorder: {low_stock_count}
  └─ Use get_low_stock_alerts() for details

Recent Activity:
  └─ Use get_transaction_history() for item details
"""

    return dashboard

# Resource: Supplier contact info
@mcp.resource("contacts://suppliers")
def get_supplier_contacts() -> str:
    """Get supplier contact information"""
    suppliers = set(item['supplier'] for item in inventory.values())

    # Mock contact info (in real app, this would be from a database)
    contact_info = {
        "Dell Technologies": "1-800-DELL-TECH | orders@dell.com",
        "Office Depot": "1-800-OFFICE | business@officedepot.com",
        "Staples": "1-800-STAPLES | supplies@staples.com",
        "Samsung": "1-800-SAMSUNG | b2b@samsung.com"
    }

    contacts = "Supplier Contact Directory\n" + "="*40 + "\n"

    for supplier in sorted(suppliers):
        contacts += f"\n{supplier}\n"
        contacts += f"   {contact_info.get(supplier, ' Contact info not available')}\n"

    return contacts

if __name__ == "__main__":
    print("Server Started..")
    mcp.run()