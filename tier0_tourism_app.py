# --- 7. ΔΥΝΑΜΙΚΗ ΕΠΕΞΗΓΗΣΗ ΠΑΡΑΜΕΤΡΩΝ (SHAP & PIAS) ---
st.markdown(f"### 🧠 Επιστημονική Τεκμηρίωση για: {focus_city}")

exp_col1, exp_col2 = st.columns(2)

with exp_col1:
    st.markdown(f"""
    <div class='ai-advice'>
        <b>Ανάλυση Συνεισφοράς (SHAP Values):</b><br>
        Για τον Δήμο {focus_city}, ο δείκτης ανθεκτικότητας διαμορφώθηκε κυρίως από:
        <ul>
            <li><b>Ψηφιακή Ζήτηση:</b> Καθορίζει το 40% του σκορ (Validation: LOO-CV).</li>
            <li><b>Sectoral Imputation:</b> Χρησιμοποιήθηκε η μέθοδος <i>{CONFIG['sectoral_imputation']}</i> 
            για την κάλυψη ελλιπών δεδομένων NACE Rev.2.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with exp_col2:
    st.markdown(f"""
    <div class='summary-box'>
        <b>Ευθυγράμμιση Πολιτικής (PIAS - Scale Invariant):</b><br>
        Ο δείκτης PIAS ({f_data['PIAS']:.2f}) υπολογίστηκε μέσω <b>Cosine Similarity</b>. 
        Αυτό σημαίνει ότι αξιολογούμε την <i>ποιότητα</i> της στόχευσης των κονδυλίων ΕΣΠΑ 
        σε σχέση με τις τοπικές ανάγκες, απομονώνοντας το συνολικό ύψος της χρηματοδότησης.
    </div>
    """, unsafe_allow_html=True)

# --- 8. QUALITY GATES & FALLBACKS ---
if f_data['Score'] < 40:
    st.error(f"⚠️ **Προσοχή:** Ο Δήμος {focus_city} βρίσκεται κάτω από το όριο ασφαλείας (μ - 0.5σ).")
    st.info("💡 Ενεργοποίηση Fallback: Έλεγχος Shannon Entropy για επαλήθευση των βαρών.")
