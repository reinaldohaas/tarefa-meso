function [hydro_pressure] = hydro_pressure(z,t,pground)
% given z=height (m), t=temperature vectors (K), plus a ground pressure (mb)
% this function calculates the hydrostatic pressure (mb)
% function [hydro_pressure] = hydro_pressure(z,t,pground)

R = 287; 	% gas constant
g= 9.81; 	% m/s2
hydro_pressure = pground*exp(-g*z./(R*t)); 
