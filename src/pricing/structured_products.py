from typing import Dict, Optional
from src.pricing.base.structured_products_base import StructuredProductBase
from src.pricing.base.volatility import Volatility
from src.pricing.fixed_income import ZeroCouponBond
from src.pricing.binary_options import BinaryOption
from src.pricing.base.rate import Rate
from src.utility.types import Maturity

class ReverseConvertible(StructuredProductBase):
    
    def __init__(
        self, 
        rate: Rate,
        maturity: Maturity,
        nominal: int,
        spot_price: float,
        strike_price: float,
        volatility: Volatility,
        converse_rate: float
    ) -> None:
        super().__init__("reverse-convertible")
        self.__rate = rate
        self.__maturity = maturity
        self.__nominal = nominal
        self.__spot_price = spot_price
        self.__strike_price = strike_price
        self.__volatility = volatility
        self.__converse_rate = converse_rate


    def compute_price(self) -> float:
        bond = ZeroCouponBond(
            self.__rate, 
            self.__maturity, 
            self.__nominal
            )
        option = BinaryOption(
            self.__spot_price, 
            self.__strike_price, 
            self.__maturity, 
            self.__rate, 
            self.__volatility,
            "put"
            )
        
        self._price = bond.compute_price() - (1-self.__converse_rate) * option.compute_price()
        
        return self._price


    def compute_delta(self) -> float:
        
        RC_spot = ReverseConvertible(
            self.__rate,
            self.__maturity,
            self.__nominal,
            self.__spot_price*(1-0.01),
            self.__strike_price,
            self.__volatility,
            self.__converse_rate
            )
        
        if self._price is None:
            self.compute_price()
            
        RC_spot.compute_price()
        delta = (self._price - RC_spot._price) / (self.__spot_price*0.01)
        
        return delta
    
    def compute_gamma(self) -> float:
        
        RC_spot = ReverseConvertible(
            self.__rate,
            self.__maturity,
            self.__nominal,
            self.__spot_price*(1-0.01),
            self.__strike_price,
            self.__volatility,
            self.__converse_rate
            )
        
        delta1 = self.compute_delta()
        delta2 = RC_spot.compute_delta()
        
        gamma = (delta1-delta2) / (self.__spot_price*0.01)
        
        return gamma
        
    def compute_rho(self) -> float:
        new_rate = Rate(
            self.__rate.__rate * (1-0.01),
            self.__rate.__rate_type,
            self.__rate.__interpolation_type
            )
        RC_rate = ReverseConvertible(
            new_rate,
            self.__maturity,
            self.__nominal,
            self.__spot_price,
            self.__strike_price,
            self.__volatility,
            self.__converse_rate
            )
        del new_rate
        
        if self._price is None:
            self.compute_price()
        RC_rate.compute_price()
        
        rho = (self._price - RC_rate._price) / (0.01*self.__rate.__rate)
        
        return rho
    
    def compute_vega(self) -> float:
        new_vol = Volatility(
            self.__volatility.__volatility * (1-0.01),
            self.__volatility.__interpol_type
            )
        RC_vol = ReverseConvertible(
            self.__rate,
            self.__maturity,
            self.__nominal,
            self.__spot_price,
            self.__strike_price,
            new_vol,
            self.__converse_rate
            )
        del new_vol
        
        if self._price is None:
            self.compute_price()
        RC_vol.compute_price()
        
        vega = (self._price - RC_vol._price) / (0.01*self.__volatility.__volatility)
        
        return vega
        
        
    def compute_greeks(self) -> Dict[str, float]:        
        return {
            "delta": self.compute_delta(),
            "gamma": self.compute_gamma(),
            "theta": 0.0,
            "rho": self.compute_rho(),
            "vega": self.compute_vega(),
        }



