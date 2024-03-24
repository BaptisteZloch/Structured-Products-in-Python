from requests import post, get
import json
from datetime import datetime, timedelta
import streamlit as st
import time
import pandas as pd
import numpy as np

from pricing.base.rate import Rate
from pricing.base.volatility import Volatility
from utility.types import Maturity


URL = "https://structured-pricing-api-dauphine.koyeb.app"

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


def collect_volatility_data(strike_price):
    strikes = np.array([0.8, 0.9, 1, 1.1, 1.2]) * strike_price
    volatility_matrix = pd.DataFrame(index=strikes, columns=["6M", "1Y", "2Y", "5Y", "10Y"], data=0.0)
    st.write("Veuillez saisir les valeurs de volatilité pour chaque combinaison de maturité et de moneyness :")
    volatility_matrix = st.data_editor(volatility_matrix)
    maturities = [0.5, 1, 2, 5, 10]
    volatility_surface = {}
    for i, strike in enumerate(volatility_matrix.index):
        for j, maturity in enumerate(volatility_matrix.columns):
            key = (strikes[i], maturities[j])
            if not pd.isnull(volatility_matrix.loc[strike, maturity]):
                volatility_surface[key] = volatility_matrix.loc[strike, maturity]
    if st.button("Enregistrer la Surface de Volatilité"):
        st.success("Données de volatilité enregistrées avec succès !")
    return volatility_surface


def collect_rate_data():
    rate_matrix = pd.DataFrame(index=range(1), columns=["1M", "2M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "5Y", "7Y",
                                                        "10Y", "15Y", "20Y", "30Y"], data=0.0)
    st.write("Veuillez saisir les valeurs de taux pour chaque maturité, remplir 0 si donnée manquante :")
    rate_matrix = st.data_editor(rate_matrix)
    maturities = [Maturity(1 / 12), Maturity(2 / 12), Maturity(3 / 12), Maturity(6 / 12), Maturity(9 / 12), Maturity(1),
                  Maturity(2), Maturity(3), Maturity(5), Maturity(7), Maturity(10), Maturity(15), Maturity(20),
                  Maturity(30)]
    rate_curve = {}
    for i, maturity in enumerate(rate_matrix.columns):
        if not pd.isnull(rate_matrix.at[0, maturity]):
            rate_curve[maturities[i]] = rate_matrix.at[0, maturity]
    if st.button("Enregistrer la Courbe des Taux"):
        st.success("Données de taux enregistrées avec succès !")
    return rate_curve


def show_greeks(greeks):
    del greeks["price"]
    greeks_df = pd.DataFrame.from_dict(greeks, orient="index", columns=["Value"])
    st.write(greeks_df)
    return "Done !"


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
    option_type = st.selectbox("Select Option Type", ["Vanilla Option", "Binary Option", "Barrier Option"])

    spot_price = st.number_input("Spot Price", value=100.0)
    strike = st.number_input("Strike Price", value=100.0)
    dividend = st.number_input("Dividend", value=0.05)

    maturity_date = st.date_input("Maturity", max_value=datetime.today() + timedelta(days=365 * 100), format="DD/MM/YYYY")
    maturity_datetime = datetime.combine(maturity_date, datetime.min.time())
    today = datetime.today()
    maturity = Maturity(start_date=today, end_date=maturity_datetime).maturity_in_years

    rate_choice = st.selectbox("Rate Input", ["Single Value", "Rate Curve"])
    if rate_choice == "Single Value":
        rate = st.number_input("Interest Rate", value=0.05)
        rate = Rate(rate).get_rate()
    else:
        rate_curve = collect_rate_data()
        rate = Rate(rate_curve=rate_curve).get_rate(maturity=Maturity(start_date=today, end_date=maturity_datetime))

    volatility_choice = st.selectbox("Volatility Input", ["Single Value", "Volatility Surface"])
    if volatility_choice == "Single Value":
        volatility = st.number_input("Volatility", value=0.20)
        volatility = Volatility(volatility).get_volatility()
    else:
        volatility_surface = collect_volatility_data(strike)
        volatility = Volatility(volatility_surface=volatility_surface).get_volatility(strike, maturity)

    if option_type == "Barrier Option":
        barrier_level = st.number_input("Barrier Level", value=100.0)
        barrier_type = st.selectbox("Barrier Type", ["KO", "KI"])
    else:
        barrier_level = 0
        barrier_type = 0

    opt_type = st.selectbox("Option Type", ["call", "put"])

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Price"):
            with st.spinner("Calculating..."):
                time.sleep(2)
                dict_option = {"Vanilla Option": "vanilla", "Binary Option": "binary", "Barrier Option": "barrier"}

                data = {
                    "spot_price": spot_price,
                    "strike_price": strike,
                    "maturity": maturity,
                    "dividend": dividend,
                    "rate": rate,
                    "volatility": volatility,
                    "option_type": opt_type,
                    **({"barrier_level": barrier_level, "barrier_type": barrier_type} if option_type == "Barrier Option" else {})
                }

                res = post(url=f"{URL}/api/v1/price/option/{dict_option[option_type]}", data=json.dumps(data)).json()

                option_price = res["price"]
                st.success(f"Option Price: {option_price:.2f} EUR")

    with col2:
        if st.button("Greeks"):
            with st.spinner("Calculating..."):
                time.sleep(2)
                dict_option = {"Vanilla Option": "vanilla", "Binary Option": "binary", "Barrier Option": "barrier"}

                data = {
                    "spot_price": spot_price,
                    "strike_price": strike,
                    "maturity": maturity,
                    "dividend": dividend,
                    "rate": rate,
                    "volatility": volatility,
                    "option_type": opt_type,
                    ** ({"barrier_level": barrier_level, "barrier_type": barrier_type} if option_type == "Barrier Option" else {})
                }

                res = post(url=f"{URL}/api/v1/price/option/{dict_option[option_type]}", data=json.dumps(data)).json()

                st.success(f"Greeks : {show_greeks(res)}")

    with col3:
        if st.button("Proba d'exercice"):
            with st.spinner("Calculating..."):
                time.sleep(2)
                st.success("Pobabilité : 0.5")


