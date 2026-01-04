import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="Toy Shop Simulator", layout="centered")

# Pre-defined demand scenarios
SCENARIOS = [
    {
        "name": "Holiday Season",
        "narrative": "🎄 It's the holiday season! Parents are eager to buy toys for their children. Customer demand is significantly higher than usual.",
        "multiplier": 1.15
    },
    {
        "name": "Economic Recession",
        "narrative": "📉 The economy is in a downturn. Customers are being more careful with their spending, and demand for toys has decreased.",
        "multiplier": 0.85
    },
    {
        "name": "New Competitor Opens",
        "narrative": "🏪 A new toy shop just opened nearby, offering similar products. Customers now have more options, reducing your demand.",
        "multiplier": 0.90
    },
    {
        "name": "Successful Marketing Campaign",
        "narrative": "📢 Your recent marketing campaign was a hit! More customers are aware of your shop and demand has increased.",
        "multiplier": 1.10
    },
    {
        "name": "Back to School",
        "narrative": "🎒 It's back-to-school season. While demand for toys drops as parents focus on school supplies, there's still some interest in educational toys.",
        "multiplier": 0.95
    },
    {
        "name": "Local Festival",
        "narrative": "🎪 A popular local festival is happening nearby. Increased foot traffic brings more customers to your shop, boosting demand.",
        "multiplier": 1.12
    },
    {
        "name": "Product Recall in Industry",
        "narrative": "⚠️ A major competitor had a product recall, making customers more cautious. Demand for all toys has decreased temporarily.",
        "multiplier": 0.88
    },
    {
        "name": "Celebrity Endorsement",
        "narrative": "⭐ A popular celebrity mentioned your toys on social media! The buzz has significantly increased customer interest and demand.",
        "multiplier": 1.13
    },
    {
        "name": "Rainy Weekend",
        "narrative": "🌧️ It's a rainy weekend, and families are looking for indoor activities. More customers are visiting toy shops, increasing demand.",
        "multiplier": 1.08
    },
    {
        "name": "Supply Chain Issues",
        "narrative": "🚚 Industry-wide supply chain problems have made customers aware of potential shortages. This has increased demand as customers buy proactively.",
        "multiplier": 1.10
    }
]

