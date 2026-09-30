// SmartGrocery Mock Database & Application Logic

const GROCERY_PRODUCTS = [
  {
    id: "p1",
    name: "Organic Whole Milk (1 Gallon)",
    category: "dairy",
    emoji: "🥛",
    unit: "1 gal ($0.04/oz)",
    prices: {
      walmart: 3.98,
      amazon: 4.49,
      instacart: 4.89,
      target: 4.19,
      kroger: 4.09,
      wholefoods: 5.29
    }
  },
  {
    id: "p2",
    name: "Large Grade A Eggs (12 Count)",
    category: "dairy",
    emoji: "🥚",
    unit: "12 ct ($0.23/egg)",
    prices: {
      walmart: 2.78,
      amazon: 3.19,
      instacart: 3.49,
      target: 2.99,
      kroger: 2.89,
      wholefoods: 4.19
    }
  },
  {
    id: "p3",
    name: "Hass Avocados (4 Pack)",
    category: "produce",
    emoji: "🥑",
    unit: "4 ct ($0.85/ea)",
    prices: {
      walmart: 3.42,
      amazon: 3.99,
      instacart: 4.29,
      target: 3.69,
      kroger: 3.49,
      wholefoods: 4.99
    }
  },
  {
    id: "p4",
    name: "Boneless Skinless Chicken Breast (2 lbs)",
    category: "meat",
    emoji: "🍗",
    unit: "2 lbs ($3.99/lb)",
    prices: {
      walmart: 7.98,
      amazon: 8.99,
      instacart: 9.49,
      target: 8.49,
      kroger: 7.99,
      wholefoods: 11.99
    }
  },
  {
    id: "p5",
    name: "Organic Bananas (3 lbs)",
    category: "produce",
    emoji: "🍌",
    unit: "3 lbs ($0.58/lb)",
    prices: {
      walmart: 1.74,
      amazon: 1.99,
      instacart: 2.29,
      target: 1.89,
      kroger: 1.79,
      wholefoods: 2.49
    }
  },
  {
    id: "p6",
    name: "Extra Virgin Olive Oil (16.9 oz)",
    category: "pantry",
    emoji: "🫒",
    unit: "16.9 fl oz ($0.47/oz)",
    prices: {
      walmart: 7.92,
      amazon: 8.49,
      instacart: 9.19,
      target: 8.29,
      kroger: 8.19,
      wholefoods: 10.49
    }
  },
  {
    id: "p7",
    name: "Cold Brew Coffee Concentrate (32 oz)",
    category: "beverages",
    emoji: "☕",
    unit: "32 fl oz ($0.23/oz)",
    prices: {
      walmart: 7.48,
      amazon: 7.99,
      instacart: 8.79,
      target: 7.69,
      kroger: 7.59,
      wholefoods: 9.29
    }
  },
  {
    id: "p8",
    name: "Sourdough Artisanal Bread (24 oz)",
    category: "pantry",
    emoji: "🍞",
    unit: "24 oz ($0.18/oz)",
    prices: {
      walmart: 4.28,
      amazon: 4.79,
      instacart: 5.19,
      target: 4.49,
      kroger: 4.39,
      wholefoods: 5.99
    }
  }
];

const STORE_DELIVERY_FEES = {
  walmart: 3.95,
  amazon: 2.99,
  instacart: 5.99,
  target: 4.99,
  kroger: 3.99,
  wholefoods: 4.99
};

const STORE_NAMES = {
  walmart: "Walmart Grocery",
  amazon: "Amazon Fresh",
  instacart: "Instacart Express",
  target: "Target Circle",
  kroger: "Kroger Delivery",
  wholefoods: "Whole Foods Market"
};

let cart = [];
let currentCategory = 'all';

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  renderProducts(GROCERY_PRODUCTS);

  document.getElementById("searchInput").addEventListener("input", (e) => {
    const val = e.target.value.toLowerCase().trim();
    document.getElementById("clearBtn").style.display = val ? "block" : "none";
    filterProducts();
  });
});

function filterCategory(cat, btn) {
  currentCategory = cat;
  document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
  btn.classList.add("active");
  filterProducts();
}

function clearSearch() {
  const input = document.getElementById("searchInput");
  input.value = "";
  document.getElementById("clearBtn").style.display = "none";
  filterProducts();
}

function filterProducts() {
  const query = document.getElementById("searchInput").value.toLowerCase().trim();
  const filtered = GROCERY_PRODUCTS.filter(p => {
    const matchesCat = currentCategory === 'all' || p.category === currentCategory;
    const matchesQuery = !query || p.name.toLowerCase().includes(query) || p.category.toLowerCase().includes(query);
    return matchesCat && matchesQuery;
  });

  renderProducts(filtered);
}

