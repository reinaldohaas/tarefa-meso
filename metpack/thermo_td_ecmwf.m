 function [theta, thetae, q, qsat, qsati] = thermo_td_ecmwf(t,p,td)
% thermo_td_ecmwf generates thermodynamic variables from t(oC) p(mb) td(oC)
% the modification for ec data is because their td at 2m field is
% t_dewpoint if t>0 and t_frostpoint if t<0 !! Bizarre I know - 4 Nov. 99
% output [theta, thetae, q, qsat, qsati], in K, K, g/kg, g/kg, g/kg
%
% Realised thetae calculation is incorrect (17 Nov 2009)
% Changed to used formulae of Bolton (1980), for pseudo-equivalent p.t.


%convert t,p,td to SI units
 tk = t + 273.15; %K
 p = p*100; %Pa
 tdk = t +273.15; %K

%calculate the potential temperature from temperature array
 p0=1000*100;	%reference pressure Pa
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
%saturation vapour pressure wrt to water and ice (mb)
 [es esi] = thermo_es(t);   			
 es = es*100; esi = esi*100; %Pa
 rsat = eps*es./p;		 	%saturation mixing ratio
 rsati = eps*esi./p;		 	%sat mixing ration wrt ice
 qsat = rsat./(rsat+1);				%sat specific humidity
 qsati = rsati./(rsati+1);			%sat specific humidity wrt ice
 %thetae = theta.*exp((Lv.*rsat)./(cp.*tk));	%equivalent potential temp.
 % Wrong
 

%calculate  r= mass water vapour/mass dry air &
% q= mass water vapour/mass moist air
 [e ei] = thermo_es(td); %e in mb
 e = e*100; ei= ei*100;  %in Pa
% r = (eps*e)./(p-e); 
 
%ecmwf q_new
for i=1:length(t) 
 if (t(i) < 0) 
  q_new(i) = (eps*ei(i))./p(i);
 else 
  q_new(i) = (eps*e(i))./p(i);
 end;
end;

 q = q_new';
 
%convert to g /kg
 r = r*1e3;
 q = q*1e3;
 qsat = qsat*1e3; 
 qsati = qsati*1e3; 

% calculate pseudo-equivalent potential temperature, from Bolton, Mon Wea Rev, 1980
% r = is g/kg
% Firstly calculate Temp at LCL, note e must be in mb.
Tlcl = 2840./(3.5*log(tk)-log(e/100)-4.805) + 55;                 % eqn 21, Bolton
thetae = theta.*exp(((3.376./Tlcl)-0.00254).*r.*(1+0.81*r*1e-3));   % eqn 38, Bolton