def display_history_table():
    """Display the round history table with cumulative totals."""
    if not st.session_state.history:
        return
    
    # Convert history to DataFrame
    df = pd.DataFrame(st.session_state.history)
    
    # Format columns for display
    display_df = df.copy()
    display_df['Round'] = display_df['round']
    display_df['Scenario'] = display_df['scenario']
    display_df['Revenue'] = display_df['revenue'].apply(lambda x: f"${x:.0f}")
    display_df['Toys Made'] = display_df['produced']
    display_df['Qty Sold'] = display_df['sales']
    
    # Calculate weighted average inventory cost per item for each round
    # This represents the average cost of items in inventory at the time of sale
    display_df['inventory_before'] = display_df['inventory_after'] + display_df['sales']
    
    # Calculate cumulative total cost and quantity produced up to each round
    display_df['cumulative_produced'] = display_df['produced'].cumsum()
    display_df['cumulative_spent'] = display_df['spent'].cumsum()
    
    # Calculate weighted average cost: total cost of all items produced / total quantity produced
    display_df['avg_inv_cost_per_item'] = display_df['cumulative_spent'] / display_df['cumulative_produced'].replace(0, 1)
    # If no items produced yet, use production cost for that round
    display_df.loc[display_df['cumulative_produced'] == 0, 'avg_inv_cost_per_item'] = display_df.loc[display_df['cumulative_produced'] == 0, 'production_cost']
    
    display_df['Avg Inv Cost'] = display_df['avg_inv_cost_per_item'].apply(lambda x: f"${x:.0f}")
    
    # Use stored COGS if available, otherwise calculate it
    if 'cogs' in df.columns:
        display_df['cogs'] = df['cogs']
    else:
        # Calculate Costs as Cost of Goods Sold (qty sold * avg inventory cost)
        display_df['cogs'] = display_df['sales'] * display_df['avg_inv_cost_per_item']
    display_df['Costs'] = display_df['cogs'].apply(lambda x: f"${x:.0f}")
    
    display_df['Profit'] = display_df['round_profit'].apply(lambda x: f"${x:.0f}")
    display_df['Total Value'] = (display_df['cumulative_profit'] + display_df['inventory_cost']).apply(lambda x: f"${x:.0f}")
    display_df['Inventory $'] = display_df['inventory_value'].apply(lambda x: f"${x:.0f}")
    display_df['Inventory Qty'] = display_df['inventory_after']
    display_df['Price'] = display_df['price'].apply(lambda x: f"${x:.0f}")
    display_df['Cost'] = display_df['production_cost'].apply(lambda x: f"${x:.0f}")
    display_df['Inv Cost'] = display_df['inventory_cost'].apply(lambda x: f"${x:.0f}")
    display_df['Inv Value'] = display_df['inventory_cost'].apply(lambda x: f"${x:.0f}")
    # Select columns to display in the requested order
    columns_to_show = ['Round', 'Scenario','Toys Made', 'Avg Inv Cost','Price', 'Qty Sold','Profit', 'Inv Value','Total Value', 'Inventory Qty','Cost', 'Inv Cost' ]
    display_df = display_df[columns_to_show]
    
    st.subheader("📊 Round History")
    st.dataframe(display_df)
    
    # Calculate and display cumulative totals
    total_revenue = df['revenue'].sum()
    total_spent = df['spent'].sum()
    cumulative_profit = df['round_profit'].sum()
    
    # Calculate current inventory cost from last entry
    if len(df) > 0:
        last_entry = df.iloc[-1]
        current_inventory_cost = last_entry['inventory_cost']
        total_value_created = cumulative_profit + current_inventory_cost
    else:
        current_inventory_cost = 0
        total_value_created = cumulative_profit
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    with col2:
        st.metric("Total Spent", f"${total_spent:,.0f}")
    with col3:
        st.metric("Cumulative Profit", f"${cumulative_profit:,.0f}")
    with col4:
        st.metric("Total Value Created", f"${total_value_created:,.0f}")

st.title("🧸 Toy Shop Simulator")

st.markdown("""
### A Game to Learn Supply, Demand, and Pricing

You run a toy shop selling one type of toy. Each day:
- The cost to produce toys changes randomly.
- You decide how many toys to produce (it costs money from your cash).
- You set a selling price.
- Customers buy based on demand: **lower prices = more customers**, higher prices = fewer customers.
- Unsold toys stay in your inventory for future days.

**Goal:** Maximize your profit (final cash minus starting cash) over the set number of days.

**Demand formula:** `max(0, Base Demand + Coefficient × Price)`  
(The coefficient is usually negative — e.g., -2.)

Have fun and experiment with different strategies!
""")

if 'game_started' not in st.session_state:
    st.header("Configure Your Game")
    
    with st.sidebar:
        st.subheader("Custom Settings")
        
        num_rounds = st.number_input(
            "Number of rounds (days)", 
            min_value=1, max_value=50, value=3, step=1
        )
        
        starting_cash = st.number_input(
            "Starting cash ($)", 
            min_value=0, value=200, step=10
        )
        
        starting_inventory = st.number_input(
            "Starting inventory (toys)", 
            min_value=0, value=0, step=1
        )
        
        min_cost = st.number_input(
            "Minimum production cost per toy ($)", 
            min_value=1, value=8, step=1
        )
        
        max_cost = st.number_input(
            "Maximum production cost per toy ($)", 
            min_value=1, value=12, step=1
        )
        
        base_demand = st.number_input(
            "Base demand (customers at $0 price)", 
            min_value=0, value=50, step=1
        )
        
        demand_coeff = st.number_input(
            "Demand price coefficient (usually negative)", 
            value=-2, step=1
        )
        
        min_price = st.number_input(
            "Minimum allowed selling price ($)", 
            min_value=0, value=10, step=1
        )

    if min_cost > max_cost:
        st.error("⚠️ Minimum production cost cannot be greater than maximum!")
    else:
        if st.button("🚀 Start Game"):
            st.session_state.game_started = True
            st.session_state.num_rounds = num_rounds
            st.session_state.starting_cash = starting_cash
            st.session_state.cash = starting_cash
            st.session_state.inventory = starting_inventory
            st.session_state.current_round = 1
            st.session_state.min_cost = min_cost
            st.session_state.max_cost = max_cost
            st.session_state.base_demand = base_demand
            st.session_state.demand_coeff = demand_coeff
            st.session_state.min_price = min_price
            st.session_state.current_production_cost = random.randint(min_cost, max_cost)
            st.session_state.history = []
            st.session_state.current_scenario = random.choice(SCENARIOS)
            st.rerun()