def show_fixed_income_pricing():
    st.title("Pricing des Produits à Revenu Fixe")
    option_type = st.selectbox("Select Option Type", ["Zero Coupon Bond", "Bond"])

    nominal = st.number_input("Nominal", value=100.0)
    maturity_date = st.date_input("Maturity", max_value=datetime.today() + timedelta(days=365 * 100), format="DD/MM/YYYY")
    maturity_datetime = datetime.combine(maturity_date, datetime.min.time())
    today = datetime.today()
    maturity = Maturity(start_date=today, end_date=maturity_datetime).maturity_in_years

    rate_choice = st.selectbox("Rate Input", ["Single Value", "Rate Curve"])
    if rate_choice == "Single Value":
        rate = st.number_input("Interest Rate", value=0.05)
        rate = Rate(rate).get_rate()
    else:
        rate_curve = collect_rate_data()
        rate = Rate(rate_curve=rate_curve).get_rate(maturity=Maturity(start_date=today, end_date=maturity_datetime))

    if option_type == "Bond":
        coupon_rate = st.number_input("Coupon Rate", value=0.05)
        nb_coupon = st.number_input("Nb coupons", value=10)
    else:
        coupon_rate = 0
        nb_coupon = 0

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Price"):
            with st.spinner("Calculating..."):
                time.sleep(2)
                dict_option = {"Zero Coupon Bond": "zero-coupon", "Bond": "vanilla"}

                data = {
                    "maturity": maturity,
                    "rate": rate,
                    "nominal": nominal,
                    **({"coupon_rate": coupon_rate, "nb_coupon": nb_coupon} if option_type == "Bond" else {})
                }

                res = post(url=f"{URL}/api/v1/price/bond/{dict_option[option_type]}", data=json.dumps(data)).json()

                option_price = res["price"]
                st.success(f"Option Price: {option_price:.2f} EUR")

    with col2:
        if st.button("Greeks"):
            with st.spinner("Calculating..."):
                time.sleep(2)
                dict_option = {"Zero Coupon Bond": "zero-coupon", "Bond": "vanilla"}

                data = {
                    "maturity": maturity,
                    "rate": rate,
                    "nominal": nominal,
                    **({"coupon_rate": coupon_rate, "nb_coupon": nb_coupon} if option_type == "Bond" else {})
                }

                res = post(url=f"{URL}/api/v1/price/bond/{dict_option[option_type]}", data=json.dumps(data)).json()

            st.success(f"Greeks : {show_greeks(res)}")

    with col3:
        if st.button("Proba d'exercice"):
            with st.spinner("Calculating..."):
                time.sleep(2)
                st.success("Pobabilité : 0.5")