function renderProducts(products) {
  const grid = document.getElementById("productsGrid");
  grid.innerHTML = "";

  if (products.length === 0) {
    grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">No items found matching your search. Try searching for "Milk", "Eggs", or "Avocado".</div>`;
    return;
  }

  products.forEach(p => {
    // Find lowest price store
    const storeEntries = Object.entries(p.prices);
    storeEntries.sort((a, b) => a[1] - b[1]);
    const cheapestStore = storeEntries[0][0];
    const cheapestPrice = storeEntries[0][1];

    const isCarted = cart.includes(p.id);

    const card = document.createElement("div");
    card.className = "product-card";

    let storeRowsHtml = "";
    storeEntries.forEach(([storeKey, price]) => {
      const isCheapest = storeKey === cheapestStore;
      storeRowsHtml += `
        <div class="store-price-row ${isCheapest ? 'cheapest' : ''}">
          <span class="store-name">
            ${STORE_NAMES[storeKey]}
            ${isCheapest ? '<span class="lowest-badge">Lowest Price</span>' : ''}
          </span>
          <span class="price-val">$${price.toFixed(2)}</span>
        </div>
      `;
    });

    card.innerHTML = `
      <div class="product-top">
        <div class="product-img">${p.emoji}</div>
        <div class="product-meta">
          <h4>${p.name}</h4>
          <span class="product-unit">${p.unit}</span>
          <div><span class="category-tag">${p.category}</span></div>
        </div>
      </div>

      <div class="store-prices-list">
        ${storeRowsHtml}
      </div>

      <div class="card-actions">
        <button class="add-cart-btn" onclick="toggleCart('${p.id}')">
          ${isCarted ? '✓ In Optimizer Basket' : '+ Add to Optimizer Basket'}
        </button>
      </div>
    `;

    grid.appendChild(card);
  });
}

function toggleCart(productId) {
  const idx = cart.indexOf(productId);
  if (idx > -1) {
    cart.splice(idx, 1);
  } else {
    cart.push(productId);
  }

  document.getElementById("cartCount").textContent = cart.length;
  filterProducts();
}

function toggleLocationModal() {
  document.getElementById("locationModal").classList.toggle("open");
}

function selectPresetLoc(zip, name) {
  document.getElementById("zipInput").value = zip;
  document.getElementById("currentLocationText").textContent = name;
  toggleLocationModal();
}

function saveLocation() {
  const zip = document.getElementById("zipInput").value.trim() || "98101";
  document.getElementById("currentLocationText").textContent = `Zip Code ${zip}`;
  toggleLocationModal();
}

function openOptimizerModal() {
  if (cart.length === 0) {
    alert("Please add at least 1 item to your Optimizer Basket first!");
    return;
  }

  const resultsDiv = document.getElementById("optimizerResults");
  const cartItems = GROCERY_PRODUCTS.filter(p => cart.includes(p.id));

  // Calculate single store totals
  const storeTotals = {};
  Object.keys(STORE_NAMES).forEach(s => {
    let itemsTotal = 0;
    cartItems.forEach(item => {
      itemsTotal += item.prices[s];
    });
    const fee = STORE_DELIVERY_FEES[s];
    storeTotals[s] = {
      itemsTotal: itemsTotal,
      fee: fee,
      grandTotal: itemsTotal + fee
    };
  });

  // Sort by grand total
  const sortedStores = Object.entries(storeTotals).sort((a, b) => a[1].grandTotal - b[1].grandTotal);
  const bestSingleStore = sortedStores[0];

  // Calculate absolute cheapest split total (buying each item at its absolute cheapest store)
  let splitItemsTotal = 0;
  cartItems.forEach(item => {
    const minPrice = Math.min(...Object.values(item.prices));
    splitItemsTotal += minPrice;
  });

  resultsDiv.innerHTML = `
    <div style="margin-bottom: 20px;">
      <p style="color: #64748b; font-size: 14px;">Comparing basket cost for <strong>${cartItems.length} items</strong> including delivery & service fees:</p>
    </div>

    <div class="opt-option best">
      <div class="opt-title">
        <span>🏆 Option 1: Single Store Best Value (${STORE_NAMES[bestSingleStore[0]]})</span>
        <span class="opt-cost">$${bestSingleStore[1].grandTotal.toFixed(2)}</span>
      </div>
      <p style="font-size: 13px; color: #059669; margin-top: 6px;">
        Subtotal: $${bestSingleStore[1].itemsTotal.toFixed(2)} + Delivery Fee: $${bestSingleStore[1].fee.toFixed(2)}
      </p>
    </div>

    <div class="opt-option">
      <div class="opt-title">
        <span>🏪 Option 2: Split Store (Cheapest item per store)</span>
        <span class="opt-cost">$${splitItemsTotal.toFixed(2)} (items only)</span>
      </div>
      <p style="font-size: 13px; color: #64748b; margin-top: 6px;">
        Items subtotal when buying each product from its lowest price platform. (Note: Multiple delivery fees may apply).
      </p>
    </div>

    <h4 style="margin: 20px 0 10px 0; font-size: 15px;">Single Store Comparison Matrix:</h4>
    <div style="display: flex; flex-direction: column; gap: 8px;">
      ${sortedStores.map(([sKey, data]) => `
        <div style="display: flex; justify-content: space-between; padding: 10px 14px; background: #f8fafc; border-radius: 8px; font-size: 14px;">
          <span>${STORE_NAMES[sKey]}</span>
          <span style="font-weight: 700;">$${data.grandTotal.toFixed(2)} <span style="font-size: 12px; font-weight: normal; color: #64748b;">($${data.itemsTotal.toFixed(2)} + $${data.fee.toFixed(2)} fee)</span></span>
        </div>
      `).join('')}
    </div>
  `;

  document.getElementById("optimizerModal").classList.add("open");
}

function closeOptimizerModal() {
  document.getElementById("optimizerModal").classList.remove("open");
}
