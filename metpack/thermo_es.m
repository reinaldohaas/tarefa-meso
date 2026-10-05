 function [esw, esi] = thermo_es(t)
% use [esw, esi] = thermo_es(t)
 % thermo_es calculates saturation vapour pressures (mb) wrt water and ice
% from t(oC) from the polynomial approximation of Lowe (see Sargent 1980)
% [esw, esi] = thermo_es(t)

lowe_coef_ice = [6.109177956 5.03469897e-1 1.886013408e-2 4.176223716e-4...
		5.824720280e-6 4.838803174e-8 1.838826904e-10];

lowe_coef_water = [6.107799961 4.436518521e-1 1.428945805e-2 2.650648471e-4...
		3.031240396e-6 2.034080948e-8 6.136820929e-11];

%reverse order of coefficients
pesi = lowe_coef_ice(length(lowe_coef_ice):-1:1);
pesw= lowe_coef_water(length(lowe_coef_water):-1:1);

%evaluate polynomials for t in deg C
esi = polyval(pesi,t);
esw = polyval(pesw,t);
