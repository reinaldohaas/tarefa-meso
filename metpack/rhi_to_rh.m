 function [rh] = rhi_to_rh(rhi,t,p)
% rhi_to_rh converts rh wrt ice to rh, (%) 
% given rhi (%), t (oC), and p (mb)
% [rh] = rhi_to_rh(rhi,t,p)

%convert to SI units
 tk = t + 273.15; %K
 p = p*100; %Pa

%calculate saturated specific humidities
 eps = 0.622; 	%Rd/Rv
 [es esi] = thermo_es(t);  	 	%es and es_wrt_ice in mb
 es = es*100; esi = esi*100;    	% convert to Pa
 rsat = eps*es./p;		 	%saturation mixing ratio
 rsati = eps*esi./p;		 	%sat mixing ration wrt ice
 qsat = rsat./(rsat+1);			%sat specific humidity
 qsati = rsati./(rsati+1);		%sat specific humidity wrt ice

%calculate vapour pressure
 e = (rhi/100).*esi;

%calculate RH
 rh = (e./es)*100;
