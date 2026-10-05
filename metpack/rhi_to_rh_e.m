 function [rh, e] = rhi_to_rh_e(rhi,t,p)
% rhi_to_rh_e converts rh wrt ice to rh (%) and e (mb) 
% given rhi (%), t (oC), and p (mb)
% [rh, e] = rhi_to_rh(rhi,t,p)

%convert to SI units
 tk = t + 273.15; %K
 p = p*100; %Pa

%calculate saturated specific humidities
 eps = 0.622; 	%Rd/Rv
 [es esi] = thermo_es(t);  	 	%es and es_wrt_ice in mb
 es = es*100; esi = esi*100;    	%convert to Pa
 rsat = eps*es./p;		 	%saturation mixing ratio
 rsati = eps*esi./p;		 	%sat mixing ration wrt ice
 qsat = rsat./(rsat+1);			%sat specific humidity
 qsati = rsati./(rsati+1);		%sat specific humidity wrt ice

 e = (rhi/100).*esi;			%calculate vapour pressure (Pa)
 rh = (e./es)*100;			%calculate RH (%)

 e = e*1e-2;				%vapour pressure (mb)

