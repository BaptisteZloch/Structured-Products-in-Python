from datetime import datetime, timedelta
import streamlit as st
import time
import pandas as pd

from pricing.base.rate import Rate
from pricing.base.volatility import Volatility
from pricing.barrier_options import BarrierOption
from pricing.fixed_income import ZeroCouponBond, Bond
from pricing.vanilla_options import VanillaOption
from pricing.binary_options import BinaryOption
from pricing.option_strategies import StraddleStrategy, StrangleStrategy, ButterflyStrategy, CallSpreadStrategy, PutSpreadStrategy, StripStrategy, StrapStrategy
from utility.types import Maturity


# Couleurs personnalisées
background_color = "#f0f0f0"
button_color = "#4CAF50"
button_hover_color = "#45a049"
text_color = "black"
border_color = "black"

# Configuration du style Streamlit
st.markdown(
    f"""
    <style>
    body {{
        color: {text_color};
        background-color: {background_color};
    }}
    .stButton>button {{
        background-color: {button_color};
        color: white;
        font-weight: bold;
        border-color: {border_color};
        border-width: 2px;
        border-style: solid;
    }}
    .stButton>button:hover {{
        background-color: {button_hover_color};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def collect_volatility_data():
    st.title("Collecte des données de volatilité")
    volatility_matrix = pd.DataFrame(index=range(1, 6), columns=range(1, 6), data=0.0)
    st.write("Veuillez saisir les valeurs de volatilité pour chaque combinaison de maturité et de moneyness :")
    volatility_matrix = st.data_editor(volatility_matrix)
    if st.button("Enregistrer"):
        st.success("Données de volatilité enregistrées avec succès !")
    return volatility_matrix


def collect_rate_data():
    st.title("Collecte des données de taux")
    rate_matrix = pd.DataFrame(index=range(1), columns=range(1, 11), data=0.0)
    st.write("Veuillez saisir les valeurs de taux pour chaque maturité :")
    rate_matrix = st.data_editor(rate_matrix)
    if st.button("Enregistrer"):
        st.success("Données de taux enregistrées avec succès !")
    return rate_matrix


def show_greeks(greeks):
    greeks_df = pd.DataFrame.from_dict(greeks, orient="index", columns=["Value"])
    st.write(greeks_df)


def show_homepage():
    st.title("Modélisation et Pricing de produits structurés")
    st.markdown("""
    **Objectif :** Créer une application qui permet de structurer des produits financiers.

    **Scope des produits :** (Uniquement Mono Sous-Jacent)

    - Obligations à taux fixe (Formules fermées)
    - Options Vanille (sur actions, sur indices, sur taux de change) (Formules fermées)
    - Produits à stratégie optionnelle (straddle, strangle, butterfly, call spread, put spread, strip, strap) (Formules fermées)
    - Options à Barrières (KO, KI) (Monte Carlo)
    - Options Binaires (Formules fermées)
    - Produits Structurés (Reverse Convertible 1220, Certificat Outperformance 1310) (Formules fermées)
    """)


def show_option_pricing():
    st.title("Pricing des options classiques")
    option_type = st.selectbox("Select Option Type", ["Vanilla Option", "Binary Option"])

    spot_price = st.number_input("Spot Price", value=100.0)
    maturity_date = st.date_input("Maturity", max_value=datetime.today() + timedelta(days=365 * 100),
                                  format="DD/MM/YYYY")
    maturity_datetime = datetime.combine(maturity_date, datetime.min.time())
    today = datetime.today()

    rate_choice = st.selectbox("Rate Input", ["Single Value", "Rate Curve"])
    if rate_choice == "Single Value":
        rate = st.number_input("Interest Rate", value=0.05)
    else:
        rate_matrix = collect_rate_data()

    volatility_choice = st.selectbox("Volatility Input", ["Single Value", "Volatility Surface"])
    if volatility_choice == "Single Value":
        volatility = st.number_input("Volatility", value=0.20)
    else:
        volatility_matrix = collect_volatility_data()

    strike = st.number_input("Strike Price", value=100.0)
    opt_type = st.selectbox("Option Type", ["call", "put"])

    maturity = Maturity(start_date=today, end_date=maturity_datetime)
    rate = Rate(rate)
    volatility = Volatility(volatility)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Price"):
            with st.spinner("Calculating..."):
                time.sleep(2)  # Simuler un calcul long (2 secondes)

                if option_type == "Vanilla Option":
                    strategy = VanillaOption(spot_price, strike, maturity, rate, volatility, opt_type)
                elif option_type == "Binary Option":
                    strategy = BinaryOption(spot_price, strike, maturity, rate, volatility, opt_type)

                option_price = strategy.compute_price()
                st.success(f"Option Price: {option_price:.2f} EUR")

    with col2:
        if st.button("Greeks"):
            with st.spinner("Calculating..."):
                time.sleep(2)

                if option_type == "Vanilla Option":
                    strategy = VanillaOption(spot_price, strike, maturity, rate, volatility, opt_type)
                elif option_type == "Binary Option":
                    strategy = BinaryOption(spot_price, strike, maturity, rate, volatility, opt_type)

                greeks = strategy.compute_greeks()
                st.success(f"Greeks : {show_greeks(greeks)}")

    with col3:
        if st.button("Proba d'exercice"):
            with st.spinner("Calculating..."):
                time.sleep(2)
                st.success("Pobabilité : 0.5")


def show_fixed_income_pricing():
    st.title("Pricing des Produits à Revenu Fixe")
    option_type = st.selectbox("Select Option Type", ["Zero Coupon Bond", "Bond"])

    spot_price = st.number_input("Spot Price", value=100.0)
    maturity_date = st.date_input("Maturity", max_value=datetime.today() + timedelta(days=365 * 100),
                                  format="DD/MM/YYYY")
    maturity_datetime = datetime.combine(maturity_date, datetime.min.time())
    today = datetime.today()

    rate_choice = st.selectbox("Rate Input", ["Single Value", "Rate Curve"])
    if rate_choice == "Single Value":
        rate = st.number_input("Interest Rate", value=0.05)
    else:
        rate_matrix = collect_rate_data()

    if option_type == "Bond":
        coupon_rate = st.number_input("Coupon Rate", value=0.05)
        nb_coupon = st.number_input("Nb coupons", value=10)

    maturity = Maturity(start_date=today, end_date=maturity_datetime)
    rate = Rate(rate)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Price"):
            with st.spinner("Calculating..."):
                time.sleep(2)

                if option_type == "Zero Coupon Bond":
                    strategy = ZeroCouponBond(rate, maturity, spot_price)
                elif option_type == "Bond":
                    strategy = Bond(rate, maturity, spot_price, coupon_rate, nb_coupon)

                option_price = strategy.compute_price()
                st.success(f"Option Price: {option_price:.2f} EUR")

    with col2:
        if st.button("Greeks"):
            with st.spinner("Calculating..."):
                time.sleep(2)

                if option_type == "Zero Coupon Bond":
                    strategy = ZeroCouponBond(rate, maturity, spot_price)
                elif option_type == "Bond":
                    strategy = Bond(rate, maturity, spot_price, coupon_rate, nb_coupon)

                greeks = strategy.compute_greeks()
                st.success(f"Greeks : {show_greeks(greeks)}")

    with col3:
        if st.button("Proba d'exercice"):
            with st.spinner("Calculating..."):
                time.sleep(2)
                st.success("Pobabilité : 0.5")


def show_exo_product_pricing():
    st.title("Pricing des Options Exotiques")
    option_type = st.selectbox("Select Option Type", ["Barrier Option", "Straddle Strategy", "Strangle Strategy",
                                                      "Butterfly", "Call Spread", "Put Spread", "Strip", "Strap"])

    spot_price = st.number_input("Spot Price", value=100.0)
    maturity_date = st.date_input("Maturity", max_value=datetime.today() + timedelta(days=365 * 100),
                                  format="DD/MM/YYYY")
    maturity_datetime = datetime.combine(maturity_date, datetime.min.time())
    today = datetime.today()

    rate_choice = st.selectbox("Rate Input", ["Single Value", "Rate Curve"])
    if rate_choice == "Single Value":
        rate = st.number_input("Interest Rate", value=0.05)
    else:
        rate_matrix = collect_rate_data()

    volatility_choice = st.selectbox("Volatility Input", ["Single Value", "Volatility Surface"])
    if volatility_choice == "Single Value":
        volatility = st.number_input("Volatility", value=0.20)
    else:
        volatility_matrix = collect_volatility_data()

    if option_type == "Barrier Option":
        strike = st.number_input("Strike Price", value=100.0)
        opt_type = st.selectbox("Option Type", ["call", "put"])
        barrier_level = st.number_input("Barrier Level", value=100.0)
        barrier_type = st.selectbox("Barrier Type", ["KO", "KI"])
    elif option_type == "Straddle Strategy":
        strike = st.number_input("Strike Price", value=100.0)
    elif option_type == "Butterfly":
        strike_price1 = st.number_input("Strike Price 1", value=90.0)
        strike_price2 = st.number_input("Strike Price 2", value=100.0)
        strike_price3 = st.number_input("Strike Price 3", value=110.0)
    elif option_type in ["Strangle Strategy", "Call Spread", "Put Spread", "Strip", "Strap"]:
        lower_strike = st.number_input("Lower Strike", value=90.0)
        upper_strike = st.number_input("Upper Strike", value=110.0)

    maturity = Maturity(start_date=today, end_date=maturity_datetime)
    rate = Rate(rate)
    volatility = Volatility(volatility)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Price"):
            with st.spinner("Calculating..."):
                time.sleep(2)

                if option_type == "Barrier Option":
                    strategy = BarrierOption(spot_price, strike, maturity, rate, volatility, opt_type, barrier_level, barrier_type)
                elif option_type == "Straddle Strategy":
                    strategy = StraddleStrategy(spot_price, strike, maturity, rate, volatility)
                elif option_type == "Strangle Strategy":
                    strategy = StrangleStrategy(spot_price, lower_strike, upper_strike, maturity, rate, volatility)
                elif option_type == "Butterfly":
                    strategy = ButterflyStrategy(spot_price, strike_price1, strike_price2, strike_price3, maturity, rate, volatility)
                elif option_type == "Call Spread":
                    strategy = CallSpreadStrategy(spot_price, lower_strike, upper_strike, maturity, rate, volatility)
                elif option_type == "Put Spread":
                    strategy = PutSpreadStrategy(spot_price, lower_strike, upper_strike, maturity, rate, volatility)
                elif option_type == "Strip":
                    strategy = StripStrategy(spot_price, lower_strike, upper_strike, maturity, rate, volatility)
                elif option_type == "Strap":
                    strategy = StrapStrategy(spot_price, lower_strike, upper_strike, maturity, rate, volatility)

                option_price = strategy.compute_price()
                st.success(f"Option Price: {option_price:.2f} EUR")

    with col2:
        if st.button("Greeks"):
            with st.spinner("Calculating..."):
                time.sleep(2)

                if option_type == "Barrier Option":
                    strategy = BarrierOption(spot_price, strike, maturity, rate, volatility, opt_type, barrier_level, barrier_type)
                elif option_type == "Straddle Strategy":
                    strategy = StraddleStrategy(spot_price, strike, maturity, rate, volatility)
                elif option_type == "Strangle Strategy":
                    strategy = StrangleStrategy(spot_price, lower_strike, upper_strike, maturity, rate, volatility)
                elif option_type == "Butterfly":
                    strategy = ButterflyStrategy(spot_price, strike_price1, strike_price2, strike_price3, maturity, rate, volatility)
                elif option_type == "Call Spread":
                    strategy = CallSpreadStrategy(spot_price, lower_strike, upper_strike, maturity, rate, volatility)
                elif option_type == "Put Spread":
                    strategy = PutSpreadStrategy(spot_price, lower_strike, upper_strike, maturity, rate, volatility)
                elif option_type == "Strip":
                    strategy = StripStrategy(spot_price, lower_strike, upper_strike, maturity, rate, volatility)
                elif option_type == "Strap":
                    strategy = StrapStrategy(spot_price, lower_strike, upper_strike, maturity, rate, volatility)

                greeks = strategy.compute_greeks()
                st.success(f"Greeks : {show_greeks(greeks)}")

    with col3:
        if st.button("Proba d'exercice"):
            with st.spinner("Calculating..."):
                time.sleep(2)
                st.success("Pobabilité : 0.5")


def main():
    pages = {
        "Page d'accueil": show_homepage,
        "Pricing des Options Classiques": show_option_pricing,
        "Pricing des Produits à Revenu Fixe": show_fixed_income_pricing,
        "Pricing des Options Exotiques": show_exo_product_pricing
    }

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(pages.keys()))

    page = pages[selection]
    page()


if __name__ == "__main__":
    main()
