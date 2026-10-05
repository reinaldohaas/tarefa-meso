function [hydro_height] = hydro_height(p,t,pground)
%use [hydro_height] = hydro_height(p,t,pground)
% given pressure (mb), temp vectors (K), and scalar ground pressure
% calculates the hydrostatic height

R = 287; 	% gas constant
g= 9.81; 	%m/s2
hydro_height = -(R/g)*t.*log(([p]*100)./(pground*100)); %p must be in Pa