def show_strat_product_pricing():
    st.title("Pricing des Stratégies d'Options")
    option_type = st.selectbox("Select Option Type", ["Straddle Strategy", "Strangle Strategy", "Butterfly",
                                                      "Call Spread", "Put Spread", "Strip", "Strap"])

    spot_price = st.number_input("Spot Price", value=100.0)
    dividend = st.number_input("Dividend", value=0.05)
    maturity_date = st.date_input("Maturity", max_value=datetime.today() + timedelta(days=365 * 100), format="DD/MM/YYYY")
    maturity_datetime = datetime.combine(maturity_date, datetime.min.time())
    today = datetime.today()
    maturity = Maturity(start_date=today, end_date=maturity_datetime).maturity_in_years

    rate_choice = st.selectbox("Rate Input", ["Single Value", "Rate Curve"])
    if rate_choice == "Single Value":
        rate = st.number_input("Interest Rate", value=0.05)
        rate = Rate(rate).get_rate()
    else:
        rate_curve = collect_rate_data()
        rate = Rate(rate_curve=rate_curve).get_rate(maturity=Maturity(start_date=today, end_date=maturity_datetime))

    volatility = st.number_input("Volatility", value=0.20)
    volatility = Volatility(volatility).get_volatility()

    strike, strike_price1, strike_price2, strike_price3, lower_strike, upper_strike = 0, 0, 0, 0, 0, 0

    if option_type == "Straddle Strategy":
        strike = st.number_input("Strike Price", value=100.0)
    elif option_type == "Butterfly":
        strike_price1 = st.number_input("Strike Price 1", value=90.0)
        strike_price2 = st.number_input("Strike Price 2", value=100.0)
        strike_price3 = st.number_input("Strike Price 3", value=110.0)
    elif option_type in ["Strangle Strategy", "Call Spread", "Put Spread", "Strip", "Strap"]:
        lower_strike = st.number_input("Lower Strike", value=90.0)
        upper_strike = st.number_input("Upper Strike", value=110.0)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Price"):
            with st.spinner("Calculating..."):
                time.sleep(2)

                dict_option = {"Straddle Strategy": "straddle", "Strangle Strategy": "strangle",
                               "Butterfly": "butterfly", "Call Spread": "call-spread", "Put Spread": "put-spread",
                               "Strip": "strip", "Strap": "strap"}

                data = {
                    "spot_price": spot_price,
                    "maturity": maturity,
                    "dividend": dividend,
                    "rate": rate,
                    "volatility": volatility,
                    **({"strike_price": strike} if option_type == "Straddle Strategy" else
                       ({"lower_strike": lower_strike, "upper_strike": upper_strike} if option_type != "Butterfly" else
                       {"strike_price1": strike_price1, "strike_price2": strike_price2, "strike_price3": strike_price3})
                       )
                }

                res = post(url=f"{URL}/api/v1/price/option-strategy/{dict_option[option_type]}", data=json.dumps(data)).json()

                option_price = res["price"]
                st.success(f"Option Price: {option_price:.2f} EUR")

    with col2:
        if st.button("Greeks"):
            with st.spinner("Calculating..."):
                time.sleep(2)

                dict_option = {"Straddle Strategy": "straddle", "Strangle Strategy": "strangle",
                               "Butterfly": "butterfly", "Call Spread": "call-spread", "Put Spread": "put-spread",
                               "Strip": "strip", "Strap": "strap"}

                data = {
                    "spot_price": spot_price,
                    "maturity": maturity,
                    "dividend": dividend,
                    "rate": rate,
                    "volatility": volatility,
                    **({"strike": strike} if option_type == "Straddle Strategy" else
                       ({"lower_strike": lower_strike, "upper_strike": upper_strike} if option_type != "Butterfly" else
                       {"strike_price1": strike_price1, "strike_price2": strike_price2, "strike_price3": strike_price3})
                       )
                }

                res = post(url=f"{URL}/api/v1/price/option-strategy/{dict_option[option_type]}", data=json.dumps(data)).json()

            st.success(f"Greeks : {show_greeks(res)}")

    with col3:
        if st.button("Proba d'exercice"):
            with st.spinner("Calculating..."):
                time.sleep(2)
                st.success("Pobabilité : 0.5")


def show_struct_product_pricing():
    st.title("Pricing des Produits Structurés")
    option_type = st.selectbox("Select Option Type", ["Reverse Convertible", "Outperformer Certificate"])

    spot_price = st.number_input("Spot Price", value=100.0)
    maturity_date = st.date_input("Maturity", max_value=datetime.today() + timedelta(days=365 * 100), format="DD/MM/YYYY")
    maturity_datetime = datetime.combine(maturity_date, datetime.min.time())
    today = datetime.today()
    maturity = Maturity(start_date=today, end_date=maturity_datetime).maturity_in_years

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Price"):
            with st.spinner("Calculating..."):
                time.sleep(2)

                dict_option = {"Reverse Convertible": "reverse-convertible",
                               "Outperformer Certificate": "outperformer-certificate"}

                res = post(url=f"{URL}/api/v1/price/structured-product/{dict_option[option_type]}",
                           data=json.dumps(
                               {
                                   "maturity": maturity,
                                   "spot_price": spot_price
                               }
                           )
                           ).json()

                option_price = res["price"]
                st.success(f"Option Price: {option_price:.2f} EUR")

    with col2:
        if st.button("Greeks"):
            with st.spinner("Calculating..."):
                time.sleep(2)

                dict_option = {"Reverse Convertible": "reverse-convertible",
                               "Outperformer Certificate": "outperformer-certificate"}

                res = post(url=f"{URL}/api/v1/price/structured-product/{dict_option[option_type]}",
                           data=json.dumps(
                               {
                                   "maturity": maturity,
                                   "spot_price": spot_price
                               }
                           )
                           ).json()

                st.success(f"Greeks : {show_greeks(res)}")

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
        "Pricing des Stratégies d'Options": show_strat_product_pricing,
        "Pricing des Produits Structurés": show_struct_product_pricing
    }

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(pages.keys()))

    page = pages[selection]
    page()


if __name__ == "__main__":
    main()
