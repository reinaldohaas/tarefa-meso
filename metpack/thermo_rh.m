function [theta, thetae, q, qsat, qsati] = thermo_rh(t,p,rh)
% thermo_rh generates thermodynamic variables from t(oC) p(mb) rh(%) vectors
% output [theta, thetae, q, qsat, qsati] = thermo_rh(t,p,rh)
% in K, K, g/kg, g/kg, g/kg

% changed rsat denominator from p to p-es (3 may 07)
%
% Realised thetae calculation is incorrect (17 Nov 2009)
% Changed to used formulae of Bolton (1980), for pseudo-equivalent p.t.

%convert t,p to SI units
tk = t + 273.15; %K
p = p*100; %Pa

%calculate the potential temperature from temperature array
p0=1000*100;	%reference pressure in Pa
R=287;		%gas constant
cp=1004;	%specific heat wrt pressure
K= R/cp;
a = ((p./p0).^(-K));
theta = tk.*a;

%calculate equivalent potential temperature 
Lv = 2.5e6; 	%latent heat of vapourisation
eps = 0.622; 	%Rd/Rv
es0 = 0.61e3;	%reference saturation vapour pressure Pa
tk0 = 273.15;	%reference temperature
[es esi] = thermo_es(t);   			%...wrt to water and ice 
es = es*100; esi = esi*100; 		%convert to Pa
rsat = eps*es./(p-es);		 	%saturation mixing ratio
rsati = eps*esi./(p-esi);		 	%sat mixing ratio wrt ice
qsat = rsat./(rsat+1);				%sat specific humidity
qsati = rsati./(rsati+1);			%sat specific humidity wrt ice
%thetae = theta.*exp((Lv.*rsat)./(cp.*tk));	%equivalent potential temp.
% this is incorrect - need to change. 
e = rh.*es/100;                              % vapour pressure (Pa)

% Calculate water vapour mixing ratio r and q specific humidity
 r = (eps*e)./(p-e); 
 q = r./(1+r);

% change units to g/kg
r = r*1e3;
q = q*1e3;
qsat = qsat*1e3;
qsati = qsati*1e3;

% calculate pseudo-equivalent potential temperature, from Bolton, Mon Wea Rev, 1980
% r = is g/kg
% Firstly calculate Temp at LCL, note e must be in mb.
Tlcl = 2840./(3.5*log(tk)-log(e/100)-4.805) + 55;                 % eqn 21, Bolton
thetae = theta.*exp(((3.376./Tlcl)-0.00254).*r.*(1+0.81*r*1e-3));   % eqn 38, Bolton