else:
    # Game is running
    if st.session_state.current_round > st.session_state.num_rounds:
        st.balloons()
        profit = st.session_state.cash - st.session_state.starting_cash
        
        # Calculate inventory value and cost (use last round's data if available)
        if st.session_state.history:
            last_entry = st.session_state.history[-1]
            inventory_value = st.session_state.inventory * last_entry['price']
            inventory_cost = last_entry['inventory_cost']  # Use stored inventory cost
        else:
            inventory_value = 0
            inventory_cost = 0
        
        total_value_created = profit + inventory_cost
        
        st.header("🎉 Game Over!")
        
        # Income Statement
        st.subheader("📊 Income Statement")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Revenue & Costs:**")
            st.write(f"Starting Cash: ${st.session_state.starting_cash:,}")
            st.write(f"Final Cash: ${st.session_state.cash:,}")
            st.write(f"Cash Profit/Loss: ${profit:,}")
        
        with col2:
            st.markdown("**Inventory:**")
            st.write(f"Inventory On Hand: {st.session_state.inventory} toys")
            if st.session_state.history:
                st.write(f"At Price: ${last_entry['price']:.0f} per toy")
                st.write(f"Inventory Value: ${inventory_value:,.0f}")
            else:
                st.write(f"Inventory Value: ${inventory_value:,.0f}")
        
        st.markdown("---")
        st.markdown(f"### Total Value Created: ${total_value_created:,.0f}")
        st.markdown(f"*(Cash Profit: ${profit:,} + Inventory Cost: ${inventory_cost:,.0f})*")
        
        if profit > 0:
            st.success(f"Excellent! You earned a cash profit of ${profit:,}!")
        elif profit == 0:
            st.info("You broke even on cash.")
        else:
            st.warning(f"You ended with a cash loss of ${-profit:,}.")
        
        # Display final history table
        st.markdown("---")
        display_history_table()
        
        if st.button("🔄 Play Again with New Settings"):
            st.session_state.clear()
            st.rerun()
            
    else:
        # Active round
        st.header(f"📅 Day {st.session_state.current_round} of {st.session_state.num_rounds}")
        
        # Display current scenario narrative
        current_scenario = st.session_state.current_scenario
        st.info(f"**{current_scenario['name']}** - {current_scenario['narrative']}")
        
        # Calculate effective demand coefficient with scenario multiplier
        effective_coeff = st.session_state.demand_coeff * current_scenario['multiplier']
        
        # Display history table if there's any history
        if st.session_state.history:
            display_history_table()
            st.markdown("---")
        
        st.metric("Current cash", f"${st.session_state.cash:,}")
        st.metric("Current inventory", f"{st.session_state.inventory} toys")
        
        production_cost = st.session_state.current_production_cost
        st.info(f"Today's production cost per toy: **${production_cost}**")
        
        max_produce = int(st.session_state.cash // production_cost if production_cost > 0 else 0)
        
        produce_qty = st.number_input(
            "How many toys to produce today?",
            min_value=0,
            max_value=max_produce,
            value=0,
            step=1,
            help=f"You can afford up to {max_produce} toys at current cash."
        )
        
        price = st.number_input(
            "Set selling price per toy ($)",
            min_value=st.session_state.min_price,
            value=max(st.session_state.min_price + 5, 15),
            step=1
        )
        
        expected_demand = int(max(0, st.session_state.base_demand + effective_coeff * price))
        
        # Calculate average inventory cost (average production cost of items in inventory)
        if st.session_state.history:
            total_produced = sum(entry['produced'] for entry in st.session_state.history)
            total_spent = sum(entry['spent'] for entry in st.session_state.history)
            if total_produced > 0:
                avg_inventory_cost = total_spent / total_produced
            else:
                avg_inventory_cost = production_cost
        else:
            avg_inventory_cost = production_cost
        
        st.caption(f"At price {price}, expected customer demand is: {expected_demand} toys(scenario: {current_scenario['multiplier']:.2f}x multiplier) | Avg inventory cost: **{avg_inventory_cost:.2f}**")
        
        if st.button("🛍️ Produce, Sell, and End Day"):
            # Production
            spent = produce_qty * production_cost
            st.session_state.cash -= spent
            st.session_state.inventory += produce_qty
            
            # Sales (recalculate effective coefficient for this round)
            round_effective_coeff = st.session_state.demand_coeff * current_scenario['multiplier']
            demand = int(max(0, st.session_state.base_demand + round_effective_coeff * price))
            sales = min(demand, st.session_state.inventory)
            revenue = sales * price
            
            # Calculate average inventory cost for COGS (weighted average of all items produced)
            if st.session_state.history:
                total_produced = sum(entry['produced'] for entry in st.session_state.history)
                total_spent = sum(entry['spent'] for entry in st.session_state.history)
                if total_produced > 0:
                    avg_inv_cost = total_spent / total_produced
                else:
                    avg_inv_cost = production_cost
            else:
                avg_inv_cost = production_cost
            
            # Calculate Cost of Goods Sold (COGS)
            cogs = sales * avg_inv_cost
            
            st.session_state.cash += revenue
            st.session_state.inventory -= sales
            
            # Calculate round profit (Revenue - COGS)
            round_profit = revenue - cogs
            
            # Calculate cumulative profit
            cumulative_profit = sum(entry['round_profit'] for entry in st.session_state.history) + round_profit
            
            # Calculate inventory value and cost
            inventory_value = st.session_state.inventory * price  # Value at selling price
            inventory_cost = st.session_state.inventory * avg_inv_cost  # Cost basis using average inventory cost
            
            # Record round data to history
            history_entry = {
                "round": st.session_state.current_round,
                "scenario": current_scenario['name'],
                "production_cost": production_cost,
                "produced": produce_qty,
                "price": price,
                "demand": demand,
                "sales": sales,
                "revenue": revenue,
                "spent": spent,
                "cogs": cogs,
                "round_profit": round_profit,
                "cash_after": st.session_state.cash,
                "inventory_after": st.session_state.inventory,
                "inventory_value": inventory_value,
                "inventory_cost": inventory_cost,
                "cumulative_profit": cumulative_profit
            }
            st.session_state.history.append(history_entry)
            
            # Day summary
            st.success("Day complete!")
            st.markdown(f"""
            ### Day Summary
            - Produced: **{produce_qty}** toys (spent **${spent:,}**)
            - Price set: **${price}**
            - Customer demand: **{demand}**
            - Sold: **{sales}** toys (revenue **${revenue:,}**)
            - Round profit: **${round_profit:,}**
            - Cash after day: **${st.session_state.cash:,}**
            - Inventory carried over: **{st.session_state.inventory}** toys
            """)
            
            # Advance round
            st.session_state.current_round += 1
            if st.session_state.current_round <= st.session_state.num_rounds:
                st.session_state.current_production_cost = random.randint(
                    st.session_state.min_cost, st.session_state.max_cost
                )
                st.session_state.current_scenario = random.choice(SCENARIOS)
            st.rerun()
    
    # Sidebar controls during game
    with st.sidebar:
        st.caption("Current Game Settings")
        st.write(f"Rounds: {st.session_state.num_rounds}")
        st.write(f"Starting cash: ${st.session_state.starting_cash}")
        st.write(f"Demand formula: max(0, {st.session_state.base_demand} + {st.session_state.demand_coeff} × price)")
        if st.button("🛑 Abandon Game & Reset"):
            st.session_state.clear()
            st.rerun()