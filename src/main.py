from datetime import datetime, timedelta
import streamlit as st
import time

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


def main():
    st.title("Option Pricing Calculator")

    option_type = st.selectbox("Select Option Type", ["Zero Coupon Bond", "Bond", "Vanilla Option", "Binary Option",
                                                      "Barrier Option", "Straddle Strategy", "Strangle Strategy",
                                                      "Butterfly", "Call Spread", "Put Spread", "Strip", "Strap"])

    spot_price = st.number_input("Spot Price", value=100.0)
    maturity_date = st.date_input("Maturity", max_value=datetime.today() + timedelta(days=365 * 100), format="DD/MM/YYYY")
    maturity_datetime = datetime.combine(maturity_date, datetime.min.time())
    today = datetime.today()

    rate = st.number_input("Interest Rate", value=0.05)
    volatility = st.number_input("Volatility", value=0.20)

    if option_type == "Bond":
        coupon_rate = st.number_input("Coupon Rate", value=0.05)
        nb_coupon = st.number_input("Nb coupons", value=10)
    elif option_type in ["Vanilla Option", "Binary Option"]:
        strike = st.number_input("Strike Price", value=100.0)
        opt_type = st.selectbox("Option Type", ["call", "put"])
    elif option_type == "Barrier Option":
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

    # Bouton pour calculer le prix de l'option
    if st.button("Price"):
        with st.spinner("Calculating..."):
            time.sleep(2)  # Simuler un calcul long (2 secondes)
            maturity = Maturity(start_date=today, end_date=maturity_datetime)
            rate = Rate(rate)
            volatility = Volatility(volatility)

            # Calcul du prix de l'option en fonction du type sélectionné
            if option_type == "Zero Coupon Bond":
                strategy = ZeroCouponBond(rate, maturity, spot_price)
            elif option_type == "Bond":
                strategy = Bond(rate, maturity, spot_price, coupon_rate, nb_coupon)
            elif option_type == "Vanilla Option":
                strategy = VanillaOption(spot_price, strike, maturity, rate, volatility, opt_type)
            elif option_type == "Binary Option":
                strategy = BinaryOption(spot_price, strike, maturity, rate, volatility, opt_type)
            elif option_type == "Barrier Option":
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


if __name__ == "__main__":
    main()
