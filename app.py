import streamlit as st
import pandas as pd
from grammar_core import Grammar
from transform import eliminate_left_recursion
from first_follow import compute_first, compute_follow
from parse_table import generate_parse_table, has_conflicts
from parser_ll1 import parse
from visualize import generate_tree_dot

st.set_page_config(page_title="LL(1) Grammar Debugger", layout="wide")

st.title("🧩 LL(1) Grammar Debugger & Visual Parser")
st.markdown("Analyze Context-Free Grammars, eliminate left recursion, compute FIRST/FOLLOW sets, generate LL(1) parse tables, and visualize predictive parsing.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Input Grammar")
    default_grammar = "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id"
    grammar_input = st.text_area("Enter grammar rules (e.g., A -> B c | epsilon):", value=default_grammar, height=200)
    
    st.header("2. Input String")
    test_string = st.text_input("Enter string to parse (space-separated tokens):", value="id + id * id")
    
    run_btn = st.button("Run Analysis")

with col2:
    if run_btn:
        try:
            # 1. Parse Grammar
            g = Grammar()
            g.parse_from_string(grammar_input)
            
            # 2. Eliminate Left Recursion
            g_transformed = eliminate_left_recursion(g)
            
            # 3. FIRST and FOLLOW
            first_sets = compute_first(g_transformed)
            follow_sets = compute_follow(g_transformed, first_sets)
            
            # 4. Parse Table
            parse_table = generate_parse_table(g_transformed, first_sets, follow_sets)
            is_ll1 = not has_conflicts(parse_table)
            
            # 5. Parsing
            success, trace, tree_root = parse(g_transformed, parse_table, test_string)
            
            # --- Output Sections ---
            st.markdown("### 📊 Analysis Results")
            
            tab_grammar, tab_symbols, tab_sets, tab_table, tab_parse, tab_tree = st.tabs([
                "1. Transform", 
                "2. Symbols", 
                "3. FIRST/FOLLOW", 
                "4. Parse Table", 
                "5. Parse Trace", 
                "6. Visual Tree"
            ])
            
            with tab_grammar:
                st.info("Left recursion elimination converts grammar into a form suitable for LL(1) parsing. If the grammar has no left recursion, it remains unchanged.")
                st.subheader("Original Grammar")
                st.code(g.display(), language="text")
                
                st.subheader("Transformed Grammar")
                st.code(g_transformed.display(), language="text")
            
            with tab_symbols:
                symbols_data = []
                for nt in sorted(list(g_transformed.non_terminals)):
                    type_str = "Start Symbol (Non-Terminal)" if nt == g_transformed.start_symbol else "Non-Terminal"
                    symbols_data.append({"Symbol": nt, "Type": type_str})
                for t in sorted(list(g_transformed.terminals)):
                    symbols_data.append({"Symbol": t, "Type": "Terminal"})
                
                st.dataframe(pd.DataFrame(symbols_data))
            
            with tab_sets:
                st.subheader("FIRST Sets")
                first_df = [{"Non-Terminal": nt, "FIRST": "{ " + ", ".join(first_sets[nt]) + " }"} for nt in g_transformed.non_terminals]
                st.dataframe(pd.DataFrame(first_df))
                
                st.subheader("FOLLOW Sets")
                follow_df = [{"Non-Terminal": nt, "FOLLOW": "{ " + ", ".join(follow_sets[nt]) + " }"} for nt in g_transformed.non_terminals]
                st.dataframe(pd.DataFrame(follow_df))
                
            with tab_table:
                if not is_ll1:
                    st.error("⚠️ Grammar is **NOT LL(1)**. There are conflicts in the parse table!")
                else:
                    st.success("✅ Grammar is **LL(1)**. No conflicts found.")
                    
                terminals = sorted(list(g_transformed.terminals | {'$'}))
                table_data = []
                for nt in g_transformed.non_terminals:
                    row = {"Non-Terminal": f"<b>{nt}</b>"}
                    for t in terminals:
                        prods = parse_table[nt].get(t, [])
                        if len(prods) == 0:
                            row[t] = ""
                        elif len(prods) == 1:
                            row[t] = f"{nt} &rarr; {' '.join(prods[0])}"
                        else:
                            row[t] = "<span style='color:red; font-weight:bold'>CONFLICT</span><br>" + "<br>".join([f"{nt} &rarr; {' '.join(p)}" for p in prods])
                    table_data.append(row)
                    
                df = pd.DataFrame(table_data)
                st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            with tab_parse:
                if success:
                    st.success(f"✅ String **'{test_string}'** successfully parsed!")
                else:
                    st.error(f"❌ Failed to parse string **'{test_string}'**. See trace below.")
                    
                trace_df = pd.DataFrame(trace)
                st.dataframe(trace_df)
            
            with tab_tree:
                if success:
                    st.info("The visual parse tree demonstrates the predictive parsing process from the Start Symbol down to the input tokens.")
                    dot_str = generate_tree_dot(tree_root)
                    st.graphviz_chart(dot_str)
                else:
                    st.warning("⚠️ Parse tree is incomplete because parsing failed due to conflicts or invalid syntax.")
                    if tree_root:
                        dot_str = generate_tree_dot(tree_root)
                        st.graphviz_chart(dot_str)

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")
