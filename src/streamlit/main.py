import streamlit as st

from pricing.base.rate import Rate
from pricing.base.volatility import Volatility
from pricing.option_strategies import ButterflyStrategy, CallSpreadStrategy, PutSpreadStrategy, StripStrategy, StrapStrategy
from utility.types import Maturity


def main():
    st.title("Option Pricing Calculator")

    option_type = st.selectbox("Select Option Type", ["Butterfly", "Call Spread", "Put Spread", "Strip", "Strap"])

    spot_price = st.number_input("Spot Price", value=100.0)
    maturity = st.date_input("Maturity")

    rate = st.number_input("Interest Rate", value=0.05)
    volatility = st.number_input("Volatility", value=0.20)

    if option_type == "Butterfly":
        strike_price1 = st.number_input("Strike Price 1", value=90.0)
        strike_price2 = st.number_input("Strike Price 2", value=100.0)
        strike_price3 = st.number_input("Strike Price 3", value=110.0)
    elif option_type in ["Call Spread", "Put Spread", "Strip", "Strap"]:
        lower_strike = st.number_input("Lower Strike", value=90.0)
        upper_strike = st.number_input("Upper Strike", value=110.0)

    if st.button("Price"):
        maturity = Maturity(maturity)

        if option_type == "Butterfly":
            strategy = ButterflyStrategy(spot_price, strike_price1, strike_price2, strike_price3, maturity, Rate(rate), Volatility(volatility))
        elif option_type == "Call Spread":
            strategy = CallSpreadStrategy(spot_price, lower_strike, upper_strike, maturity, Rate(rate), Volatility(volatility))
        elif option_type == "Put Spread":
            strategy = PutSpreadStrategy(spot_price, lower_strike, upper_strike, maturity, Rate(rate), Volatility(volatility))
        elif option_type == "Strip":
            strategy = StripStrategy(spot_price, strike_price1, strike_price2, maturity, Rate(rate), Volatility(volatility))
        elif option_type == "Strap":
            strategy = StrapStrategy(spot_price, lower_strike, upper_strike, maturity, Rate(rate), Volatility(volatility))

        option_price = strategy.compute_price()
        st.success(f"Option Price: {option_price:.2f} EUR")


if __name__ == "__main__":
    main()