class OutperformerCertificate(StructuredProductBase):
    
    def __init__(
        self,
        rate: Rate,
        maturity: Maturity,
        nominal: int,
        spot_price: float,
        strike_price1: float,
        strike_price2: float,
        volatility: Volatility,
        n_call: float,
    ) -> None:
        super().__init__("outperformer-certificate")
        self.__rate = rate
        self.__maturity = maturity
        self.__nominal = nominal
        self.__spot_price = spot_price
        self.__strike_price1 = strike_price1
        self.__strike_price2 = strike_price2
        self.__volatility = volatility
        self.__n_call = n_call
        
        
    def compute_price(self) -> float:
        mat = Maturity(maturity_in_years=1)
        bond = ZeroCouponBond(
            self.__rate, 
            self.__maturity, 
            self.__nominal
            )
        option_call1 = BinaryOption(
            self.__spot_price, 
            self.__strike_price1, 
            mat, 
            self.__rate, 
            self.__volatility,
            "call"
            )
        option_call2 = BinaryOption(
            self.__spot_price, 
            self.__strike_price2, 
            mat, 
            self.__rate, 
            self.__volatility,
            "call"
            )
        option_put = BinaryOption(
            self.__spot_price, 
            self.__strike_price1, 
            mat, 
            self.__rate, 
            self.__volatility,
            "put"
            )
        self._price = bond.compute_price() \
                    + self.__n_call * option_call1.compute_price() \
                    - self.__n_call * option_call2.compute_price() \
                    - option_put.compute_price()
        return self._price
    
    
    def compute_delta(self) -> float:
        
        OC_spot = OutperformerCertificate(
            self.__rate,
            self.__maturity,
            self.__nominal,
            self.__spot_price * (1-0.01),
            self.__strike_price1,
            self.__strike_price2,
            self.__volatility,
            self.__n_call
            )
        
        if self._price is None:
            self.compute_price()
            
        OC_spot.compute_price()
        delta = (self._price - OC_spot._price) / (self.__spot_price*0.01)
        
        return delta
    
    def compute_gamma(self) -> float:
        
        OC_spot = OutperformerCertificate(
            self.__rate,
            self.__maturity,
            self.__nominal,
            self.__spot_price * (1-0.01),
            self.__strike_price1,
            self.__strike_price2,
            self.__volatility,
            self.__n_call
            )
        
        delta1 = self.compute_delta()
        delta2 = OC_spot.compute_delta()
        
        gamma = (delta1-delta2) / (self.__spot_price*0.01)
        
        return gamma
        
    def compute_rho(self) -> float:
        new_rate = Rate(
            self.__rate.__rate * (1-0.01),
            self.__rate.__rate_type,
            self.__rate.__interpolation_type
            )
        OC_rate = OutperformerCertificate(
            new_rate,
            self.__maturity,
            self.__nominal,
            self.__spot_price * (1-0.01),
            self.__strike_price1,
            self.__strike_price2,
            self.__volatility,
            self.__n_call
            )
        del new_rate
        
        if self._price is None:
            self.compute_price()
        OC_rate.compute_price()
        
        rho = (self._price - OC_rate._price) / (0.01*self.__rate.__rate)
        
        return rho
    
    def compute_vega(self) -> float:
        new_vol = Volatility(
            self.__volatility.__volatility * (1-0.01),
            self.__volatility.__interpol_type
            )
        OC_vol = OutperformerCertificate(
            self.__rate,
            self.__maturity,
            self.__nominal,
            self.__spot_price,
            self.__strike_price1,
            self.__strike_price2,
            new_vol,
            self.__n_call
            )
        del new_vol
        
        if self._price is None:
            self.compute_price()
        OC_vol.compute_price()
        
        vega = (self._price - OC_vol._price) / (0.01*self.__volatility.__volatility)
        
        return vega

    def compute_greeks(self) -> Dict[str, float]:
        return {
            "delta": self.compute_delta(),
            "gamma": self.compute_gamma(),
            "theta": 0.0,
            "rho": self.compute_rho(),
            "vega": self.compute_vega(),
        }